from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from config import START_MSG, HELP_TXT, COMMANDS_TXT, ABOUT_TXT, DISCLAIMER_TXT
from database.database import is_admin, is_maintenance
from helper_func import safe_edit

@Client.on_callback_query(filters.regex("^(start|help|commands|about|disclaimer|close|admin_panel|settings)$"))
async def generic_cb_handler(client: Client, query: CallbackQuery):
    try: await query.answer()
    except: pass
    user_id = query.from_user.id
    
    # Blocks non-admins if Maintenance is ON
    if await is_maintenance(user_id):
        return await query.answer("🛠 ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ ᴍᴏᴅᴇ ᴏɴ. ᴘʟᴇᴀꜱᴇ ᴛʀʏ ᴀɢᴀɪɴ ʟᴀᴛᴇʀ.", show_alert=True)
        
    data = query.data
    first_name = query.from_user.first_name or "User"
    new_text, buttons = "", []

    if data == "start":
        new_text = START_MSG.format(first=first_name)
        buttons = [
            [InlineKeyboardButton("👑 ᴍʏ ᴀᴄᴄᴏᴜɴᴛ", callback_data="my_account")],
            [InlineKeyboardButton("🧠 ʜᴇʟᴘ", callback_data="help"), InlineKeyboardButton("🔰 ᴀʙᴏᴜᴛ", callback_data="about")]
        ]
        if await is_admin(user_id):
            buttons.append([InlineKeyboardButton("⚙️ ᴀᴅᴍɪɴ ꜱᴇᴛᴛɪɴɢꜱ", callback_data="settings")])

    elif data in ["settings", "admin_panel"]:
        if not await is_admin(user_id): return await query.answer("⚠️ ᴀᴄᴄᴇꜱꜱ ᴅᴇɴɪᴇᴅ!", show_alert=True)
        new_text = "⚙️ <b>ᴀᴅᴍɪɴ ꜱᴇᴛᴛɪɴɢꜱ ᴘᴀɴᴇʟ</b>"
        
        # 🚀 LAYOUT FIX: Protect Content and Maintenance are now side-by-side in ONE row!
        buttons = [
            [InlineKeyboardButton("👨‍💻 ᴀᴅᴍɪɴ ᴍᴇɴᴜ", callback_data="admin_menu"), InlineKeyboardButton("🚫 ʙᴀɴ ᴍᴇɴᴜ", callback_data="ban_menu")],
            [InlineKeyboardButton("🗑 ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ", callback_data="autodelete_menu"), InlineKeyboardButton("📁 ᴀᴅᴅ ᴄʜᴀɴɴᴇʟꜱ", callback_data="add_channels_menu")],
            [InlineKeyboardButton("🔒 ᴘʀᴏᴛᴇᴄᴛ ᴄᴏɴᴛᴇɴᴛ", callback_data="protect_menu"), InlineKeyboardButton("🛠 ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ", callback_data="maint_menu")],
            [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="start")]
        ]

    elif data == "help":
        new_text = HELP_TXT.format(first=first_name)
        buttons = [
            [InlineKeyboardButton("🧑‍💻 ᴄᴏɴᴛᴀᴄᴛ ᴏᴡɴᴇʀ", url="https://t.me/TitanXBots"), InlineKeyboardButton("💬 ᴄᴏᴍᴍᴀɴᴅꜱ", callback_data="commands")],
            [InlineKeyboardButton("⚓ ʜᴏᴍᴇ", callback_data="start"), InlineKeyboardButton("⚡ ᴄʟᴏꜱᴇ", callback_data="close")]
        ]

    elif data == "commands":
        new_text = COMMANDS_TXT
        buttons = [[InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="help"), InlineKeyboardButton("⚓ ʜᴏᴍᴇ", callback_data="start")], [InlineKeyboardButton("⚡ ᴄʟᴏꜱᴇ", callback_data="close")]]

    elif data == "about":
        new_text = ABOUT_TXT.format(first=first_name)
        buttons = [[InlineKeyboardButton("📜 ᴅɪꜱᴄʟᴀɪᴍᴇʀ", callback_data="disclaimer"), InlineKeyboardButton("🔐 ꜱᴏᴜʀᴄᴇ", url="https://github.com/TitanXBots/FileStore-Bot")], [InlineKeyboardButton("⚓ ʜᴏᴍᴇ", callback_data="start"), InlineKeyboardButton("⚡ ᴄʟᴏꜱᴇ", callback_data="close")]]

    elif data == "disclaimer":
        new_text = DISCLAIMER_TXT
        buttons = [[InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="about"), InlineKeyboardButton("⚓ ʜᴏᴍᴇ", callback_data="start")], [InlineKeyboardButton("⚡ ᴄʟᴏꜱᴇ", callback_data="close")]]

    elif data == "close":
        try: await query.message.delete()
        except: pass
        return
        
    await safe_edit(query.message, new_text, InlineKeyboardMarkup(buttons))
    
