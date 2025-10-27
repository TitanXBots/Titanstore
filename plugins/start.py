import os
import asyncio
import humanize
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated
from Script import NEW_USER_TXT
from bot import Bot
from config import *
from helper_func import subscribed, encode, decode, get_messages
from database.database import add_user, del_user, full_userbase, present_user


titanxofficials = FILE_AUTO_DELETE
titandeveloper = titanxofficials
file_auto_delete = humanize.naturaldelta(titandeveloper)

@Bot.on_message(filters.command('start') & filters.private & subscribed)
async def start_command(client: Client, message: Message):
    user_id = message.from_user.id
    if not await present_user(user_id):
        try:
            await add_user(user_id)
            user_name = message.from_user.first_name or "Unknown"
            message_text = NEW_USER_TXT.format(message.from_user.mention, user_id, user_name)
            await client.send_message(LOG_CHANNEL_ID, message_text)
        except:
            pass
    text = message.text
    if len(text)>7:
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
            if start <= end:
                ids = range(start,end+1)
            else:
                ids = []
                i = start
                while True:
                    ids.append(i)
                    i -= 1
                    if i < end:
                        break
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

        titanx_msgs = [] # List to keep track of sent message 

        for msg in messages:

            if bool(CUSTOM_CAPTION) & bool(msg.document):
                caption = CUSTOM_CAPTION.format(previouscaption = "" if not msg.caption else msg.caption.html, filename = msg.document.file_name)
            else:
                caption = "" if not msg.caption else msg.caption.html

            if DISABLE_CHANNEL_BUTTON:
                reply_markup = msg.reply_markup
            else:
                reply_markup = None

            try:
                titanx_msg = await msg.copy(chat_id=message.from_user.id, caption = caption, parse_mode = ParseMode.HTML, reply_markup = reply_markup, protect_content=PROTECT_CONTENT)
                titanx_msgs.append(titanx_msg)
                
            except FloodWait as e:
                await asyncio.sleep(e.value)
                titanx_msg = await msg.copy(chat_id=message.from_user.id, caption = caption, parse_mode = ParseMode.HTML, reply_markup = reply_markup, protect_content=PROTECT_CONTENT)
                titanx_msgs.append(titanx_msg)
            except Exception as e:
                print(f"Error coping message: {e}")
                pass

        k = await client.send_message(chat_id=message.from_user.id, text=f"<b>❗️ <u>IMPORTANT</u> ❗️</b>\n\nThis Video / File Will Be Deleted In {file_auto_delete} (Due To Copyright Issues).\n\n📌 Please Forward This Video / File To Somewhere Else And Start Downloading There.")

        # Schedule the file deletion
        asyncio.create_task(delete_files(titanx_msgs, client, k, base64_string if 'base64_string' in locals() else None))
        
        return
    else:
        reply_markup = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("🧠 ʜᴇʟᴘ", callback_data = "help"),
                    InlineKeyboardButton("🔰 ᴀʙᴏᴜᴛ", callback_data = "about")
                ]
            ]
        )
        await message.reply_photo(
            photo= START_PIC,
            caption= START_MSG.format(
                first = message.from_user.first_name,
                last = message.from_user.last_name,
                username = None if not message.from_user.username else '@' + message.from_user.username,
                mention = message.from_user.mention,
                id = message.from_user.id
            ),
            reply_markup = reply_markup,
            
        )
        return
    

#=====================================================================================##

WAIT_MSG = "<b>Working....</b>"

REPLY_ERROR = "<code>Use this command as a reply to any telegram message without any spaces.</code>"

#=====================================================================================##

    
    
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
                    text = '☢ ɴᴏᴡ ᴄʟɪᴄᴋ ʜᴇʀᴇ •',
                    url = f"https://t.me/{client.username}?start={message.command[1]}"
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

@Bot.on_message(filters.command('users') & filters.private & filters.user(ADMINS))
async def get_users(client: Bot, message: Message):
    msg = await client.send_message(chat_id=message.chat.id, text=WAIT_MSG)
    users = await full_userbase()
    await msg.edit(f"{len(users)} users are using this bot")

@Bot.on_message(filters.private & filters.command('broadcast') & filters.user(ADMINS))
async def send_text(client: Bot, message: Message):
    if message.reply_to_message:
        query = await full_userbase()
        broadcast_msg = message.reply_to_message
        total = 0
        successful = 0
        blocked = 0
        deleted = 0
        unsuccessful = 0
        
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
                pass
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




import logging



# Global state
AUTO_DELETE_ENABLED = True  # Default: auto-delete enabled

async def delete_files(messages, client, k, command_payload=None):
    """Deletes specified messages after a delay if auto-delete is enabled."""
    global AUTO_DELETE_ENABLED

    if not AUTO_DELETE_ENABLED:
        logging.info("Auto-delete disabled. Skipping deletion.")
        return

    await asyncio.sleep(FILE_AUTO_DELETE)

    for msg in messages:
        try:
            await client.delete_messages(chat_id=msg.chat.id, message_ids=[msg.id])
            logging.info(f"Deleted message {msg.id} in chat {msg.chat.id}")
        except Exception as e:
            logging.error(f"Failed to delete message {msg.id}: {e}")

    if command_payload:
        button_url = f"https://t.me/{client.username}?start={command_payload}"
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Get File Again!", url=button_url)]])
    else:
        keyboard = None

    try:
        await k.edit_text("File deleted. Click below to get it again.", reply_markup=keyboard)
        logging.info(f"Edited message {k.id} after deletion.")
    except Exception as e:
        logging.error(f"Error editing message after deletion: {e}")

# --- New/Modified Functions for Inline Buttons ---

def update_auto_delete_state(enable: bool):
    """Updates the global AUTO_DELETE_ENABLED state."""
    global AUTO_DELETE_ENABLED
    AUTO_DELETE_ENABLED = enable
    return AUTO_DELETE_ENABLED

def create_settings_keyboard():
    """Creates the settings keyboard with separate Enable/Disable buttons."""
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("✅ Enable Auto-Delete", callback_data="enable_autodelete"),
                InlineKeyboardButton("❌ Disable Auto-Delete", callback_data="disable_autodelete")
            ]
        ]
    )
    return keyboard

def get_current_status_text():
    """Returns a text string indicating the current auto-delete status."""
    return f"Auto-delete is currently **{'ENABLED' if AUTO_DELETE_ENABLED else 'DISABLED'}**."
async def handle_settings_command(client, message):
    """Handles the /settings command to show the settings keyboard."""
    keyboard = create_settings_keyboard()
    status_text = get_current_status_text()
    await message.reply_text(
        f"Auto-Delete Settings:\n{status_text}",
        reply_markup=keyboard,
        parse_mode="markdown" # Enable markdown for bold text
    )

async def handle_callback_query(client, callback_query):
    """Handles inline button presses for auto-delete settings."""
    message_text = "Auto-Delete Settings:\n"
    new_state_set = None

    if callback_query.data == "enable_autodelete":
        new_state_set = update_auto_delete_state(True)
        feedback_text = "Auto-delete is now **ENABLED**."
        logging.info("Auto-delete enabled via button.")
    elif callback_query.data == "disable_autodelete":
        new_state_set = update_auto_delete_state(False)
        feedback_text = "Auto-delete is now **DISABLED**."
        logging.info("Auto-delete disabled via button.")
    else:
        # If it's another callback_data, let other handlers potentially process it
        return

    # Update the message with the new status and the same buttons
    status_text = get_current_status_text()
    keyboard = create_settings_keyboard()
    await callback_query.edit_message_text(
        f"{message_text}{status_text}",
        reply_markup=keyboard,
        parse_mode="markdown"
    )
    await callback_query.answer(feedback_text) # Show a popup notification to the user

# --- Pyrogram Setup ---
app = Client("auto_delete_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@client.on_message(filters.command("settings"))
async def settings_command(client, message):
    await handle_settings_command(client, message)

@Bot.on_callback_query()
async def callback_query_handler(client, callback_query):
    await handle_callback_query(client, callback_query)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    print("Bot started")
    app.run()



# Dont Remove Credit
# Update Channel - TitanXBots
# Ask Any Doubt on Telegram - @TitanOwner
# Support Group - @TitanMattersSupport
