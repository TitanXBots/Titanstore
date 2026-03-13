import os
import asyncio
import humanize
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated
from Script import NEW_USER_TXT
from bot import Bot
from config import *
from helper_func import subscribed, encode, decode, get_messages
from database.database import add_user, del_user, full_userbase, present_user, is_banned, get_ban_reason
import logging
from pymongo import MongoClient

client = MongoClient(DB_URI)
db = client[DB_NAME]
collection = db["TelegramFiles"]

AUTO_DELETE_ENABLED = True  
titanxofficials = FILE_AUTO_DELETE
file_auto_delete = humanize.naturaldelta(titanxofficials)


async def is_maintenance(user_id:int) -> bool:
    check_msg = collection.find_one({"maintenance": "on"})
    if check_msg and user_id not in ADMINS:
        return True
    return False


@Bot.on_message(filters.command('start') & filters.private)
async def start_command(client: Client, message: Message):
    user_id = message.from_user.id

    # 🚫 Ban check
    if await is_banned(user_id):
        reason = await get_ban_reason(user_id)
        await message.reply_text(f"🚫 You are banned from using this bot.\n\n**Reason:** {reason}")
        return

    # ✅ Add new user
    if not await present_user(user_id):
        try:
            await add_user(user_id)
            user_name = message.from_user.first_name or "Unknown"
            message_text = NEW_USER_TXT.format(message.from_user.mention, user_id, user_name)
            await client.send_message(LOG_CHANNEL_ID, message_text)
        except:
            pass

    # ⚙️ Maintenance check
    if await is_maintenance(user_id):
        await message.reply_text("⚙️ Maintenance mode is currently active. Please try again later.")
        return

    # 🚪 Check if user has joined required channels
    joined = await check_joined_channels(client, user_id)
    if not joined:
        buttons = [
            [InlineKeyboardButton("ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ", url=client.invitelink),
             InlineKeyboardButton("ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ", url=client.invitelink2)],
            [InlineKeyboardButton("ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ", url=client.invitelink3),
             InlineKeyboardButton("ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ", url=client.invitelink4)]
        ]
        try:
            buttons.append([InlineKeyboardButton(
                text='☢ ɴᴏᴡ ᴄʟɪᴄᴋ ʜᴇʀᴇ •',
                url=f"https://t.me/{client.username}?start={message.command[1]}"
            )])
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
        return

    # Handle base64 payload (file download)
    text = message.text
    if len(text) > 7:
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
                if start <= end:
                    ids = range(start, end + 1)
                else:
                    i = start
                    while i >= end:
                        ids.append(i)
                        i -= 1
            elif len(argument) == 2:
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
        for msg in messages:
            caption = CUSTOM_CAPTION.format(
                previouscaption="" if not msg.caption else msg.caption.html,
                filename=msg.document.file_name
            ) if bool(CUSTOM_CAPTION) and bool(msg.document) else "" if not msg.caption else msg.caption.html
            reply_markup = None if not DISABLE_CHANNEL_BUTTON else msg.reply_markup
            try:
                titanx_msg = await msg.copy(
                    chat_id=user_id, caption=caption, parse_mode=ParseMode.HTML,
                    reply_markup=reply_markup, protect_content=PROTECT_CONTENT
                )
                titanx_msgs.append(titanx_msg)
            except FloodWait as e:
                await asyncio.sleep(e.value)
                titanx_msg = await msg.copy(
                    chat_id=user_id, caption=caption, parse_mode=ParseMode.HTML,
                    reply_markup=reply_markup, protect_content=PROTECT_CONTENT
                )
                titanx_msgs.append(titanx_msg)
            except Exception as e:
                print(f"Error copying message: {e}")

        k = await client.send_message(
            chat_id=user_id,
            text=f"<b>❗️ <u>IMPORTANT</u> ❗️</b>\n\n"
                 f"This Video / File Will Be Deleted In {file_auto_delete} "
                 f"(Due To Copyright Issues).\n\n"
                 f"📌 Please Forward This Video / File To Somewhere Else And Start Downloading There."
        )

        asyncio.create_task(delete_files(titanx_msgs, client, k, base64_string))
        return

    # Default start message
    buttons = [
        [InlineKeyboardButton("🧠 ʜᴇʟᴘ", callback_data="help"),
         InlineKeyboardButton("🔰 ᴀʙᴏᴜᴛ", callback_data="about")],
        [InlineKeyboardButton("⚙️  Sᴇᴛᴛɪɴɢs", callback_data="settings")]
    ]
    await message.reply_photo(
        photo=START_PIC,
        caption=START_MSG.format(
            first=message.from_user.first_name,
            last=message.from_user.last_name,
            username=None if not message.from_user.username else '@' + message.from_user.username,
            mention=message.from_user.mention,
            id=message.from_user.id
        ),
        reply_markup=InlineKeyboardMarkup(buttons)
    )


# ====== AUTO DELETE FUNCTION ======
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
            keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("ɢᴇᴛ ғɪʟᴇ ᴀɢᴀɪɴ!", url=button_url)]])
        except Exception as e:
            logging.error(f"Failed to build 'get file' button: {e}")

    try:
        await k.edit_text(
            "ʏᴏᴜʀ ᴠɪᴅᴇᴏ / ꜰɪʟᴇ ɪꜱ ꜱᴜᴄᴇꜱꜰᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ ✅\n"
            "ɴᴏᴡ ᴄʟɪᴄᴋ ʙᴇʟᴏᴡ ʙᴜᴛᴛᴏɴ ᴛᴏ ɢᴇᴛ ʏᴏᴜʀ ᴅᴇʟᴇᴛᴇᴅ ᴠɪᴅᴇᴏ / ꜰɪʟᴇ 👇",
            reply_markup=keyboard
        )
    except Exception as e:
        logging.error(f"Error editing message after deletion: {e}")


# ====== TOGGLE STATE ======
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
