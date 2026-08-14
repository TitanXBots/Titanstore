import asyncio
from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from pyromod.exceptions import ListenerTimeout
from config import OWNER_ID
from helper_func import safe_edit, send_cancel_msg
from database.database import is_admin, add_admin, remove_admin, get_admins

def get_admin_menu():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("➕ ᴀᴅᴅ ᴀᴅᴍɪɴ", callback_data="admin_add"), 
            InlineKeyboardButton("➖ ʀᴇᴍᴏᴠᴇ ᴀᴅᴍɪɴ", callback_data="admin_remove")
        ],
        [
            InlineKeyboardButton("📋 ᴀᴅᴍɪɴ ʟɪꜱᴛ", callback_data="admin_list")
        ],
        [
            InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="admin_panel")
        ]
    ])

@Client.on_callback_query(filters.regex(r"^admin_(menu|add|remove|list)$"))
async def admin_callbacks(client: Client, query: CallbackQuery):
    try: await query.answer()
    except: pass
    if not await is_admin(query.from_user.id): 
        try: await query.answer("⚠️ ᴀᴄᴄᴇꜱꜱ ᴅᴇɴɪᴇᴅ: ᴀᴅᴍɪɴ ᴍᴇɴᴜ ɪꜱ ʀᴇꜱᴛʀɪᴄᴛᴇᴅ!", show_alert=True)
        except: pass
        return
    
    data = query.data

    if data == "admin_menu":
        return await safe_edit(query.message, "👨‍💻 <b>ᴀᴅᴍɪɴ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ</b>", get_admin_menu())

    elif data == "admin_add":
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="admin_menu")]])
        await safe_edit(query.message, "👨‍💻 <b>ᴀᴅᴅ ᴀᴅᴍɪɴ</b>\n\nꜱᴇɴᴅ ᴜꜱᴇʀ_ɪᴅ ᴛᴏ ᴀᴅᴅ ᴀꜱ ᴀᴅᴍɪɴ\n\n/cancel - ᴄᴀɴᴄᴇʟ.", keyboard)
        try:
            input_msg = await client.listen(query.message.chat.id, timeout=60)
        except ListenerTimeout:
            return await safe_edit(query.message, "⌛ ᴛɪᴍᴇᴏᴜᴛ!\n\n👨‍💻 <b>ᴀᴅᴍɪɴ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ</b>", get_admin_menu())
            
        text = input_msg.text or ""
        try: await input_msg.delete()
        except: pass
        
        if not text or text.lower() == "/cancel":
            await send_cancel_msg(client, query.message.chat.id)
            return await safe_edit(query.message, "👨‍💻 <b>ᴀᴅᴍɪɴ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ</b>", get_admin_menu())
            
        if not text.isdigit(): 
            return await safe_edit(query.message, "❌ <b>ɪɴᴠᴀʟɪᴅ ɪᴅ!</b>\n\nᴘʟᴇᴀꜱᴇ ꜱᴇɴᴅ ᴀ ᴠᴀʟɪᴅ ᴜꜱᴇʀ ɪᴅ.", keyboard)
            
        uid = int(text)
        if uid == int(OWNER_ID): 
            return await safe_edit(query.message, "⚠️ <b>ᴏᴡɴᴇʀ ɪꜱ ᴀʟʀᴇᴀᴅʏ ᴀᴅᴍɪɴ!</b>", keyboard)
            
        await add_admin(uid)
        return await safe_edit(query.message, f"✅ <b>ꜱᴜᴄᴄᴇꜱꜱ!</b>\n\nᴜꜱᴇʀ <code>{uid}</code> ʜᴀꜱ ʙᴇᴇɴ ᴀᴅᴅᴇᴅ ᴀꜱ ᴀᴅᴍɪɴ.", get_admin_menu())

    elif data == "admin_remove":
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="admin_menu")]])
        await safe_edit(query.message, "👨‍💻 <b>ʀᴇᴍᴏᴠᴇ ᴀᴅᴍɪɴ</b>\n\nꜱᴇɴᴅ ᴜꜱᴇʀ_ɪᴅ ᴛᴏ ʀᴇᴍᴏᴠᴇ ꜰʀᴏᴍ ᴀᴅᴍɪɴ\n\n/cancel - ᴄᴀɴᴄᴇʟ.", keyboard)
        try:
            input_msg = await client.listen(query.message.chat.id, timeout=60)
        except ListenerTimeout:
            return await safe_edit(query.message, "⌛ ᴛɪᴍᴇᴏᴜᴛ!\n\n👨‍💻 <b>ᴀᴅᴍɪɴ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ</b>", get_admin_menu())
            
        text = input_msg.text or ""
        try: await input_msg.delete()
        except: pass
        
        if not text or text.lower() == "/cancel":
            await send_cancel_msg(client, query.message.chat.id)
            return await safe_edit(query.message, "👨‍💻 <b>ᴀᴅᴍɪɴ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ</b>", get_admin_menu())
            
        if not text.isdigit(): 
            return await safe_edit(query.message, "❌ <b>ɪɴᴠᴀʟɪᴅ ɪᴅ!</b>\n\nᴘʟᴇᴀꜱᴇ ꜱᴇɴᴅ ᴀ ᴠᴀʟɪᴅ ᴜꜱᴇʀ ɪᴅ.", keyboard)
            
        uid = int(text)
        if uid == int(OWNER_ID): 
            return await safe_edit(query.message, "❌ <b>ᴄᴀɴɴᴏᴛ ʀᴇᴍᴏᴠᴇ ᴏᴡɴᴇʀ!</b>", keyboard)
            
        await remove_admin(uid)
        return await safe_edit(query.message, f"✅ <b>ꜱᴜᴄᴄᴇꜱꜱ!</b>\n\nᴜꜱᴇʀ <code>{uid}</code> ʜᴀꜱ ʙᴇᴇɴ ʀᴇᴍᴏᴠᴇᴅ ꜰʀᴏᴍ ᴀᴅᴍɪɴꜱ.", get_admin_menu())

    elif data == "admin_list":
        admins = await get_admins()
        if not admins: return await safe_edit(query.message, "ɴᴏ ᴀᴅᴍɪɴꜱ ꜰᴏᴜɴᴅ.", InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="admin_menu")]
        ]))
        text = "\n".join([f"• <code>{a}</code>" for a in admins[:100]])
        return await safe_edit(query.message, f"👨‍💻 <b>ᴀᴅᴍɪɴ ʟɪꜱᴛ:</b>\n\n{text}", InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="admin_menu")]
        ]))
        
