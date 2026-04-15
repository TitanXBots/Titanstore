import asyncio
import logging
import humanize

from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait

from bot import Bot
from config import *
from helper_fun import subscribed, encode, decode, get_messages

from database.database import (
    user_data,
    is_user_present,
    add_user,
    is_user_banned,
    get_ban_reason,
    is_maintenance,
    is_admin
)

logging.basicConfig(level=logging.INFO)

# -------------------------------
# AUTO DELETE SYSTEM
# -------------------------------
AUTO_DELETE_ENABLED = True
file_auto_delete = humanize.naturaldelta(FILE_AUTO_DELETE)


def set_auto_delete(state: bool):
    global AUTO_DELETE_ENABLED
    AUTO_DELETE_ENABLED = state


# -------------------------------
# FORCE JOIN CHECK (HANDLED BY helper_fun subscribed)
# -------------------------------
# (No change needed here, already handled in helper_fun.py)


# -------------------------------
# START COMMAND
# -------------------------------
@Bot.on_message(filters.command("start") & filters.private)
async def start_command(client: Client, message: Message):

    user_id = message.from_user.id
    text = message.text or ""

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
                NEW_USER_TXT.format(
                    message.from_user.mention,
                    user_id,
                    message.from_user.first_name or "Unknown"
                )
            )

        except Exception as e:
            logging.error(f"User add error: {e}")

    # ---------------- MAINTENANCE ----------------
    if await is_maintenance(user_id):
        return await message.reply_text(
            "🛠 Bot is under maintenance.\nPlease try again later."
        )

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

        temp = await message.reply_text("⏳ Please wait...")

        try:
            messages = await get_messages(client, ids)
        except:
            return await message.reply_text("❌ Error retrieving file.")

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

        # ---------------- AUTO DELETE MESSAGE ----------------
        warn_msg = await client.send_message(
            user_id,
            f"⚠️ File will be deleted in {file_auto_delete}"
        )

        asyncio.create_task(delete_files(copied_msgs, client, warn_msg, text.split(" ", 1)[1]))


    # ---------------- START MENU ----------------
    admin_status = await is_admin(user_id)

    buttons = [
        [
            InlineKeyboardButton("🧠 HELP", callback_data="help"),
            InlineKeyboardButton("🔰 ABOUT", callback_data="about")
        ]
    ]

    if admin_status:
        buttons.append([
            InlineKeyboardButton("⚙️ SETTINGS", callback_data="settings")
        ])

    return await message.reply_photo(
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


# ---------------- AUTO DELETE FUNCTION ----------------
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
        await main_message.edit_text("✅ File deleted!")
    except:
        pass


# ---------------- AUTO DELETE ON ----------------
@Client.on_message(filters.command("autodeleteon") & filters.user(OWNER_ID))
async def autodelete_on(client, message):
    set_auto_delete(True)
    await message.reply_text("✅ Auto Delete Enabled")


# ---------------- AUTO DELETE OFF ----------------
@Client.on_message(filters.command("autodeleteoff") & filters.user(OWNER_ID))
async def autodelete_off(client, message):
    set_auto_delete(False)
    await message.reply_text("❌ Auto Delete Disabled")


# ---------------- USERS COUNT ----------------
@Bot.on_message(filters.command("users") & filters.private)
async def total_users(client, message):
    if not await is_admin(message.from_user.id):
        return await message.reply_text("⚠️ Admins only!")

    total = await user_data.count_documents({})
    await message.reply_text(f"👥 Total Users: {total}")


# ---------------- BROADCAST ----------------
@Bot.on_message(filters.command("broadcast") & filters.private)
async def broadcast_handler(client, message):

    if not await is_admin(message.from_user.id):
        return await message.reply_text("⚠️ Admins only!")

    if not message.reply_to_message:
        return await message.reply_text("Reply to a message to broadcast.")

    users = await user_data.find({}).to_list(length=None)

    success, failed = 0, 0

    status = await message.reply_text("📢 Broadcasting...")

    for user in users:
        try:
            await message.reply_to_message.copy(user["_id"])
            success += 1
            await asyncio.sleep(0.05)
        except:
            failed += 1

    await status.edit_text(
        f"📢 Done\n\n✅ Success: {success}\n❌ Failed: {failed}"
    )
