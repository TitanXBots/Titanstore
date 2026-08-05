from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from helper_func import safe_edit
from database.database import (
    is_admin, get_protect_status, set_protect_status, 
    get_force_sub_status, set_force_sub_status,
    get_file_again_status, set_file_again_status
)

@Client.on_callback_query(filters.regex("^(settings|protect_menu|protect_on|protect_off|forcesub_menu|forcesub_on|forcesub_off|getfileagain_menu|getfileagain_on|getfileagain_off)$"))
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
                InlineKeyboardButton("🔒 ᴘʀᴏᴛᴇᴄᴛ ᴄᴏɴᴛᴇɴᴛ", callback_data="protect_menu"),
                InlineKeyboardButton("📢 ꜰᴏʀᴄᴇ ꜱᴜʙ", callback_data="forcesub_menu")
            ],
            [
                InlineKeyboardButton("♻️ ɢᴇᴛ ꜰɪʟᴇ ᴀɢᴀɪɴ", callback_data="getfileagain_menu")
            ],
            [
                InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="start")
            ]
        ]))

    # --- PROTECT CONTENT MENU ---
    elif data == "protect_menu":
        is_on = await get_protect_status()
        status = "ᴏɴ ✅" if is_on else "ᴏꜰꜰ ❌"
        return await safe_edit(query.message, f"🔒 <b>ᴘʀᴏᴛᴇᴄᴛ ᴄᴏɴᴛᴇɴᴛ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ</b>\n\nᴘʀᴇᴠᴇɴᴛꜱ ᴜꜱᴇʀꜱ ꜰʀᴏᴍ ꜰᴏʀᴡᴀʀᴅɪɴɢ, ꜱᴀᴠɪɴɢ, ᴏʀ ᴄᴏᴘʏɪɴɢ ꜰɪʟᴇꜱ.\n\nᴄᴜʀʀᴇɴᴛ ꜱᴛᴀᴛᴜꜱ: <b>{status}</b>", InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ ᴇɴᴀʙʟᴇ", callback_data="protect_on"), 
                InlineKeyboardButton("❌ ᴅɪꜱᴀʙʟᴇ", callback_data="protect_off")
            ],
            [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="settings")]
        ]))

    elif data == "protect_on":
        if await get_protect_status():
            return await query.answer("⚠️ ᴘʀᴏᴛᴇᴄᴛ ᴄᴏɴᴛᴇɴᴛ ɪꜱ ᴀʟʀᴇᴀᴅʏ ᴏɴ!", show_alert=True)
        await set_protect_status(True)
        await query.answer("✅ ᴘʀᴏᴛᴇᴄᴛ ᴄᴏɴᴛᴇɴᴛ ᴇɴᴀʙʟᴇᴅ!", show_alert=True)
        return await safe_edit(query.message, "🔒 <b>ᴘʀᴏᴛᴇᴄᴛ ᴄᴏɴᴛᴇɴᴛ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ</b>\n\nᴄᴜʀʀᴇɴᴛ ꜱᴛᴀᴛᴜꜱ: <b>ᴏɴ ✅</b>", InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ ᴇɴᴀʙʟᴇ", callback_data="protect_on"), InlineKeyboardButton("❌ ᴅɪꜱᴀʙʟᴇ", callback_data="protect_off")], 
            [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="settings")]
        ]))

    elif data == "protect_off":
        if not await get_protect_status():
            return await query.answer("⚠️ ᴘʀᴏᴛᴇᴄᴛ ᴄᴏɴᴛᴇɴᴛ ɪꜱ ᴀʟʀᴇᴀᴅʏ ᴏꜰꜰ!", show_alert=True)
        await set_protect_status(False)
        await query.answer("❌ ᴘʀᴏᴛᴇᴄᴛ ᴄᴏɴᴛᴇɴᴛ ᴅɪꜱᴀʙʟᴇᴅ!", show_alert=True)
        return await safe_edit(query.message, "🔒 <b>ᴘʀᴏᴛᴇᴄᴛ ᴄᴏɴᴛᴇɴᴛ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ</b>\n\nᴄᴜʀʀᴇɴᴛ ꜱᴛᴀᴛᴜꜱ: <b>ᴏꜰꜰ ❌</b>", InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ ᴇɴᴀʙʟᴇ", callback_data="protect_on"), InlineKeyboardButton("❌ ᴅɪꜱᴀʙʟᴇ", callback_data="protect_off")], 
            [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="settings")]
        ]))

    # --- FORCE SUB MENU ---
    elif data == "forcesub_menu":
        is_on = await get_force_sub_status()
        status = "ᴏɴ ✅" if is_on else "ᴏꜰꜰ ❌"
        return await safe_edit(query.message, f"📢 <b>ꜰᴏʀᴄᴇ ꜱᴜʙ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ</b>\n\nFᴏʀᴄᴇ ᴜꜱᴇʀꜱ ᴛᴏ ᴊᴏɪɴ ʏᴏᴜʀ ᴄʜᴀɴɴᴇʟꜱ ʙᴇꜰᴏʀᴇ ᴜꜱɪɴɢ ᴛʜᴇ ʙᴏᴛ.\n\nᴄᴜʀʀᴇɴᴛ ꜱᴛᴀᴛᴜꜱ: <b>{status}</b>", InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ ᴇɴᴀʙʟᴇ", callback_data="forcesub_on"), 
                InlineKeyboardButton("❌ ᴅɪꜱᴀʙʟᴇ", callback_data="forcesub_off")
            ],
            [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="settings")]
        ]))

    elif data == "forcesub_on":
        if await get_force_sub_status():
            return await query.answer("⚠️ ꜰᴏʀᴄᴇ ꜱᴜʙ ɪꜱ ᴀʟʀᴇᴀᴅʏ ᴏɴ!", show_alert=True)
        await set_force_sub_status(True)
        await query.answer("✅ ꜰᴏʀᴄᴇ ꜱᴜʙ ᴇɴᴀʙʟᴇᴅ!", show_alert=True)
        return await safe_edit(query.message, "📢 <b>ꜰᴏʀᴄᴇ ꜱᴜʙ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ</b>\n\nᴄᴜʀʀᴇɴᴛ ꜱᴛᴀᴛᴜꜱ: <b>ᴏɴ ✅</b>", InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ ᴇɴᴀʙʟᴇ", callback_data="forcesub_on"), InlineKeyboardButton("❌ ᴅɪꜱᴀʙʟᴇ", callback_data="forcesub_off")], 
            [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="settings")]
        ]))

    elif data == "forcesub_off":
        if not await get_force_sub_status():
            return await query.answer("⚠️ ꜰᴏʀᴄᴇ ꜱᴜʙ ɪꜱ ᴀʟʀᴇᴀᴅʏ ᴏꜰꜰ!", show_alert=True)
        await set_force_sub_status(False)
        await query.answer("❌ ꜰᴏʀᴄᴇ ꜱᴜʙ ᴅɪꜱᴀʙʟᴇᴅ!", show_alert=True)
        return await safe_edit(query.message, "📢 <b>ꜰᴏʀᴄᴇ ꜱᴜʙ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ</b>\n\nᴄᴜʀʀᴇɴᴛ ꜱᴛᴀᴛᴜꜱ: <b>ᴏꜰꜰ ❌</b>", InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ ᴇɴᴀʙʟᴇ", callback_data="forcesub_on"), InlineKeyboardButton("❌ ᴅɪꜱᴀʙʟᴇ", callback_data="forcesub_off")], 
            [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="settings")]
        ]))

    # --- GET FILE AGAIN MENU ---
    elif data == "getfileagain_menu":
        is_on = await get_file_again_status()
        status = "ᴏɴ ✅" if is_on else "ᴏꜰꜰ ❌"
        return await safe_edit(query.message, f"♻️ <b>ɢᴇᴛ ꜰɪʟᴇ ᴀɢᴀɪɴ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ</b>\n\nꜱʜᴏᴡ 'ɢᴇᴛ ꜰɪʟᴇ ᴀɢᴀɪɴ' ʙᴜᴛᴛᴏɴ ᴀꜰᴛᴇʀ ꜰɪʟᴇ ᴀᴜᴛᴏ-ᴅᴇʟᴇᴛɪᴏɴ.\n\nᴄᴜʀʀᴇɴᴛ ꜱᴛᴀᴛᴜꜱ: <b>{status}</b>", InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ ᴇɴᴀʙʟᴇ", callback_data="getfileagain_on"), 
                InlineKeyboardButton("❌ ᴅɪꜱᴀʙʟᴇ", callback_data="getfileagain_off")
            ],
            [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="settings")]
        ]))

    elif data == "getfileagain_on":
        if await get_file_again_status():
            return await query.answer("⚠️ ɢᴇᴛ ꜰɪʟᴇ ᴀɢᴀɪɴ ɪꜱ ᴀʟʀᴇᴀᴅʏ ᴏɴ!", show_alert=True)
        await set_file_again_status(True)
        await query.answer("✅ ɢᴇᴛ ꜰɪʟᴇ ᴀɢᴀɪɴ ᴇɴᴀʙʟᴇᴅ!", show_alert=True)
        return await safe_edit(query.message, "♻️ <b>ɢᴇᴛ ꜰɪʟᴇ ᴀɢᴀɪɴ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ</b>\n\nᴄᴜʀʀᴇɴᴛ ꜱᴛᴀᴛᴜꜱ: <b>ᴏɴ ✅</b>", InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ ᴇɴᴀʙʟᴇ", callback_data="getfileagain_on"), InlineKeyboardButton("❌ ᴅɪꜱᴀʙʟᴇ", callback_data="getfileagain_off")], 
            [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="settings")]
        ]))

    elif data == "getfileagain_off":
        if not await get_file_again_status():
            return await query.answer("⚠️ ɢᴇᴛ ꜰɪʟᴇ ᴀɢᴀɪɴ ɪꜱ ᴀʟʀᴇᴀᴅʏ ᴏꜰꜰ!", show_alert=True)
        await set_file_again_status(False)
        await query.answer("❌ ɢᴇᴛ ꜰɪʟᴇ ᴀɢᴀɪɴ ᴅɪꜱᴀʙʟᴇᴅ!", show_alert=True)
        return await safe_edit(query.message, "♻️ <b>ɢᴇᴛ ꜰɪʟᴇ ᴀɢᴀɪɴ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ</b>\n\nᴄᴜʀʀᴇɴᴛ ꜱᴛᴀᴛᴜꜱ: <b>ᴏꜰꜰ ❌</b>", InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ ᴇɴᴀʙʟᴇ", callback_data="getfileagain_on"), InlineKeyboardButton("❌ ᴅɪꜱᴀʙʟᴇ", callback_data="getfileagain_off")], 
            [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="settings")]
        ]))
        
