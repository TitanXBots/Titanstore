# start.py
import os
import asyncio
import humanize
import logging
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait
from Script import NEW_USER_TXT
from bot import Bot
from config import *
from helper_func import subscribed, encode, decode, get_messages
from database.database import (
    add_user, del_user, full_userbase, present_user,
    banned_users_list, ban_user, unban_user, is_banned, get_ban_reason,
    is_admin
)
from pymongo import MongoClient

# -------------------------------
# Database setup
# -------------------------------
client_db = MongoClient(DB_URI)
db = client_db[DB_NAME]
collection = db["TelegramFiles"]

AUTO_DELETE_ENABLED = True  # default state
file_auto_delete = humanize.naturaldelta(FILE_AUTO_DELETE)

# -------------------------------
# Maintenance check
# -------------------------------
async def is_maintenance(client, user_id: int) -> bool:
    check_msg = collection.find_one({"maintenance": "on"})
    if check_msg and user_id not in ADMINS:
        return True
    return False

# -------------------------------
# START COMMAND
# -------------------------------
@Bot.on_message(filters.command('start') & filters.private & subscribed)
async def start_command(client: Client, message: Message):
    user_id = message.from_user.id

    # 🚫 Ban check
    if is_banned(user_id):
        reason = get_ban_reason(user_id)
        await message.reply_text(
            f"🚫 You are banned from using this bot.\n\n**Reason:** {reason}"
        )
        return

    # ✅ Add new user
    if not present_user(user_id):
        try:
            add_user(user_id)
            user_name = message.from_user.first_name or "Unknown"
            message_text = NEW_USER_TXT.format(message.from_user.mention, user_id, user_name)
            await client.send_message(LOG_CHANNEL_ID, message_text)
        except Exception as e:
            print(f"Error adding user: {e}")
            pass

    # ⚙️ Maintenance mode
    if await is_maintenance(client, user_id):
        await message.reply_text("⚙️ Maintenance mode is currently active. Please try again later.")
        return

    # Admin check
    admin_status = is_admin(user_id)

    # Check if start command has payload (file forwarding)
    text = message.text
    if len(text) > 7:
        try:
            base64_string = text.split(" ", 1)[1]
            string = await decode(base64_string)
            argument = string.split("-")
        except:
            return

        # Calculate message IDs to forward
        if len(argument) == 3:
            try:
                start = int(int(argument[1]) / abs(client.db_channel.id))
                end = int(int(argument[2]) / abs(client.db_channel.id))
            except:
                return
            ids = range(start, end + 1) if start <= end else list(range(start, end - 1, -1))
        elif len(argument) == 2:
            try:
                ids = [int(int(argument[1]) / abs(client.db_channel.id))]
            except:
                return

        temp_msg = await message.reply("Wait Bro...")
        try:
            messages = await get_messages(client, ids)
        except:
            await message.reply_text("Something went wrong..!")
            return
        await temp_msg.delete()

        titanx_msgs = []

        # Forward messages with optional custom caption
        for msg in messages:
            caption = ""
            if bool(CUSTOM_CAPTION) and bool(msg.document):
                caption = CUSTOM_CAPTION.format(previouscaption="" if not msg.caption else msg.caption.html,
                                                filename=msg.document.file_name)
            elif msg.caption:
                caption = msg.caption.html

            reply_markup = None if not DISABLE_CHANNEL_BUTTON else msg.reply_markup

            try:
                titanx_msg = await msg.copy(chat_id=message.from_user.id, caption=caption,
                                            parse_mode=ParseMode.HTML, reply_markup=reply_markup,
                                            protect_content=PROTECT_CONTENT)
                titanx_msgs.append(titanx_msg)
            except FloodWait as e:
                await asyncio.sleep(e.value)
                titanx_msg = await msg.copy(chat_id=message.from_user.id, caption=caption,
                                            parse_mode=ParseMode.HTML, reply_markup=reply_markup,
                                            protect_content=PROTECT_CONTENT)
                titanx_msgs.append(titanx_msg)
            except Exception as e:
                print(f"Error copying message: {e}")
                pass

        k = await client.send_message(chat_id=message.from_user.id,
                                      text=f"<b>❗️ <u>IMPORTANT</u> ❗️</b>\n\nThis Video / File Will Be Deleted In {file_auto_delete} (Due To Copyright Issues).\n\n📌 Please Forward This Video / File To Somewhere Else And Start Downloading There.")

        # Schedule deletion
        asyncio.create_task(delete_files(titanx_msgs, client, k, base64_string if 'base64_string' in locals() else None))
        return

    # -------------------------------
    # Default start menu
    # -------------------------------
    if admin_status:
        reply_markup = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("🧠 ʜᴇʟᴘ", callback_data="help"),
                 InlineKeyboardButton("🔰 ᴀʙᴏᴜᴛ", callback_data="about")],
                [InlineKeyboardButton("⚙️  Sᴇᴛᴛɪɴɢs", callback_data="settings")]  # Admin-only
            ]
        )
    else:
        reply_markup = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("🧠 ʜᴇʟᴘ", callback_data="help"),
                 InlineKeyboardButton("🔰 ᴀʙᴏᴜᴛ", callback_data="about")]
            ]
        )

    await message.reply_photo(
        photo=START_PIC,
        caption=START_MSG.format(
            first=message.from_user.first_name,
            last=message.from_user.last_name,
            username=None if not message.from_user.username else '@' + message.from_user.username,
            mention=message.from_user.mention,
            id=message.from_user.id
        ),
        reply_markup=reply_markup,
    )

# -------------------------------
# FORCE JOIN HANDLER
# -------------------------------
@Bot.on_message(filters.command('start') & filters.private)
async def not_joined(client: Client, message: Message):
    buttons = [
        [InlineKeyboardButton(text="ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ", url=client.invitelink),
         InlineKeyboardButton(text="ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ", url=client.invitelink2)],
        [InlineKeyboardButton(text="ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ", url=client.invitelink3),
         InlineKeyboardButton(text="ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ", url=client.invitelink4)]
    ]
    try:
        buttons.append(
            [InlineKeyboardButton(
                text='☢ ɴᴏᴡ ᴄʟɪᴄᴋ ʜᴇʀᴇ •',
                url=f"https://t.me/{client.username}?start={message.command[1]}"
            )]
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
# AUTO DELETE FUNCTION
# -------------------------------
async def delete_files(messages, client, k, command_payload=None):
    global AUTO_DELETE_ENABLED

    if not AUTO_DELETE_ENABLED:
        logging.info("Auto-delete is disabled. Skipping deletion.")
        return

    await asyncio.sleep(FILE_AUTO_DELETE)

    for msg in messages:
        try:
            await client.delete_messages(chat_id=msg.chat.id, message_ids=[msg.id])
            logging.info(f"Deleted message {msg.id} in chat {msg.chat.id}")
        except Exception as e:
            logging.error(f"Failed to delete message {msg.id}: {e}")

    keyboard = None
    if command_payload:
        try:
            me = await client.get_me()
            button_url = f"https://t.me/{me.username}?start={command_payload}"
            keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("ɢᴇᴛ ꜰɪʟᴇ ᴀɢᴀɪɴ!", url=button_url)]])
        except Exception as e:
            logging.error(f"Failed to build 'get file' button: {e}")

    try:
        await k.edit_text(
            "ʏᴏᴜʀ ᴠɪᴅᴇᴏ / ꜰɪʟᴇ ɪꜱ ꜱᴜᴄᴇꜱꜰᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ ✅\n"
            "ɴᴏᴡ ᴄʟɪᴄᴋ ʙᴇʟᴏᴡ ʙᴜᴛᴛᴏɴ ᴛᴏ ɢᴇᴛ ʏᴏᴜʀ ᴅᴇʟᴇᴛᴇᴅ ᴠɪᴅᴇᴏ / ꜰɪʟᴇ 👇",
            reply_markup=keyboard,
        )
        logging.info(f"Edited message {k.id} in chat {k.chat.id}")
    except Exception as e:
        logging.error(f"Error editing message after deletion: {e}")

# -------------------------------
# TOGGLE AUTO DELETE
# -------------------------------
def set_auto_delete(state: bool):
    global AUTO_DELETE_ENABLED
    AUTO_DELETE_ENABLED = state
    return AUTO_DELETE_ENABLED

@Client.on_message(filters.command("autodeleteon") & filters.user(ADMINS))
async def handle_autodelete_on(client, message):
    set_auto_delete(True)
    await message.reply_text("✅ ᴀᴜᴛᴏ-ᴅᴇʟᴇᴛᴇ ɪꜱ ɴᴏᴡ ᴇɴᴀʙʟᴇᴅ.")

@Client.on_message(filters.command("autodeleteoff") & filters.user(ADMINS))
async def handle_autodelete_off(client, message):
    set_auto_delete(False)
    await message.reply_text("❌ ᴀᴜᴛᴏ-ᴅᴇʟᴇᴛᴇ ɪꜱ ɴᴏᴡ ᴅɪꜱᴀʙʟᴇᴅ.")
