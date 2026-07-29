from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from helper_func import safe_edit
from database.database import is_admin, get_protect_status, set_protect_status

@Client.on_callback_query(filters.regex("^(settings|protect_menu|protect_on|protect_off)$"))
async def settings_cb(client: Client, query: CallbackQuery):
    if not await is_admin(query.from_user.id): 
        return await query.answer("⚠️ ᴀᴄᴄᴇꜱꜱ ᴅᴇɴɪᴇᴅ: ꜱᴇᴛᴛɪɴɢꜱ ᴀʀᴇ ꜰᴏʀ ᴀᴅᴍɪɴꜱ ᴏɴʟʏ!", show_alert=True)
        
    data = query.data

    if data == "settings":
        return await safe_edit(query.message, "⚙️ ᴀᴅᴍɪɴ ꜱᴇᴛᴛɪɴɢꜱ ᴘᴀɴᴇʟ", InlineKeyboardMarkup([
            [
                InlineKeyboardButton("👨‍💻 ᴀᴅᴍɪɴ ᴍᴇɴᴜ", callback_data="admin_menu"), 
                InlineKeyboardButton("🚫 ʙᴀɴ ᴍᴇɴᴜ", callback_data="ban_menu")
            ],
            [
                InlineKeyboardButton("💎 ᴘʀᴇᴍɪᴜᴍ ᴍᴇɴᴜ", callback_data="premium_menu"), 
                InlineKeyboardButton("🗑 ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ", callback_data="autodelete_menu")
            ],
            [
                InlineKeyboardButton("🔒 ᴘʀᴏᴛᴇᴄᴛ ᴄᴏɴᴛᴇɴᴛ", callback_data="protect_menu")
            ],
            [
                InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="start")
            ]
        ]))

    elif data == "protect_menu":
        is_on = await get_protect_status()
        status = "ᴏɴ ✅" if is_on else "ᴏꜰꜰ ❌"
        return await safe_edit(query.message, f"🔒 <b>ᴘʀᴏᴛᴇᴄᴛ ᴄᴏɴᴛᴇɴᴛ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ</b>\n\nᴘʀᴇᴠᴇɴᴛꜱ ᴜꜱᴇʀꜱ ꜰʀᴏᴍ ꜰᴏʀᴡᴀʀᴅɪɴɢ, ꜱᴀᴠɪɴɢ, ᴏʀ ᴄᴏᴘʏɪɴɢ ꜰɪʟᴇꜱ.\n\nᴄᴜʀʀᴇɴᴛ ꜱᴛᴀᴛᴜꜱ: <b>{status}</b>", InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ ᴇɴᴀʙʟᴇ", callback_data="protect_on"), 
                InlineKeyboardButton("❌ ᴅɪꜱᴀʙʟᴇ", callback_data="protect_off")
            ],
            [
                InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="settings")
            ]
        ]))

    elif data == "protect_on":
        if await get_protect_status():
            return await query.answer("⚠️ ᴘʀᴏᴛᴇᴄᴛ ᴄᴏɴᴛᴇɴᴛ ɪꜱ ᴀʟʀᴇᴀᴅʏ ᴏɴ!", show_alert=True)
        await set_protect_status(True)
        await query.answer("✅ ᴘʀᴏᴛᴇᴄᴛ ᴄᴏɴᴛᴇɴᴛ ᴇɴᴀʙʟᴇᴅ!", show_alert=True)
        return await safe_edit(query.message, "🔒 <b>ᴘʀᴏᴛᴇᴄᴛ ᴄᴏɴᴛᴇɴᴛ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ</b>\n\nᴄᴜʀʀᴇɴᴛ ꜱᴛᴀᴛᴜꜱ: <b>ᴏɴ ✅</b>", InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ ᴇɴᴀʙʟᴇ", callback_data="protect_on"), 
                InlineKeyboardButton("❌ ᴅɪꜱᴀʙʟᴇ", callback_data="protect_off")
            ], 
            [
                InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="settings")
            ]
        ]))

    elif data == "protect_off":
        if not await get_protect_status():
            return await query.answer("⚠️ ᴘʀᴏᴛᴇᴄᴛ ᴄᴏɴᴛᴇɴᴛ ɪꜱ ᴀʟʀᴇᴀᴅʏ ᴏꜰꜰ!", show_alert=True)
        await set_protect_status(False)
        await query.answer("❌ ᴘʀᴏᴛᴇᴄᴛ ᴄᴏɴᴛᴇɴᴛ ᴅɪꜱᴀʙʟᴇᴅ!", show_alert=True)
        return await safe_edit(query.message, "🔒 <b>ᴘʀᴏᴛᴇᴄᴛ ᴄᴏɴᴛᴇɴᴛ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ</b>\n\nᴄᴜʀʀᴇɴᴛ ꜱᴛᴀᴛᴜꜱ: <b>ᴏꜰꜰ ❌</b>", InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ ᴇɴᴀʙʟᴇ", callback_data="protect_on"), 
                InlineKeyboardButton("❌ ᴅɪꜱᴀʙʟᴇ", callback_data="protect_off")
            ], 
            [
                InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="settings")
            ]
        ]))
        
