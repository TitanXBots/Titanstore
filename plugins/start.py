import asyncio
import logging
from datetime import datetime

from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message

from bot import Bot
from config import *
from helper_func import subscribed, encode, decode, get_messages
from database.database import (
    add_user,
    is_user,
    is_banned,
    get_ban_reason,
    is_admin,
    is_maintenance,
    get_file
)

AUTO_DELETE_ENABLED = True
file_auto_delete = FILE_AUTO_DELETE


# ---------------- START COMMAND ----------------
@Bot.on_message(filters.command("start") & filters.private)
async def start_command(client: Client, message: Message):

    user_id = message.from_user.id
    text = message.text

    # ---------------- FORCE SUB ----------------
    if not await subscribed(client, user_id):

        buttons = [
            [
                InlineKeyboardButton("Join Channel 1", url=client.invitelink),
                InlineKeyboardButton("Join Channel 2", url=client.invitelink2)
            ],
            [
                InlineKeyboardButton("Join Channel 3", url=client.invitelink3),
                InlineKeyboardButton("Join Channel 4", url=client.invitelink4)
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
    if await is_banned(user_id):
        reason = await get_ban_reason(user_id)
        return await message.reply_text(f"🚫 You are banned.\nReason: {reason}")

    # ---------------- MAINTENANCE ----------------
    if await is_maintenance() and user_id != OWNER_ID:
        return await message.reply_text("🛠 Bot under maintenance")

    # ---------------- ADD USER ----------------
    if not await is_user(user_id):
        await add_user(
            user_id,
            message.from_user.first_name,
            message.from_user.username
        )

        try:
            await client.send_message(
                LOG_CHANNEL_ID,
                f"New User: {message.from_user.mention} ({user_id})"
            )
        except:
            pass

    # ---------------- FILE SYSTEM (SAFE UUID BASED) ----------------
    if len(text.split()) > 1:

        try:
            payload = text.split(" ", 1)[1]
            decoded = await decode(payload)
            args = decoded.split("-")
        except:
            return

        try:
            # SINGLE FILE
            if len(args) == 2:

                file_doc = await get_file(args[1])
                if not file_doc:
                    return await message.reply_text("Invalid file link")

                msg_id = file_doc["message_id"]
                ids = [msg_id]

            else:
                return

        except:
            return

        temp = await message.reply_text("⏳ Processing...")

        messages = await get_messages(client, ids)

        await temp.delete()

        copied_msgs = []

        for msg in messages:
            try:
                copied = await msg.copy(
                    chat_id=user_id,
                    protect_content=PROTECT_CONTENT
                )
                copied_msgs.append(copied)

            except Exception:
                continue

        warn = await client.send_message(
            chat_id=user_id,
            text=(
                f"⚠️ <b>Important Notice</b>\n\n"
                f"This file will be auto deleted in <b>{file_auto_delete}s</b>.\n"
                f"Forward it to save permanently."
            ),
            parse_mode=ParseMode.HTML
        )

        asyncio.create_task(delete_files(copied_msgs, client, warn, payload))
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
        buttons.append([
            InlineKeyboardButton("⚙️ SETTINGS", callback_data="settings")
        ])

    await message.reply_photo(
        photo=START_PIC,
        caption=START_MSG.format(first=message.from_user.first_name),
        reply_markup=InlineKeyboardMarkup(buttons)
    )


# ---------------- AUTO DELETE FUNCTION ----------------
async def delete_files(messages, client, main_message, payload):

    if not AUTO_DELETE_ENABLED:
        return

    await asyncio.sleep(file_auto_delete)

    for msg in messages:
        try:
            await client.delete_messages(msg.chat.id, msg.id)
        except:
            pass

    try:
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "♻️ Get Again",
                    url=f"https://t.me/{client.username}?start={payload}"
                )
            ]
        ])

        await main_message.edit_text(
            "✅ File deleted. Click below to get again.",
            reply_markup=keyboard
        )

    except:
        pass


# ---------------- AUTO DELETE TOGGLE ----------------
def set_auto_delete(state: bool):
    global AUTO_DELETE_ENABLED
    AUTO_DELETE_ENABLED = state


@Client.on_message(filters.command("autodeleteon") & filters.user(OWNER_ID))
async def on_autodelete(client, message):
    set_auto_delete(True)
    await message.reply_text("Auto delete ON")


@Client.on_message(filters.command("autodeleteoff") & filters.user(OWNER_ID))
async def off_autodelete(client, message):
    set_auto_delete(False)
    await message.reply_text("Auto delete OFF")
