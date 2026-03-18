import os
import asyncio
import logging
import humanize
from pymongo import MongoClient
from datetime import datetime

from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait

from bot import Bot
from config import *
from helper_func import subscribed, encode, decode, get_messages
from database.database import is_admin

# -------------------------------
# Logging
# -------------------------------
logging.basicConfig(level=logging.INFO)

# -------------------------------
# Database setup
# -------------------------------
client_db = MongoClient(DB_URI)
db = client_db[DB_NAME]

user_data = db['users']
banned_users = db['banned_users']
telegram_files = db['TelegramFiles']

AUTO_DELETE_ENABLED = True
file_auto_delete = humanize.naturaldelta(FILE_AUTO_DELETE)

# -------------------------------
# User management
# -------------------------------
async def is_user_present(user_id: int) -> bool:
    return user_data.find_one({'_id': user_id}) is not None

async def add_user(user_id: int, first_name: str, username: str):
    user_data.update_one(
        {'_id': user_id},
        {'$set': {
            '_id': user_id,
            'first_name': first_name,
            'username': username,
            'joined_at': datetime.utcnow()
        }},
        upsert=True
    )

# -------------------------------
# Ban management
# -------------------------------
async def is_user_banned(user_id: int) -> bool:
    data = banned_users.find_one({'_id': user_id})
    return data.get("is_banned", False) if data else False

async def get_ban_reason(user_id: int) -> str:
    data = banned_users.find_one({'_id': user_id})
    return data.get('reason', 'No reason provided') if data else 'No reason provided'

# -------------------------------
# Maintenance check
# -------------------------------
async def is_maintenance(user_id: int) -> bool:
    data = telegram_files.find_one({"maintenance": "on"})
    return bool(data and user_id != OWNER_ID)

# -------------------------------
# START COMMAND (MAIN HANDLER)
# -------------------------------
@Bot.on_message(filters.command("start") & filters.private)
async def start_command(client: Client, message: Message):

    user_id = message.from_user.id
    text = message.text

    # -------------------------------
    # FORCE JOIN
    # -------------------------------
    if not await subscribed(client, message):
        buttons = [
            [InlineKeyboardButton("Join Channel", url=client.invitelink),
             InlineKeyboardButton("Join Channel", url=client.invitelink2)],
            [InlineKeyboardButton("Join Channel", url=client.invitelink3),
             InlineKeyboardButton("Join Channel", url=client.invitelink4)]
        ]

        await message.reply_photo(
            photo=FORCE_PIC,
            caption=FORCE_MSG.format(
                first=message.from_user.first_name,
                last=message.from_user.last_name,
                username=message.from_user.username,
                mention=message.from_user.mention,
                id=user_id
            ),
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        return

    # -------------------------------
    # BAN CHECK
    # -------------------------------
    if await is_user_banned(user_id):
        reason = await get_ban_reason(user_id)
        return await message.reply_text(f"🚫 You are banned.\nReason: {reason}")

    # -------------------------------
    # ADD USER
    # -------------------------------
    if not await is_user_present(user_id):
        try:
            await add_user(
                user_id,
                message.from_user.first_name,
                message.from_user.username
            )

            log_text = NEW_USER_TXT.format(
                message.from_user.mention,
                user_id,
                message.from_user.first_name or "Unknown"
            )

            await client.send_message(LOG_CHANNEL_ID, log_text)

        except Exception as e:
            logging.error(f"User add error: {e}")

    # -------------------------------
    # MAINTENANCE MODE
    # -------------------------------
    if await is_maintenance(user_id):
        return await message.reply_text(
            "🛠 Bot is under maintenance.\nPlease try again later."
        )

    # -------------------------------
    # FILE LINK SYSTEM
    # -------------------------------
    if len(text.split()) > 1:
        try:
            base64_string = text.split(" ", 1)[1]
            string = await decode(base64_string)
            argument = string.split("-")
        except:
            return

        ids = []
        try:
            if len(argument) == 3:
                start = int(int(argument[1]) / abs(client.db_channel.id))
                end = int(int(argument[2]) / abs(client.db_channel.id))
                ids = range(start, end + 1)
            elif len(argument) == 2:
                ids = [int(int(argument[1]) / abs(client.db_channel.id))]
        except:
            return

        temp = await message.reply_text("⏳ Please wait...")

        try:
            messages = await get_messages(client, ids)
        except:
            await message.reply_text("❌ Error retrieving file.")
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

            try:
                copied = await msg.copy(
                    chat_id=user_id,
                    caption=caption,
                    parse_mode=ParseMode.HTML,
                    protect_content=PROTECT_CONTENT
                )
                copied_msgs.append(copied)

            except FloodWait as e:
                await asyncio.sleep(e.value)
                copied = await msg.copy(chat_id=user_id)
                copied_msgs.append(copied)

        warn_msg = await client.send_message(
            chat_id=user_id,
            text=f"⚠️ This file will be deleted in {file_auto_delete}.\nPlease forward it to save."
        )

        asyncio.create_task(delete_files(copied_msgs, client, warn_msg, base64_string))
        return

    # -------------------------------
    # START MENU
    # -------------------------------
    admin_status = await is_admin(user_id)

    buttons = [
        [InlineKeyboardButton("🧠 HELP", callback_data="help"),
         InlineKeyboardButton("🔰 ABOUT", callback_data="about")]
    ]

    if admin_status:
        buttons.append([InlineKeyboardButton("⚙️ SETTINGS", callback_data="settings")])

    await message.reply_photo(
        photo=START_PIC,
        caption=START_MSG.format(
            first=message.from_user.first_name,
            last=message.from_user.last_name,
            username=f"@{message.from_user.username}" if message.from_user.username else "None",
            mention=message.from_user.mention,
            id=user_id
        ),
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# -------------------------------
# USERS COMMAND
# -------------------------------
@Bot.on_message(filters.command("users") & filters.private)
async def total_users(client, message):
    if not await is_admin(message.from_user.id):
        return await message.reply_text("⚠️ Admins only!")

    total = user_data.count_documents({})
    await message.reply_text(f"👥 Total Users: {total}")

# -------------------------------
# BROADCAST
# -------------------------------
@Bot.on_message(filters.command("broadcast") & filters.private)
async def broadcast_handler(client, message):

    if not await is_admin(message.from_user.id):
        return await message.reply_text("⚠️ Admins only!")

    if not message.reply_to_message:
        return await message.reply_text("Reply to a message to broadcast.")

    users = user_data.find()
    success, failed = 0, 0

    status = await message.reply_text("📢 Broadcasting...")

    for user in users:
        try:
            await message.reply_to_message.copy(user['_id'])
            success += 1
            await asyncio.sleep(0.1)
        except:
            failed += 1

    await status.edit_text(
        f"📢 Done\n✅ Success: {success}\n❌ Failed: {failed}"
    )

# -------------------------------
# FILE AUTO DELETE
# -------------------------------
async def delete_files(messages, client, main_message, payload=None):

    if not AUTO_DELETE_ENABLED:
        return

    await asyncio.sleep(FILE_AUTO_DELETE)

    for msg in messages:
        try:
            await client.delete_messages(msg.chat.id, msg.id)
        except:
            pass

    keyboard = None
    if payload:
        me = await client.get_me()
        keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton("Get File Again", url=f"https://t.me/{me.username}?start={payload}")]]
        )

    try:
        await main_message.edit_text(
            "✅ File deleted!\nClick below to get again.",
            reply_markup=keyboard
        )
    except:
        pass

# -------------------------------
# AUTO DELETE TOGGLE
# -------------------------------
def set_auto_delete(state: bool):
    global AUTO_DELETE_ENABLED
    AUTO_DELETE_ENABLED = state

@Client.on_message(filters.command("autodeleteon") & filters.user(OWNER_ID))
async def enable_autodelete(client, message):
    set_auto_delete(True)
    await message.reply_text("✅ Auto delete enabled")

@Client.on_message(filters.command("autodeleteoff") & filters.user(OWNER_ID))
async def disable_autodelete(client, message):
    set_auto_delete(False)
    await message.reply_text("❌ Auto delete disabled")
