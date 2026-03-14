# start.py
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
from database.database import *
# -------------------------------
# Database setup
# -------------------------------
client_db = MongoClient(DB_URI)
db = client_db[DB_NAME]

user_data = db['users']
banned_users = db['banned_users']
telegram_files = db['TelegramFiles']
admins_collection = db['admins']

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
    return banned_users.find_one({'_id': user_id}) is not None


async def get_ban_reason(user_id: int) -> str:
    data = banned_users.find_one({'_id': user_id})
    return data.get('reason', 'No reason provided') if data else 'No reason provided'

# -------------------------------
# Owner/Admin check
# -------------------------------
async def is_owner(user_id: int) -> bool:
    return user_id == OWNER_ID


async def is_admin(user_id: int) -> bool:
    return user_id == OWNER_ID or admins_collection.find_one({"_id": user_id}) is not None

# -------------------------------
# Maintenance check
# -------------------------------
async def is_maintenance(user_id: int) -> bool:
    data = telegram_files.find_one({"maintenance": "on"})
    if data and user_id != OWNER_ID:
        return True
    return False

# -------------------------------
# START COMMAND
# -------------------------------
@Bot.on_message(filters.command("start") & filters.private & subscribed)
async def start_command(client: Client, message: Message):

    user_id = message.from_user.id
    text = message.text

    # Ban check
    if await is_user_banned(user_id):
        reason = await get_ban_reason(user_id)
        await message.reply_text(f"🚫 You are banned from using this bot.\n\nReason: {reason}")
        return

    # Add user
    if not await is_user_present(user_id):
        try:
            await add_user(user_id, message.from_user.first_name, message.from_user.username)

            log_text = NEW_USER_TXT.format(
                message.from_user.mention,
                user_id,
                message.from_user.first_name or "Unknown"
            )

            await client.send_message(LOG_CHANNEL_ID, log_text)

        except Exception as e:
            print(f"User add error: {e}")

    # Maintenance mode
    if await is_maintenance(user_id):
        await message.reply_text("⚙️ Bot is under maintenance.\nPlease try again later.")
        return

    # Admin check
    admin_status = await is_admin(user_id)

    # -------------------------------
    # File link payload
    # -------------------------------
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
                ids = range(start, end + 1)
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
            text=f"<b>IMPORTANT</b>\n\nThis file will be deleted in {file_auto_delete}.\n\nForward it somewhere to save."
        )

        asyncio.create_task(delete_files(copied_msgs, client, warn_msg, base64_string))
        return

    # -------------------------------
    # Start menu
    # -------------------------------
    # Check admin status
    admin_status = await is_admin(user_id)
    buttons = [
        [
            InlineKeyboardButton("🧠 HELP", callback_data="help"),
            InlineKeyboardButton("📗 ABOUT", callback_data="about")
        ]
    ]

    if admin_status:
        buttons.append(
            [InlineKeyboardButton("⚙️ SETTINGS", callback_data="settings")]
        )

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
# Force join (your code)
# -------------------------------
@Bot.on_message(filters.command('start') & filters.private)
async def not_joined(client: Client, message: Message):

    buttons = [
        [
            InlineKeyboardButton(text="ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ", url=client.invitelink),
            InlineKeyboardButton(text="ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ", url=client.invitelink2),
        ],
        [
            InlineKeyboardButton(text="ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ", url=client.invitelink3),
            InlineKeyboardButton(text="ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ", url=client.invitelink4),
        ]
    ]

    try:
        buttons.append(
            [
                InlineKeyboardButton(
                    text='☢ ɴᴏᴡ ᴄʟɪᴄᴋ ʜᴇʀᴇ •',
                    url=f"https://t.me/{client.username}?start={message.command[1]}"
                )
            ]
        )
    except IndexError:
        pass

    await message.reply_photo(
        photo=FORCE_PIC,
        caption=FORCE_MSG.format(
            first=message.from_user.first_name,
            last=message.from_user.last_name,
            username=None if not message.from_user.username else '@' + message.from_user.username,
            mention=message.from_user.mention,
            id=message.from_user.id
        ),
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# -------------------------------
# Users command
# -------------------------------
@Bot.on_message(filters.command("users") & filters.private)
async def total_users(client, message):

    if not await is_admin(message.from_user.id):
        await message.reply_text("⚠️ Only admins allowed.")
        return

    total = user_data.count_documents({})
    await message.reply_text(f"👥 Total Users: {total}")

# -------------------------------
# Broadcast command
# -------------------------------
@Bot.on_message(filters.command("broadcast") & filters.private)
async def broadcast_handler(client, message):

    if not await is_admin(message.from_user.id):
        await message.reply_text("⚠️ Only admins allowed.")
        return

    if not message.reply_to_message:
        await message.reply_text("Reply to a message to broadcast.")
        return

    users = user_data.find()

    success = 0
    failed = 0

    msg = await message.reply_text("📢 Broadcast started...")

    for user in users:

        try:
            await message.reply_to_message.copy(user['_id'])
            success += 1
            await asyncio.sleep(0.1)

        except:
            failed += 1

    await msg.edit_text(
        f"📢 Broadcast Completed\n\n"
        f"✅ Success: {success}\n"
        f"❌ Failed: {failed}"
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
        except:
            pass

    try:
        await k.edit_text("Your file has been deleted.")
    except:
        pass

# -------------------------------
# Auto delete toggle
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
