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



async def delete_files(messages, client, k, command_payload=None):
    await asyncio.sleep(FILE_AUTO_DELETE)  # Wait for the duration specified in config.py
    
    # Delete all messages first
    for msg in messages:
        try:
            await client.delete_messages(chat_id=msg.chat.id, message_ids=[msg.id])
        except Exception as e:
            print(f"The attempt to delete the media {msg.id} was unsuccessful: {e}")

    # Safeguard against k.command being None or having insufficient parts
    command_part = command_payload

    if command_part:
        button_url = f"https://t.me/{client.username}?start={command_part}"
        keyboard = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("ɢᴇᴛ ғɪʟᴇ ᴀɢᴀɪɴ!", url=button_url)]
            ]
        )
    else:
        keyboard = None

    # Edit message with the button (outside the for loop)
    try:
        await k.edit_text("ʏᴏᴜʀ ᴠɪᴅᴇᴏ / ꜰɪʟᴇ ɪꜱ ꜱᴜᴄᴇꜱꜱꜰᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ ✅\nɴᴏᴡ ᴄʟɪᴄᴋ ʙᴇʟᴏᴡ ʙᴜᴛᴛᴏɴ ᴛᴏ ɢᴇᴛ ʏᴏᴜʀ ᴅᴇʟᴇᴛᴇᴅ ᴠɪᴅᴇᴏ / ꜰɪʟᴇ 👇", reply_markup=keyboard)
    except Exception as e:
        logging.error(f"Error editing the message: {e}")
            



# --- Configuration and Global State ---
# Placeholder for global configuration
FILE_AUTO_DELETE = 60  # Default auto-delete delay in seconds

# Global variable to control auto-delete state
AUTO_DELETE_ENABLED = True  # Default state

# Configu
# --- Core Auto-Delete Logic ---

async def delete_files(messages: list[Message], client: Client, k: Message, command_payload: str = None):
    """
    Deletes a list of messages after a delay if auto-delete is enabled,
    then edits a 'k' message to inform the user.
    """
    global AUTO_DELETE_ENABLED

    if not AUTO_DELETE_ENABLED:
        logger.info(f"Auto-delete is disabled. Skipping deletion for messages: {[m.id for m in messages]}.")
        return

    logger.info(f"Auto-delete enabled. Waiting {FILE_AUTO_DELETE} seconds before deleting messages: {[m.id for m in messages]}.")
    await asyncio.sleep(FILE_AUTO_DELETE)  # Wait for the duration

    # Delete all messages
    for msg in messages:
        try:
            await client.delete_messages(chat_id=msg.chat.id, message_ids=[msg.id])
            logger.info(f"Deleted message {msg.id} in chat {msg.chat.id}")
        except Exception as e:
            logger.error(f"Failed to delete message {msg.id} in chat {msg.chat.id}: {e}")

    # Construct the inline keyboard button
    keyboard = None
    if command_payload:
        # Assuming client.username is available, if not, use a direct link like "t.me/your_bot_username"
        bot_username = (await client.get_me()).username if not client.username else client.username
        button_url = f"https://t.me/{bot_username}?start={command_payload}"
        keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton("ɢᴇᴛ ғɪʟᴇ ᴀɢᴀɪɴ!", url=button_url)]]
        )

    # Edit the message 'k' to inform the user
    try:
        await k.edit_text(
            "ʏᴏᴜʀ ᴠɪᴅᴇᴏ / ꜰɪʟᴇ ɪꜱ ꜱᴜᴄᴇꜱꜱꜰᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ ✅\nɴᴏᴡ ᴄʟɪᴄᴋ ʙᴇʟᴏᴡ ʙᴜᴛᴛᴏɴ ᴛᴏ ɢᴇᴛ ʏᴏᴜʀ ᴅᴇʟᴇᴛᴇᴅ ᴠɪᴅᴇᴏ / ꜰɪʟᴇ 👇",
            reply_markup=keyboard,
        )
        logger.info(f"Successfully edited message {k.id} in chat {k.chat.id} after deletion.")
    except Exception as e:
        logger.error(f"Error editing message {k.id} after deletion: {e}")

# --- Settings and Inline Button Logic ---

def get_settings_message_and_keyboard():
    """
    Generates the text and inline keyboard for the auto-delete settings.
    """
    current_state_text = "Enabled" if AUTO_DELETE_ENABLED else "Disabled"
    text = (
        f"⚙️ **Auto-Delete Settings**\n\n"
        f"Auto-delete is currently: **{current_state_text}**\n\n"
        f"Choose an option below to change the setting."
    )

    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("✅ Enable Auto-delete", callback_data="set_auto_delete_on")],
            [InlineKeyboardButton("❌ Disable Auto-delete", callback_data="set_auto_delete_off")]
        ]
    )
    return text, keyboard

@Client.on_message(filters.command("settings"))
async def settings_command_handler(client: Client, message: Message):
    """
    Handles the /settings command, displaying the current auto-delete state
    and inline buttons to change it.
    """
    logger.info(f"Received /settings command from user {message.from_user.id} in chat {message.chat.id}")
    text, keyboard = get_settings_message_and_keyboard()
    await message.reply_text(text, reply_markup=keyboard, parse_mode="markdown")

@Client.on_callback_query(filters.regex(r"set_auto_delete_on|set_auto_delete_off"))
async def settings_callback_handler(client: Client, callback_query: CallbackQuery):
    """
    Handles callback queries from the auto-delete settings inline keyboard.
    Toggles the AUTO_DELETE_ENABLED state and updates the settings message.
    """
    global AUTO_DELETE_ENABLED
    data = callback_query.data
    user_id = callback_query.from_user.id
    chat_id = callback_query.message.chat.id
    message_id = callback_query.message.id

    logger.info(f"Received callback query '{data}' from user {user_id} in chat {chat_id}")

    # Optional: You might want to add a check here to ensure only the user
    # who invoked the /settings command can interact with its buttons.
    # For simplicity, we'll allow any user in the chat to press for now.
    # if user_id != callback_query.message.reply_to_message.from_user.id:
    #     await callback_query.answer("You can only change settings for your own messages!", show_alert=True)
    #     return

    toast_text = ""
    if data == "set_auto_delete_on":
        if not AUTO_DELETE_ENABLED:
            AUTO_DELETE_ENABLED = True
            toast_text = "Auto-delete is now ENABLED."
            logger.info("Auto-delete state changed to ENABLED.")
        else:
            toast_text = "Auto-delete is already enabled."
    elif data == "set_auto_delete_off":
        if AUTO_DELETE_ENABLED:
            AUTO_DELETE_ENABLED = False
            toast_text = "Auto-delete is now DISABLED."
            logger.info("Auto-delete state changed to DISABLED.")
        else:
            toast_text = "Auto-delete is already disabled."

    # Regenerate the message and keyboard based on the new state
    new_text, new_keyboard = get_settings_message_and_keyboard()

    # Edit the original message to reflect the new state
    try:
        await callback_query.message.edit_text(
            new_text,
            reply_markup=new_keyboard,
            parse_mode="markdown"
        )
        # Show a small toast notification to the user
        await callback_query.answer(toast_text)
        logger.info(f"Edited settings message {message_id} in chat {chat_id} and answered callback.")
    except Exception as e:
        logger.error(f"Error editing settings message {message_id} or answering callback: {e}")
        await callback_query.answer("An error occurred while updating settings.", show_alert=True)


# --- Main Execution Block ---
if __name__ == "__main__":
    logger.info("Bot starting...")
    app.run()
    logger.info("Bot stopped.")
    


# Dont Remove Credit
# Update Channel - TitanXBots
# Ask Any Doubt on Telegram - @TitanOwner
# Support Group - @TitanMattersSupport
