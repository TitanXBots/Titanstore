import os
import asyncio
import humanize
import logging
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated
from pymongo import MongoClient

from bot import Bot
from config import *
from Script import *
from helper_func import subscribed, encode, decode, get_messages
from database.database import add_user, del_user, full_userbase, present_user, banned_users, ban_user, unban_user, is_banned, get_ban_reason

# -------------------------------
# DATABASE SETUP
# -------------------------------
client = MongoClient(DB_URI)
db = client[DB_NAME]
collection = db["TelegramFiles"]

AUTO_DELETE_ENABLED = True
file_auto_delete = humanize.naturaldelta(FILE_AUTO_DELETE)

# -------------------------------
# HELPER FUNCTIONS
# -------------------------------
async def is_maintenance(client, user_id: int) -> bool:
    check_msg = collection.find_one({"maintenance": "on"})
    if check_msg and user_id not in ADMINS:
        return True
    return False


def set_auto_delete(state: bool):
    global AUTO_DELETE_ENABLED
    AUTO_DELETE_ENABLED = state
    return AUTO_DELETE_ENABLED


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
            keyboard = InlineKeyboardMarkup(
                [[InlineKeyboardButton("ɢᴇᴛ ғɪʟᴇ ᴀɢᴀɪɴ!", url=button_url)]]
            )
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
# START COMMAND (Combined)
# -------------------------------
@Bot.on_message(filters.command("start") & filters.private)
async def start_command(client: Client, message: Message):
    user_id = message.from_user.id

    # ---------- BAN CHECK ----------
    if await is_banned(user_id):
        reason = await get_ban_reason(user_id)
        await message.reply_text(f"🚫 You are banned from using this bot.\n\n**Reason:** {reason}")
        return

    # ---------- ADD NEW USER ----------
    if not await present_user(user_id):
        try:
            await add_user(user_id)
            user_name = message.from_user.first_name or "Unknown"
            msg_text = NEW_USER_TXT.format(message.from_user.mention, user_id, user_name)
            await client.send_message(LOG_CHANNEL_ID, msg_text)
        except:
            pass

    # ---------- MAINTENANCE CHECK ----------
    if await is_maintenance(client, user_id):
        await message.reply_text("⚙️ Maintenance mode is active. Try again later.")
        return

    # ---------- ADMIN CHECK ----------
    is_admin_user = user_id == OWNER_ID or user_id in ADMINS

    text = message.text

    # ---------- HANDLE FILE COPY WITH BASE64 PAYLOAD ----------
    if len(text) > 7:
        try:
            base64_string = text.split(" ", 1)[1]
        except:
            return

        string = await decode(base64_string)
        argument = string.split("-")
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
        for msg in messages:
            caption = (CUSTOM_CAPTION.format(
                        previouscaption="" if not msg.caption else msg.caption.html,
                        filename=msg.document.file_name)
                       if bool(CUSTOM_CAPTION) and bool(msg.document)
                       else "" if not msg.caption else msg.caption.html)
            reply_markup = msg.reply_markup if DISABLE_CHANNEL_BUTTON else None
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
                                     text=f"<b>❗️ <u>IMPORTANT</u> ❗️</b>\n\n"
                                          f"This Video / File Will Be Deleted In {file_auto_delete} (Due To Copyright Issues).\n\n"
                                          f"📌 Forward this Video / File elsewhere to download safely.")

        asyncio.create_task(delete_files(titanx_msgs, client, k, base64_string))
        return

    # ---------- CHECK SUBSCRIPTION ----------
    is_subscribed = await subscribed(user_id)

    if not is_subscribed:
        # ---------- FORCE JOIN PANEL ----------
        buttons = [
            [InlineKeyboardButton("ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ", url=client.invitelink),
             InlineKeyboardButton("ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ", url=client.invitelink2)],
            [InlineKeyboardButton("ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ", url=client.invitelink3),
             InlineKeyboardButton("ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ", url=client.invitelink4)]
        ]
        try:
            buttons.append(
                [InlineKeyboardButton("☢ ɴᴏᴡ ᴄʟɪᴄᴋ ʜᴇʀᴇ •",
                                      url=f"https://t.me/{client.username}?start={message.command[1]}")]
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
        return

    # ---------- SHOW START PANEL ----------
    buttons = [
        [InlineKeyboardButton("🧠 Help", callback_data="help"),
         InlineKeyboardButton("🔰 About", callback_data="about")]
    ]

    if is_admin_user:
        buttons.append([InlineKeyboardButton("⚙️ Settings", callback_data="settings")])

    await message.reply_photo(
        photo=START_PIC,
        caption=START_MSG.format(
            first=message.from_user.first_name,
            last=message.from_user.last_name,
            username=None if not message.from_user.username else '@' + message.from_user.username,
            mention=message.from_user.mention,
            id=message.from_user.id
        ),
        reply_markup=InlineKeyboardMarkup(buttons),
    )

# -------------------------------
# USERS & BROADCAST COMMANDS
# -------------------------------
WAIT_MSG = "<b>Working....</b>"
REPLY_ERROR = "<code>Use this command as a reply to any telegram message without any spaces.</code>"

@Bot.on_message(filters.command("users") & filters.private & filters.user(ADMINS))
async def get_users(client: Bot, message: Message):
    msg = await client.send_message(chat_id=message.chat.id, text=WAIT_MSG)
    users = await full_userbase()
    await msg.edit(f"{len(users)} users are using this bot")


@Bot.on_message(filters.private & filters.command("broadcast") & filters.user(ADMINS))
async def send_text(client: Bot, message: Message):
    if message.reply_to_message:
        query = await full_userbase()
        broadcast_msg = message.reply_to_message
        total = successful = blocked = deleted = unsuccessful = 0

        pls_wait = await message.reply("<i>ʙʀᴏᴀᴅᴄᴀꜱᴛ ᴘʀᴏᴄᴇꜱꜱɪɴɢ....</i>")
        for chat_id in query:
            try:
                await broadcast_msg.copy(chat_id)
                successful += 1
            except FloodWait as e:
                await asyncio.sleep(e.x)
                await broadcast_msg.copy(chat_id)
                successful += 1
            except UserIsBlocked:
                await del_user(chat_id)
                blocked += 1
            except InputUserDeactivated:
                await del_user(chat_id)
                deleted += 1
            except:
                unsuccessful += 1
            total += 1

        status = f"""<b><u>ʙʀᴏᴀᴅᴄᴀꜱᴛ...</u>
Total Users: <code>{total}</code>
Successful: <code>{successful}</code>
Blocked Users: <code>{blocked}</code>
Deleted Accounts: <code>{deleted}</code>
Unsuccessful: <code>{unsuccessful}</code></b>"""

        return await pls_wait.edit(status)
    else:
        msg = await message.reply(REPLY_ERROR)
        await asyncio.sleep(8)
        await msg.delete()


# -------------------------------
# AUTO-DELETE TOGGLE COMMANDS
# -------------------------------
@Client.on_message(filters.command("autodeleteon") & filters.user(ADMINS))
async def handle_autodelete_on(client, message):
    set_auto_delete(True)
    await message.reply_text("✅ ᴀᴜᴛᴏ-ᴅᴇʟᴇᴛᴇ ɪꜱ ɴᴏᴡ ᴇɴᴀʙʟᴇᴅ.")


@Client.on_message(filters.command("autodeleteoff") & filters.user(ADMINS))
async def handle_autodelete_off(client, message):
    set_auto_delete(False)
    await message.reply_text("❌ ᴀᴜᴛᴏ-ᴅᴇʟᴇᴛᴇ ɪꜱ ɴᴏᴡ ᴅɪꜱᴀʙʟᴇᴅ.")
