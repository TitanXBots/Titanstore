import os
import asyncio
import humanize
import logging
from pymongo import MongoClient
from datetime import datetime

from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait

from Script import *
from bot import Bot
from config import *
from helper_func import subscribed, encode, decode, get_messages
from database import database  # full database.py module

# -------------------------------
# Database setup
# -------------------------------
client_db = MongoClient(DB_URI)
db = client_db[DB_NAME]
telegram_files = db['TelegramFiles']

AUTO_DELETE_ENABLED = True
file_auto_delete = humanize.naturaldelta(FILE_AUTO_DELETE)

# -------------------------------
# START COMMAND
# -------------------------------
@Bot.on_message(filters.command("start") & filters.private & subscribed)
async def start_command(client: Client, message: Message):
    user_id = message.from_user.id
    text = message.text

    # Ban check
    if await database.is_banned(user_id):
        reason = await database.get_ban_reason(user_id)
        await message.reply_text(f"🚫 You are banned.\nReason: {reason}")
        return

    # Add user
    if not await database.present_user(user_id):
        try:
            await database.add_user(user_id, message.from_user.first_name, message.from_user.username)
            log_text = NEW_USER_TXT.format(
                message.from_user.mention,
                user_id,
                message.from_user.first_name or "Unknown"
            )
            await client.send_message(LOG_CHANNEL_ID, log_text)
        except Exception as e:
            print(f"User add error: {e}")

    # Maintenance mode
    if telegram_files.find_one({"maintenance": "on"}) and user_id != OWNER_ID:
        await message.reply_text("⚙️ Bot is under maintenance. Please try later.")
        return

    # Admin status
    admin_status = await database.is_admin(user_id)

    # File payload
    if len(text.split()) > 1:
        try:
            base64_string = text.split(" ", 1)[1]
            string = await decode(base64_string)
            argument = string.split("-")
        except:
            return

        ids = []
        if len(argument) == 3:
            try:
                start = int(int(argument[1]) / abs(client.db_channel.id))
                end = int(int(argument[2]) / abs(client.db_channel.id))
                ids = range(start, end + 1) if start <= end else range(start, end - 1, -1)
            except:
                return
        elif len(argument) == 2:
            try:
                ids = [int(int(argument[1]) / abs(client.db_channel.id))]
            except:
                return

        temp = await message.reply("Please wait...")
        try:
            messages = await get_messages(client, ids)
        except:
            await message.reply_text("Error retrieving file.")
            return
        await temp.delete()

        copied_msgs = []
        for msg in messages:
            caption = ""
            if CUSTOM_CAPTION and msg.document:
                caption = CUSTOM_CAPTION.format(
                    previouscaption="" if not msg.caption else msg.caption.html,
                    filename=msg.document.file_name
                )
            elif msg.caption:
                caption = msg.caption.html

            reply_markup = None if not DISABLE_CHANNEL_BUTTON else msg.reply_markup

            try:
                copied = await msg.copy(
                    chat_id=user_id,
                    caption=caption,
                    parse_mode=ParseMode.HTML,
                    reply_markup=reply_markup,
                    protect_content=PROTECT_CONTENT
                )
                copied_msgs.append(copied)
            except FloodWait as e:
                await asyncio.sleep(e.value)
                copied = await msg.copy(
                    chat_id=user_id,
                    caption=caption,
                    parse_mode=ParseMode.HTML,
                    reply_markup=reply_markup,
                    protect_content=PROTECT_CONTENT
                )
                copied_msgs.append(copied)

        warn_msg = await client.send_message(
            chat_id=user_id,
            text=f"<b>IMPORTANT</b>\n\nThis file will be deleted in {file_auto_delete}.\nForward it somewhere to save."
        )

        asyncio.create_task(delete_files(copied_msgs, client, warn_msg, base64_string))
        return

    # Start menu
    buttons = [
        [InlineKeyboardButton("🧠 HELP", callback_data="help"),
         InlineKeyboardButton("📗 ABOUT", callback_data="about")]
    ]
    if admin_status:
        buttons.append([InlineKeyboardButton("⚙️ SETTINGS", callback_data="settings")])

    reply_markup = InlineKeyboardMarkup(buttons)
    await message.reply_photo(
        photo=START_PIC,
        caption=START_MSG.format(
            first=message.from_user.first_name,
            last=message.from_user.last_name or "",
            username=f"@{message.from_user.username}" if message.from_user.username else "None",
            mention=message.from_user.mention,
            id=user_id
        ),
        reply_markup=reply_markup
    )

# -------------------------------
# Force join
# -------------------------------
@Bot.on_message(filters.command("start") & filters.private)
async def not_joined(client: Client, message: Message):
    buttons = [
        [InlineKeyboardButton("Join Channel", url=client.invitelink),
         InlineKeyboardButton("Join Channel", url=client.invitelink2)],
        [InlineKeyboardButton("Join Channel", url=client.invitelink3),
         InlineKeyboardButton("Join Channel", url=client.invitelink4)]
    ]
    try:
        buttons.append([InlineKeyboardButton(
            "Click Here",
            url=f"https://t.me/{client.username}?start={message.command[1]}"
        )])
    except:
        pass

    await message.reply_photo(
        photo=FORCE_PIC,
        caption=FORCE_MSG.format(
            first=message.from_user.first_name,
            last=message.from_user.last_name,
            username=f"@{message.from_user.username}" if message.from_user.username else "None",
            mention=message.from_user.mention,
            id=message.from_user.id
        ),
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# -------------------------------
# File auto delete
# -------------------------------
async def delete_files(messages, client, k, command_payload=None):
    global AUTO_DELETE_ENABLED
    if not AUTO_DELETE_ENABLED:
        return

    await asyncio.sleep(FILE_AUTO_DELETE)
    for msg in messages:
        try:
            await client.delete_messages(msg.chat.id, msg.id)
        except Exception as e:
            logging.error(e)

    keyboard = None
    if command_payload:
        me = await client.get_me()
        keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton("Get File Again", url=f"https://t.me/{me.username}?start={command_payload}")]]
        )

    try:
        await k.edit_text("Your file has been deleted.\n\nClick below to get it again.", reply_markup=keyboard)
    except:
        pass

# -------------------------------
# Auto delete toggle (owner only)
# -------------------------------
def set_auto_delete(state: bool):
    global AUTO_DELETE_ENABLED
    AUTO_DELETE_ENABLED = state
    return AUTO_DELETE_ENABLED

@Client.on_message(filters.command("autodeleteon") & filters.user(OWNER_ID))
async def enable_autodelete(client, message):
    set_auto_delete(True)
    await message.reply_text("✅ Auto Delete Enabled")

@Client.on_message(filters.command("autodeleteoff") & filters.user(OWNER_ID))
async def disable_autodelete(client, message):
    set_auto_delete(False)
    await message.reply_text("❌ Auto Delete Disabled")
