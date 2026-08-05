import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyromod.exceptions import ListenerTimeout
from config import LOG_CHANNEL_ID
from database.database import is_premium, is_admin, save_tenant_request, update_tenant_status

@Client.on_message(filters.command("connect") & filters.private)
async def request_custom_channels(client: Client, message: Message):
    user_id = message.from_user.id
    
    if not await is_premium(user_id):
        return await message.reply_text("⚠️ <b>ᴀᴄᴄᴇꜱꜱ ᴅᴇɴɪᴇᴅ:</b> ᴏɴʟʏ ᴘʀᴇᴍɪᴜᴍ ᴍᴇᴍʙᴇʀꜱ ᴄᴀɴ ʀᴇQᴜᴇꜱᴛ ᴄᴜꜱᴛᴏᴍ ᴄʜᴀɴɴᴇʟꜱ.")

    await message.reply_text("<b>⚠️ ɪᴍᴘᴏʀᴛᴀɴᴛ ɴᴏᴛɪᴄᴇ:</b>\n\n1. Yᴏᴜ ᴍᴜꜱᴛ ᴀᴅᴅ ᴛʜɪꜱ ʙᴏᴛ ᴀꜱ ᴀɴ <b>Aᴅᴍɪɴ</b> ɪɴ Yᴏᴜʀ ᴅᴀᴛᴀʙᴀꜱᴇ ᴄʜᴀɴɴᴇʟ ᴀɴᴅ ꜰᴏʀᴄᴇ-ꜱᴜʙ ᴄʜᴀɴɴᴇʟꜱ ʙᴇꜰᴏʀᴇ ᴄᴏɴᴛɪɴᴜɪɴɢ.\n2. Tʜᴇ ʙᴏᴛ ɴᴇᴇᴅꜱ 'ɪɴᴠɪᴛᴇ ᴜꜱᴇʀꜱ' ᴀɴᴅ 'ᴘᴏꜱᴛ ᴍᴇꜱꜱᴀɢᴇꜱ' ʀɪɢʜᴛꜱ.")
    
    try:
        db_prompt = await client.ask(user_id, "📤 <b>ꜱᴇɴᴅ ʏᴏᴜʀ ᴅᴀᴛᴀʙᴀꜱᴇ ᴄʜᴀɴɴᴇʟ ɪᴅ:</b>\n(Iᴛ ᴍᴜꜱᴛ ꜱᴛᴀʀᴛ ᴡɪᴛʜ -100)\n\nSᴇɴᴅ /cancel ᴛᴏ ꜱᴛᴏᴘ.", timeout=120)
    except ListenerTimeout:
        return await message.reply_text("⌛ ᴛɪᴍᴇᴏᴜᴛ!")
        
    if db_prompt.text.lower() == "/cancel": return await message.reply_text("❌ ᴄᴀɴᴄᴇʟʟᴇᴅ.")
    
    try: db_channel = int(db_prompt.text)
    except: return await message.reply_text("❌ Iɴᴠᴀʟɪᴅ ID. Mᴜꜱᴛ ʙᴇ ᴀ ɴᴜᴍʙᴇʀ ꜱᴛᴀʀᴛɪɴɢ ᴡɪᴛʜ -100.")

    try:
        fs_prompt = await client.ask(user_id, "📤 <b>ꜱᴇɴᴅ ʏᴏᴜʀ ꜰᴏʀᴄᴇ ꜱᴜʙ ᴄʜᴀɴɴᴇʟ ɪᴅꜱ:</b>\nSᴇᴘᴀʀᴀᴛᴇ ᴍᴜʟᴛɪᴘʟᴇ ɪᴅꜱ ᴡɪᴛʜ ᴀ ꜱᴘᴀᴄᴇ. (Iꜰ ɴᴏɴᴇ, ꜱᴇɴᴅ 0)\n\nSᴇɴᴅ /cancel ᴛᴏ ꜱᴛᴏᴘ.", timeout=120)
    except ListenerTimeout:
        return await message.reply_text("⌛ ᴛɪᴍᴇᴏᴜᴛ!")

    if fs_prompt.text.lower() == "/cancel": return await message.reply_text("❌ ᴄᴀɴᴄᴇʟʟᴇᴅ.")
    
    fs_channels = []
    if fs_prompt.text != "0":
        for ch in fs_prompt.text.split():
            try: fs_channels.append(int(ch))
            except: pass

    await save_tenant_request(user_id, db_channel, fs_channels)
    await message.reply_text("✅ <b>ʀᴇQᴜᴇꜱᴛ ꜱᴜʙᴍɪᴛᴛᴇᴅ!</b>\n\nPʟᴇᴀꜱᴇ ᴡᴀɪᴛ ꜰᴏʀ ᴀɴ ᴀᴅᴍɪɴ ᴛᴏ ᴀᴘᴘʀᴏᴠᴇ ʏᴏᴜʀ ᴄʜᴀɴɴᴇʟꜱ. Yᴏᴜ ᴡɪʟʟ ʙᴇ ɴᴏᴛɪꜰɪᴇᴅ ʜᴇʀᴇ.")

    admin_markup = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ ᴀᴘᴘʀᴏᴠᴇ", callback_data=f"req_approve_{user_id}"),
            InlineKeyboardButton("❌ ʀᴇᴊᴇᴄᴛ", callback_data=f"req_reject_{user_id}")
        ]
    ])
    await client.send_message(
        LOG_CHANNEL_ID,
        f"<b>🔔 ɴᴇᴡ ᴄᴜꜱᴛᴏᴍ ᴄʜᴀɴɴᴇʟ ʀᴇQᴜᴇꜱᴛ</b>\n\n<b>Uꜱᴇʀ:</b> {message.from_user.mention} (<code>{user_id}</code>)\n<b>DB Cʜᴀɴɴᴇʟ:</b> <code>{db_channel}</code>\n<b>FS Cʜᴀɴɴᴇʟꜱ:</b> <code>{fs_channels}</code>",
        reply_markup=admin_markup
    )

@Client.on_callback_query(filters.regex(r"^req_"))
async def handle_tenant_request(client: Client, query: CallbackQuery):
    if not await is_admin(query.from_user.id): return await query.answer("⚠️ ᴀᴄᴄᴇꜱꜱ ᴅᴇɴɪᴇᴅ!", show_alert=True)
    
    action, user_id = query.data.split("_")[1], int(query.data.split("_")[2])
    
    if action == "approve":
        await update_tenant_status(user_id, "approved")
        await query.message.edit_reply_markup(InlineKeyboardMarkup([[InlineKeyboardButton("✅ ᴀᴘᴘʀᴏᴠᴇᴅ", callback_data="none")]]))
        try: await client.send_message(user_id, "🎉 <b>Cᴏɴɢʀᴀᴛᴜʟᴀᴛɪᴏɴꜱ!</b>\n\nYᴏᴜʀ ᴄᴜꜱᴛᴏᴍ ᴄʜᴀɴɴᴇʟ ꜱᴇᴛᴜᴘ ʜᴀꜱ ʙᴇᴇɴ ᴀᴘᴘʀᴏᴠᴇᴅ! Yᴏᴜ ᴄᴀɴ ɴᴏᴡ ᴜꜱᴇ /batch ᴀɴᴅ /genlink ᴡɪᴛʜ ʏᴏᴜʀ ᴏᴡɴ ᴅᴀᴛᴀʙᴀꜱᴇ ᴄʜᴀɴɴᴇʟ.")
        except: pass
    
    elif action == "reject":
        await update_tenant_status(user_id, "rejected")
        await query.message.edit_reply_markup(InlineKeyboardMarkup([[InlineKeyboardButton("❌ ʀᴇᴊᴇᴄᴛᴇᴅ", callback_data="none")]]))
        try: await client.send_message(user_id, "❌ <b>RᴇQᴜᴇꜱᴛ Rᴇᴊᴇᴄᴛᴇᴅ</b>\n\nYᴏᴜʀ ᴄᴜꜱᴛᴏᴍ ᴄʜᴀɴɴᴇʟ ꜱᴇᴛᴜᴘ ᴡᴀꜱ ᴅᴇᴄʟɪɴᴇᴅ ʙʏ ᴀɴ ᴀᴅᴍɪɴ. Eɴꜱᴜʀᴇ ᴛʜᴇ ʙᴏᴛ ɪꜱ ᴀɴ ᴀᴅᴍɪɴ ɪɴ ʏᴏᴜʀ ᴄʜᴀɴɴᴇʟꜱ ᴀɴᴅ ᴛʀʏ ᴀɢᴀɪɴ ʟᴀᴛᴇʀ.")
        except: pass
          
