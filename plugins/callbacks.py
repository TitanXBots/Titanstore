from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from config import START_MSG, HELP_TXT, COMMANDS_TXT, ABOUT_TXT, DISCLAIMER_TXT, START_PIC
from helper_func import safe_edit
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

    if data == "start":
        buttons = [
            [InlineKeyboardButton("👑 ᴍʏ ᴀᴄᴄᴏᴜɴᴛ", callback_data="my_account")],
            [InlineKeyboardButton("🧠 ʜᴇʟᴘ", callback_data="help"), InlineKeyboardButton("🔰 ᴀʙᴏᴜᴛ", callback_data="about")]
        ]
        if await is_admin(user_id):
            buttons.append([InlineKeyboardButton("⚙️ ᴀᴅᴍɪɴ ꜱᴇᴛᴛɪɴɢꜱ", callback_data="settings")])
            
        return await safe_edit(query.message, START_MSG.format(first=first_name), InlineKeyboardMarkup(buttons))

    elif data == "help":
        return await safe_edit(query.message, HELP_TXT.format(first=first_name), InlineKeyboardMarkup([
            [InlineKeyboardButton("🧑‍💻 ᴄᴏɴᴛᴀᴄᴛ ᴏᴡɴᴇʀ", url="https://t.me/TitanXBots"), InlineKeyboardButton("💬 ᴄᴏᴍᴍᴀɴᴅꜱ", callback_data="commands")],
            [InlineKeyboardButton("⚓ ʜᴏᴍᴇ", callback_data="start"), InlineKeyboardButton("⚡ ᴄʟᴏꜱᴇ", callback_data="close")]
        ]))

    elif data == "commands":
        return await safe_edit(query.message, COMMANDS_TXT, InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="help")],
            [InlineKeyboardButton("⚓ ʜᴏᴍᴇ", callback_data="start"), InlineKeyboardButton("⚡ ᴄʟᴏꜱᴇ", callback_data="close")]
        ]))

    elif data == "about":
        return await safe_edit(query.message, ABOUT_TXT.format(first=first_name), InlineKeyboardMarkup([
            [InlineKeyboardButton("📜 ᴅɪꜱᴄʟᴀɪᴍᴇʀ", callback_data="disclaimer"), InlineKeyboardButton("🔐 ꜱᴏᴜʀᴄᴇ", url="https://github.com/TitanXBots/FileStore-Bot")],
            [InlineKeyboardButton("⚓ ʜᴏᴍᴇ", callback_data="start"), InlineKeyboardButton("⚡ ᴄʟᴏꜱᴇ", callback_data="close")]
        ]))

    elif data == "disclaimer":
        return await safe_edit(query.message, DISCLAIMER_TXT, InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="about")],
            [InlineKeyboardButton("⚓ ʜᴏᴍᴇ", callback_data="start"), InlineKeyboardButton("⚡ ᴄʟᴏꜱᴇ", callback_data="close")]
        ]))

    elif data == "close":
        try: await query.message.delete()
        except: pass
            
