import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyromod.exceptions import ListenerTimeout
from config import LOG_CHANNEL_ID
from helper_func import safe_edit
from database.database import is_premium, is_admin, save_tenant_request, update_tenant_status

@Client.on_callback_query(filters.regex(r"^user_connect_req$"))
async def request_custom_channels_cb(client: Client, query: CallbackQuery):
    user_id = query.from_user.id
    
    if not await is_premium(user_id):
        return await query.answer("⚠️ ᴏɴʟʏ ᴘʀᴇᴍɪᴜᴍ ᴍᴇᴍʙᴇʀꜱ ᴄᴀɴ ᴅᴏ ᴛʜɪꜱ!", show_alert=True)

    back_keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 ᴄᴀɴᴄᴇʟ", callback_data="settings")]])
    
    notice_text = (
        "<b>⚠️ ɪᴍᴘᴏʀᴛᴀɴᴛ ɴᴏᴛɪᴄᴇ:</b>\n\n"
        "1. Yᴏᴜ ᴍᴜꜱᴛ ᴀᴅᴅ ᴛʜɪꜱ ʙᴏᴛ ᴀꜱ ᴀɴ <b>Aᴅᴍɪɴ</b> ɪɴ ʏᴏᴜʀ ᴅᴀᴛᴀʙᴀꜱᴇ ᴄʜᴀɴɴᴇʟ ᴀɴᴅ ꜰᴏʀᴄᴇ-ꜱᴜʙ ᴄʜᴀɴɴᴇʟꜱ ʙᴇꜰᴏʀᴇ ᴄᴏɴᴛɪɴᴜɪɴɢ.\n"
        "2. Tʜᴇ ʙᴏᴛ ɴᴇᴇᴅꜱ 'ɪɴᴠɪᴛᴇ ᴜꜱᴇʀꜱ' ᴀɴᴅ 'ᴘᴏꜱᴛ ᴍᴇꜱꜱᴀɢᴇꜱ' ʀɪɢʜᴛꜱ.\n\n"
        "📤 <b>ꜱᴇɴᴅ ʏᴏᴜʀ ᴅᴀᴛᴀʙᴀꜱᴇ ᴄʜᴀɴɴᴇʟ ɪᴅ:</b>\n"
        "(Iᴛ ᴍᴜꜱᴛ ꜱᴛᴀʀᴛ ᴡɪᴛʜ -100)\n\n"
        "/cancel - ᴛᴏ ꜱᴛᴏᴘ ᴘʀᴏᴄᴇꜱꜱ."
    )
    await safe_edit(query.message, notice_text, back_keyboard)
    
    try:
        db_prompt = await client.listen(query.message.chat.id, timeout=120)
    except ListenerTimeout:
        return await safe_edit(query.message, "⌛ ᴛɪᴍᴇᴏᴜᴛ!", back_keyboard)
        
    text = db_prompt.text or ""
    if not text or text.lower() == "/cancel":
        try: await db_prompt.delete()
        except: pass
        return await safe_edit(query.message, "❌ ᴄᴀɴᴄᴇʟʟᴇᴅ.", back_keyboard)
    
    try: db_channel = int(text)
    except: 
        try: await db_prompt.delete()
        except: pass
        return await safe_edit(query.message, "❌ Iɴᴠᴀʟɪᴅ ID. Mᴜꜱᴛ ʙᴇ ᴀ ɴᴜᴍʙᴇʀ ꜱᴛᴀʀᴛɪɴɢ ᴡɪᴛʜ -100.", back_keyboard)

    try: await db_prompt.delete()
    except: pass

    fs_prompt_text = (
        "📤 <b>ꜱᴇɴᴅ ʏᴏᴜʀ ꜰᴏʀᴄᴇ ꜱᴜʙ ᴄʜᴀɴɴᴇʟ ɪᴅꜱ:</b>\n"
        "Sᴇᴘᴀʀᴀᴛᴇ ᴍᴜʟᴛɪᴘʟᴇ ɪᴅꜱ ᴡɪᴛʜ ᴀ ꜱᴘᴀᴄᴇ. (Iꜰ ɴᴏɴᴇ, ꜱᴇɴᴅ 0)\n\n"
        "/cancel - ᴛᴏ ꜱᴛᴏᴘ ᴘʀᴏᴄᴇꜱꜱ."
    )
    await safe_edit(query.message, fs_prompt_text, back_keyboard)

    try:
        fs_prompt = await client.listen(query.message.chat.id, timeout=120)
    except ListenerTimeout:
        return await safe_edit(query.message, "⌛ ᴛɪᴍᴇᴏᴜᴛ!", back_keyboard)

    text_fs = fs_prompt.text or ""
    if not text_fs or text_fs.lower() == "/cancel":
        try: await fs_prompt.delete()
        except: pass
        return await safe_edit(query.message, "❌ ᴄᴀɴᴄᴇʟʟᴇᴅ.", back_keyboard)
    
    fs_channels = []
    if text_fs.strip() != "0":
        for ch in text_fs.split():
            try: fs_channels.append(int(ch))
            except: pass

    try: await fs_prompt.delete()
    except: pass

    await save_tenant_request(user_id, db_channel, fs_channels)
    
    success_text = (
        "✅ <b>ʀᴇQᴜᴇꜱᴛ ꜱᴜʙᴍɪᴛᴛᴇᴅ!</b>\n\n"
        "Pʟᴇᴀꜱᴇ ᴡᴀɪᴛ ꜰᴏʀ ᴀɴ ᴀᴅᴍɪɴ ᴛᴏ ᴀᴘᴘʀᴏᴠᴇ ʏᴏᴜʀ ᴄʜᴀɴɴᴇʟꜱ. Yᴏᴜ ᴡɪʟʟ ʙᴇ ɴᴏᴛɪꜰɪᴇᴅ ʜᴇʀᴇ."
    )
    await safe_edit(query.message, success_text, InlineKeyboardMarkup([[InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="settings")]]))

    admin_markup = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ ᴀᴘᴘʀᴏᴠᴇ", callback_data=f"req_approve_{user_id}"),
            InlineKeyboardButton("❌ ʀᴇᴊᴇᴄᴛ", callback_data=f"req_reject_{user_id}")
        ]
    ])
    
    admin_notice = (
        f"<b>🔔 ɴᴇᴡ ᴄᴜꜱᴛᴏᴍ ᴄʜᴀɴɴᴇʟ ʀᴇQᴜᴇꜱᴛ</b>\n\n"
        f"<b>Uꜱᴇʀ:</b> {query.from_user.mention} (<code>{user_id}</code>)\n"
        f"<b>DB Cʜᴀɴɴᴇʟ:</b> <code>{db_channel}</code>\n"
        f"<b>FS Cʜᴀɴɴᴇʟꜱ:</b> <code>{fs_channels}</code>"
    )
    await client.send_message(LOG_CHANNEL_ID, admin_notice, reply_markup=admin_markup)

@Client.on_callback_query(filters.regex(r"^req_"))
async def handle_tenant_request(client: Client, query: CallbackQuery):
    if not await is_admin(query.from_user.id): return await query.answer("⚠️ ᴀᴄᴄᴇꜱꜱ ᴅᴇɴɪᴇᴅ!", show_alert=True)
    
    action, user_id = query.data.split("_")[1], int(query.data.split("_")[2])
    
    if action == "approve":
        await update_tenant_status(user_id, "approved")
        await query.message.edit_reply_markup(InlineKeyboardMarkup([[InlineKeyboardButton("✅ ᴀᴘᴘʀᴏᴠᴇᴅ", callback_data="none")]]))
        try: 
            await client.send_message(user_id, "🎉 <b>Cᴏɴɢʀᴀᴛᴜʟᴀᴛɪᴏɴꜱ!</b>\n\nYᴏᴜʀ ᴄᴜꜱᴛᴏᴍ ᴄʜᴀɴɴᴇʟ ꜱᴇᴛᴜᴘ ʜᴀꜱ ʙᴇᴇɴ ᴀᴘᴘʀᴏᴠᴇᴅ! Yᴏᴜ ᴄᴀɴ ɴᴏᴡ ᴜꜱᴇ /batch ᴀɴᴅ /genlink ᴡɪᴛʜ ʏᴏᴜʀ ᴏᴡɴ ᴅᴀᴛᴀʙᴀꜱᴇ ᴄʜᴀɴɴᴇʟ.")
        except: pass
    
    elif action == "reject":
        await update_tenant_status(user_id, "rejected")
        await query.message.edit_reply_markup(InlineKeyboardMarkup([[InlineKeyboardButton("❌ ʀᴇᴊᴇᴄᴛᴇᴅ", callback_data="none")]]))
        try: 
            await client.send_message(user_id, "❌ <b>RᴇQᴜᴇꜱᴛ Rᴇᴊᴇᴄᴛᴇᴅ</b>\n\nYᴏᴜʀ ᴄᴜꜱᴛᴏᴍ ᴄʜᴀɴɴᴇʟ ꜱᴇᴛᴜᴘ ᴡᴀꜱ ᴅᴇᴄʟɪɴᴇᴅ ʙʏ ᴀɴ ᴀᴅᴍɪɴ. Eɴꜱᴜʀᴇ ᴛʜᴇ ʙᴏᴛ ɪꜱ ᴀɴ ᴀᴅᴍɪɴ ɪɴ ʏᴏᴜʀ ᴄʜᴀɴɴᴇʟꜱ ᴀɴᴅ ᴛʀʏ ᴀɢᴀɪɴ ʟᴀᴛᴇʀ.")
        except: pass
            
