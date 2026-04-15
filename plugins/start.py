import asyncio
import logging
import humanize
from datetime import datetime

from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait

from bot import Bot
from config import *
from helper_func import subscribed, encode, decode, get_messages

# -------------------------------
# DATABASE (MOTOR)
# -------------------------------
from database.database import (
    user_data,
    banned_users,
    telegram_files,
    is_admin
)

logging.basicConfig(level=logging.INFO)

# -------------------------------
# AUTO DELETE SETUP
# -------------------------------
AUTO_DELETE_ENABLED = True
file_auto_delete = humanize.naturaldelta(FILE_AUTO_DELETE)


# -------------------------------
# USER FUNCTIONS (MOTOR FIXED)
# -------------------------------
async def is_user_present(user_id: int) -> bool:
    return await user_data.find_one({"_id": user_id}) is not None


async def add_user(user_id: int, first_name: str, username: str):
    await user_data.update_one(
        {"_id": user_id},
        {"$set": {
            "_id": user_id,
            "first_name": first_name,
            "username": username,
            "joined_at": datetime.utcnow()
        }},
        upsert=True
    )


# -------------------------------
# BAN SYSTEM
# -------------------------------
async def is_user_banned(user_id: int) -> bool:
    data = await banned_users.find_one({"_id": user_id})
    return data.get("is_banned", False) if data else False


async def get_ban_reason(user_id: int) -> str:
    data = await banned_users.find_one({"_id": user_id})
    return data.get("reason", "No reason provided") if data else "No reason provided"


# -------------------------------
# MAINTENANCE CHECK (MOTOR FIXED)
# -------------------------------
async def is_maintenance(user_id: int) -> bool:
    data = await telegram_files.find_one({"maintenance": "on"})
    return bool(data and user_id != OWNER_ID)


# -------------------------------
# START COMMAND
# -------------------------------
@Bot.on_message(filters.command("start") & filters.private)
async def start_command(client: Client, message: Message):

    user_id = message.from_user.id
    text = message.text

    # ---------------- FORCE SUB ----------------
    if not await subscribed(client, message):
        buttons = [
            [
                InlineKeyboardButton("Join Channel", url=client.invitelink),
                InlineKeyboardButton("Join Channel", url=client.invitelink2)
            ],
            [
                InlineKeyboardButton("Join Channel", url=client.invitelink3),
                InlineKeyboardButton("Join Channel", url=client.invitelink4)
            ]
        ]

        return await message.reply_photo(
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

    # ---------------- BAN CHECK ----------------
    if await is_user_banned(user_id):
        reason = await get_ban_reason(user_id)
        return await message.reply_text(f"🚫 You are banned.\nReason: {reason}")

    # ---------------- ADD USER ----------------
    if not await is_user_present(user_id):
        try:
            await add_user(
                user_id,
                message.from_user.first_name,
                message.from_user.username
            )

            await client.send_message(
                LOG_CHANNEL_ID,
                f"New User: {message.from_user.mention} ({user_id})"
            )

        except Exception as e:
            logging.error(e)

    # ---------------- MAINTENANCE ----------------
    if await is_maintenance(user_id):
        return await message.reply_text("🛠 Maintenance mode ON")

    # ---------------- FILE SYSTEM ----------------
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

        temp = await message.reply_text("⏳ Processing...")

        messages = await get_messages(client, ids)

        await temp.delete()

        copied_msgs = []

        for msg in messages:
            caption = msg.caption.html if msg.caption else ""

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

        warn = await client.send_message(
            user_id,
            f"⚠️ Auto delete in {file_auto_delete}"
        )

        asyncio.create_task(delete_files(copied_msgs, client, warn, base64_string))
        return

    # ---------------- START MENU ----------------
    admin_status = await is_admin(user_id)

    buttons = [
        [
            InlineKeyboardButton("🧠 HELP", callback_data="help"),
            InlineKeyboardButton("🔰 ABOUT", callback_data="about")
        ]
    ]

    if admin_status:
        buttons.append([InlineKeyboardButton("⚙️ SETTINGS", callback_data="settings")])

    await message.reply_photo(
        photo=START_PIC,
        caption=START_MSG.format(
            first=message.from_user.first_name,
            last=message.from_user.last_name,
            username=message.from_user.username,
            mention=message.from_user.mention,
            id=user_id
        ),
        reply_markup=InlineKeyboardMarkup(buttons)
    )


# -------------------------------
# USERS COUNT
# -------------------------------
@Bot.on_message(filters.command("users") & filters.private)
async def total_users(client, message):
    if not await is_admin(message.from_user.id):
        return await message.reply_text("Admins only")

    total = await user_data.count_documents({})
    await message.reply_text(f"Total Users: {total}")


# -------------------------------
# BROADCAST
# -------------------------------
@Bot.on_message(filters.command("broadcast") & filters.private)
async def broadcast(client, message):

    if not await is_admin(message.from_user.id):
        return

    if not message.reply_to_message:
        return await message.reply_text("Reply to message")

    users = user_data.find()

    success, failed = 0, 0

    for user in users:
        try:
            await message.reply_to_message.copy(user["_id"])
            success += 1
            await asyncio.sleep(0.05)
        except:
            failed += 1

    await message.reply_text(f"Done\nSuccess:{success}\nFailed:{failed}")


# -------------------------------
# AUTO DELETE FUNCTION
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

    try:
        await main_message.edit_text("File deleted!")
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
    await message.reply_text("Auto delete ON")


@Client.on_message(filters.command("autodeleteoff") & filters.user(OWNER_ID))
async def disable_autodelete(client, message):
    set_auto_delete(False)
    await message.reply_text("Auto delete OFF")
