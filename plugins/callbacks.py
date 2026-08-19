import logging
from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import MessageNotModified

from config import START_MSG, HELP_TXT, COMMANDS_TXT, ABOUT_TXT, DISCLAIMER_TXT
from database.database import is_admin, is_maintenance

@Client.on_callback_query(filters.regex("^(start|help|commands|about|disclaimer|close)$"))
async def generic_cb_handler(client: Client, query: CallbackQuery):
    try: await query.answer()
    except: pass
    
    user_id = query.from_user.id
    
    if await is_maintenance(user_id):
        return await query.answer("🛠 ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ ᴍᴏᴅᴇ ᴏɴ.", show_alert=True)
        
    data = query.data
    first_name = query.from_user.first_name or "User"

    # Pre-define variables to hold our new text and buttons
    new_text = ""
    buttons = []

    if data == "start":
        new_text = START_MSG.format(first=first_name)
        buttons = [
            [InlineKeyboardButton("👑 ᴍʏ ᴀᴄᴄᴏᴜɴᴛ", callback_data="my_account")],
            [InlineKeyboardButton("🧠 ʜᴇʟᴘ", callback_data="help"), InlineKeyboardButton("🔰 ᴀʙᴏᴜᴛ", callback_data="about")]
        ]
        if await is_admin(user_id):
            buttons.append([InlineKeyboardButton("⚙️ ᴀᴅᴍɪɴ ꜱᴇᴛᴛɪɴɢꜱ", callback_data="settings")])

    elif data == "help":
        new_text = HELP_TXT.format(first=first_name)
        buttons = [
            [InlineKeyboardButton("🧑‍💻 ᴄᴏɴᴛᴀᴄᴛ ᴏᴡɴᴇʀ", url="https://t.me/TitanXBots"), InlineKeyboardButton("💬 ᴄᴏᴍᴍᴀɴᴅꜱ", callback_data="commands")],
            [InlineKeyboardButton("⚓ ʜᴏᴍᴇ", callback_data="start"), InlineKeyboardButton("⚡ ᴄʟᴏꜱᴇ", callback_data="close")]
        ]

    elif data == "commands":
        new_text = COMMANDS_TXT
        buttons = [
            [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="help")],
            [InlineKeyboardButton("⚓ ʜᴏᴍᴇ", callback_data="start"), InlineKeyboardButton("⚡ ᴄʟᴏꜱᴇ", callback_data="close")]
        ]

    elif data == "about":
        new_text = ABOUT_TXT.format(first=first_name)
        buttons = [
            [InlineKeyboardButton("📜 ᴅɪꜱᴄʟᴀɪᴍᴇʀ", callback_data="disclaimer"), InlineKeyboardButton("🔐 ꜱᴏᴜʀᴄᴇ", url="https://github.com/TitanXBots/FileStore-Bot")],
            [InlineKeyboardButton("⚓ ʜᴏᴍᴇ", callback_data="start"), InlineKeyboardButton("⚡ ᴄʟᴏꜱᴇ", callback_data="close")]
        ]

    elif data == "disclaimer":
        new_text = DISCLAIMER_TXT
        buttons = [
            [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="about")],
            [InlineKeyboardButton("⚓ ʜᴏᴍᴇ", callback_data="start"), InlineKeyboardButton("⚡ ᴄʟᴏꜱᴇ", callback_data="close")]
        ]

    elif data == "close":
        try: 
            await query.message.delete()
        except: 
            pass
        return
        
    # --- BULLETPROOF EDITING LOGIC ---
    try:
        # If the original message has a photo/video, we must edit the caption
        if query.message.media:
            await query.message.edit_caption(
                caption=new_text, 
                reply_markup=InlineKeyboardMarkup(buttons)
            )
        # If it's just a text message, we edit the text
        else:
            await query.message.edit_text(
                text=new_text, 
                reply_markup=InlineKeyboardMarkup(buttons)
            )
    except MessageNotModified:
        # If the user clicks a button they are already viewing, ignore the error
        pass
    except Exception as e:
        logging.error(f"Callback edit error: {e}")
        
