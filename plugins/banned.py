import asyncio
from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from config import START_PIC
from helper_func import safe_edit, get_user_input
from database.database import is_admin, ban_user, unban_user, get_banned_users

async def delayed_delete(message, delay=7):
    await asyncio.sleep(delay)
    try: await message.delete()
    except: pass

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
    await query.answer()
    if not await is_admin(query.from_user.id): 
        return await query.answer("⚠️ ᴀᴄᴄᴇꜱꜱ ᴅᴇɴɪᴇᴅ: ʙᴀɴ ᴍᴇɴᴜ ɪꜱ ʀᴇꜱᴛʀɪᴄᴛᴇᴅ!", show_alert=True)
    
    data = query.data

    if data == "ban_menu":
        return await safe_edit(query.message, "🚫 <b>ʙᴀɴ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ</b>", get_ban_menu())

    elif data == "ban_user":
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="ban_menu")]])
        res_type, res_msg = await get_user_input(client, query, "ꜱᴇɴᴅ ᴜꜱᴇʀ_ɪᴅ [ʀᴇᴀꜱᴏɴ]\n\n/cancel - ᴄᴀɴᴄᴇʟ.", keyboard)
        if res_type != "message": return await safe_edit(query.message, "🚫 <b>ʙᴀɴ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ</b>", get_ban_menu())
        
        text = res_msg.text or ""
        try: await res_msg.delete()
        except: pass
        
        if not text or text.lower() == "/cancel":
            return await safe_edit(query.message, "🚫 <b>ʙᴀɴ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ</b>", get_ban_menu())
            
        parts = text.split(maxsplit=1)
        if not parts[0].isdigit(): 
            msg = await query.message.reply_photo(photo=START_PIC, caption="❌ ɪɴᴠᴀʟɪᴅ ɪᴅ", reply_markup=keyboard)
            asyncio.create_task(delayed_delete(msg))
            return await safe_edit(query.message, "🚫 <b>ʙᴀɴ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ</b>", get_ban_menu())
            
        uid = int(parts[0])
        reason = parts[1] if len(parts) > 1 else "ɴᴏ ʀᴇᴀꜱᴏɴ"
        await ban_user(uid, reason)
        msg = await query.message.reply_photo(photo=START_PIC, caption=f"✅ ᴜꜱᴇʀ {uid} ʙᴀɴɴᴇᴅ", reply_markup=keyboard)
        asyncio.create_task(delayed_delete(msg))
        return await safe_edit(query.message, "🚫 <b>ʙᴀɴ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ</b>", get_ban_menu())

    elif data == "ban_unban_user":
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="ban_menu")]])
        res_type, res_msg = await get_user_input(client, query, "ꜱᴇɴᴅ ᴜꜱᴇʀ_ɪᴅ\n\n/cancel - ᴄᴀɴᴄᴇʟ.", keyboard)
        if res_type != "message": return await safe_edit(query.message, "🚫 <b>ʙᴀɴ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ</b>", get_ban_menu())
        
        text = res_msg.text or ""
        try: await res_msg.delete()
        except: pass
        
        if not text or text.lower() == "/cancel":
            return await safe_edit(query.message, "🚫 <b>ʙᴀɴ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ</b>", get_ban_menu())
            
        if not text.isdigit(): 
            msg = await query.message.reply_photo(photo=START_PIC, caption="❌ ɪɴᴠᴀʟɪᴅ ɪᴅ", reply_markup=keyboard)
            asyncio.create_task(delayed_delete(msg))
            return await safe_edit(query.message, "🚫 <b>ʙᴀɴ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ</b>", get_ban_menu())
            
        uid = int(text)
        await unban_user(uid)
        msg = await query.message.reply_photo(photo=START_PIC, caption=f"✅ ᴜꜱᴇʀ {uid} ᴜɴʙᴀɴɴᴇᴅ", reply_markup=keyboard)
        asyncio.create_task(delayed_delete(msg))
        return await safe_edit(query.message, "🚫 <b>ʙᴀɴ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ</b>", get_ban_menu())

    elif data == "ban_list":
        banned = await get_banned_users()
        if not banned: return await safe_edit(query.message, "ɴᴏ ʙᴀɴɴᴇᴅ ᴜꜱᴇʀꜱ ꜰᴏᴜɴᴅ.", InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="ban_menu")]
        ]))
        text = "\n".join([f"• <code>{u['_id']}</code> - {u.get('reason','ɴᴏ ʀᴇᴀꜱᴏɴ')}" for u in banned[:100]])
        return await safe_edit(query.message, f"🚫 <b>ʙᴀɴɴᴇᴅ ᴜꜱᴇʀꜱ:</b>\n\n{text}", InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="ban_menu")]
        ]))
        
