import asyncio
from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from pyromod.exceptions import ListenerTimeout
from helper_func import safe_edit
from database.database import is_admin, ban_user, unban_user, get_banned_users, is_user_banned

def get_ban_menu():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🚫 ʙᴀɴ ᴜꜱᴇʀ", callback_data="ban_user"), 
            InlineKeyboardButton("✅ ᴜɴʙᴀɴ ᴜꜱᴇʀ", callback_data="ban_unban_user")
        ],
        [
            InlineKeyboardButton("📄 ʙᴀɴɴᴇᴅ ʟɪꜱᴛ", callback_data="ban_list")
        ],
        [
            InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="admin_panel")
        ]
    ])

@Client.on_callback_query(filters.regex(r"^ban_(menu|user|unban_user|list)$"))
async def ban_callbacks(client: Client, query: CallbackQuery):
    try: await query.answer()
    except: pass
    if not await is_admin(query.from_user.id): 
        try: await query.answer("⚠️ ᴀᴄᴄᴇꜱꜱ ᴅᴇɴɪᴇᴅ: ʙᴀɴ ᴍᴇɴᴜ ɪꜱ ʀᴇꜱᴛʀɪᴄᴛᴇᴅ!", show_alert=True)
        except: pass
        return
    
    data = query.data

    if data == "ban_menu":
        return await safe_edit(query.message, "🚫 <b>ʙᴀɴ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ</b>", get_ban_menu())

    elif data == "ban_user":
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="ban_menu")]])
        await safe_edit(query.message, "🚫 <b>ʙᴀɴ ᴜꜱᴇʀ</b>\n\nꜱᴇɴᴅ ᴜꜱᴇʀ_ɪᴅ [ʀᴇᴀꜱᴏɴ]\n\n/cancel - ᴄᴀɴᴄᴇʟ.", keyboard)
        try:
            input_msg = await client.listen(query.message.chat.id, timeout=60)
        except ListenerTimeout:
            return await safe_edit(query.message, "⌛ ᴛɪᴍᴇᴏᴜᴛ!\n\n🚫 <b>ʙᴀɴ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ</b>", get_ban_menu())
            
        text = input_msg.text or ""
        try: await input_msg.delete()
        except: pass
        
        if not text or text.lower() == "/cancel":
            return await safe_edit(query.message, "❌ <b>ᴘʀᴏᴄᴇꜱꜱ ᴄᴀɴᴄᴇʟʟᴇᴅ!</b>\n\n🚫 <b>ʙᴀɴ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ</b>", get_ban_menu())
            
        parts = text.split(maxsplit=1)
        if not parts[0].isdigit(): 
            return await safe_edit(query.message, "❌ <b>ɪɴᴠᴀʟɪᴅ ɪᴅ!</b>\n\nᴘʟᴇᴀꜱᴇ ꜱᴇɴᴅ ᴀ ᴠᴀʟɪᴅ ᴜꜱᴇʀ ɪᴅ.", keyboard)
            
        uid = int(parts[0])
        if await is_user_banned(uid):
            return await safe_edit(query.message, f"⚠️ <b>ᴜꜱᴇʀ <code>{uid}</code> ɪꜱ ᴀʟʀᴇᴀᴅʏ ʙᴀɴɴᴇᴅ!</b>", get_ban_menu())

        reason = parts[1] if len(parts) > 1 else "ɴᴏ ʀᴇᴀꜱᴏɴ"
        await ban_user(uid, reason)
        return await safe_edit(query.message, f"✅ <b>ᴜꜱᴇʀ <code>{uid}</code> ʙᴀɴɴᴇᴅ!</b>\n\nʀᴇᴀꜱᴏɴ: <code>{reason}</code>", get_ban_menu())

    elif data == "ban_unban_user":
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="ban_menu")]])
        await safe_edit(query.message, "✅ <b>ᴜɴʙᴀɴ ᴜꜱᴇʀ</b>\n\nꜱᴇɴᴅ ᴜꜱᴇʀ_ɪᴅ\n\n/cancel - ᴄᴀɴᴄᴇʟ.", keyboard)
        try:
            input_msg = await client.listen(query.message.chat.id, timeout=60)
        except ListenerTimeout:
            return await safe_edit(query.message, "⌛ ᴛɪᴍᴇᴏᴜᴛ!\n\n🚫 <b>ʙᴀɴ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ</b>", get_ban_menu())
            
        text = input_msg.text or ""
        try: await input_msg.delete()
        except: pass
        
        if not text or text.lower() == "/cancel":
            return await safe_edit(query.message, "❌ <b>ᴘʀᴏᴄᴇꜱꜱ ᴄᴀɴᴄᴇʟʟᴇᴅ!</b>\n\n🚫 <b>ʙᴀɴ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ</b>", get_ban_menu())
            
        if not text.isdigit(): 
            return await safe_edit(query.message, "❌ <b>ɪɴᴠᴀʟɪᴅ ɪᴅ!</b>\n\nᴘʟᴇᴀꜱᴇ ꜱᴇɴᴅ ᴀ ᴠᴀʟɪᴅ ᴜꜱᴇʀ ɪᴅ.", keyboard)
            
        uid = int(text)
        if not await is_user_banned(uid):
            return await safe_edit(query.message, f"⚠️ <b>ᴜꜱᴇʀ <code>{uid}</code> ɪꜱ ɴᴏᴛ ʙᴀɴɴᴇᴅ!</b>", get_ban_menu())

        await unban_user(uid)
        return await safe_edit(query.message, f"✅ <b>ᴜꜱᴇʀ <code>{uid}</code> ᴜɴʙᴀɴɴᴇᴅ!</b>", get_ban_menu())

    elif data == "ban_list":
        banned = await get_banned_users()
        if not banned: return await safe_edit(query.message, "ɴᴏ ʙᴀɴɴᴇᴅ ᴜꜱᴇʀꜱ ꜰᴏᴜɴᴅ.", InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="ban_menu")]
        ]))
        text = "\n".join([f"• <code>{u['_id']}</code> - {u.get('reason','ɴᴏ ʀᴇᴀꜱᴏɴ')}" for u in banned[:100]])
        return await safe_edit(query.message, f"🚫 <b>ʙᴀɴɴᴇᴅ ᴜꜱᴇʀꜱ:</b>\n\n{text}", InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="ban_menu")]
        ]))
        
