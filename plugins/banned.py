import asyncio
from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from config import START_PIC
from helper_func import safe_edit, get_input
from database.database import is_admin, ban_user, unban_user, get_banned_users

async def delayed_delete(message, delay=7):
    await asyncio.sleep(delay)
    try: await message.delete()
    except: pass

@Client.on_callback_query(filters.regex(r"^ban_"))
async def ban_callbacks(client: Client, query: CallbackQuery):
    if not await is_admin(query.from_user.id): 
        return await query.answer("⚠️ ᴀᴄᴄᴇꜱꜱ ᴅᴇɴɪᴇᴅ: ʙᴀɴ ᴍᴇɴᴜ ɪꜱ ʀᴇꜱᴛʀɪᴄᴛᴇᴅ!", show_alert=True)
    
    data = query.data

    if data == "ban_menu":
        return await safe_edit(query.message, "🚫 ʙᴀɴ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ", InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🚫 ʙᴀɴ ᴜꜱᴇʀ", callback_data="ban_user"), 
                InlineKeyboardButton("✅ ᴜɴʙᴀɴ ᴜꜱᴇʀ", callback_data="ban_unban_user")
            ],
            [
                InlineKeyboardButton("📄 ʙᴀɴɴᴇᴅ ʟɪꜱᴛ", callback_data="ban_list")
            ],
            [
                InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="settings")
            ]
        ]))

    elif data == "ban_user":
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="ban_menu")
            ]
        ])
        text = await get_input(client, query.message, "ꜱᴇɴᴅ ᴜꜱᴇʀ_ɪᴅ [ʀᴇᴀꜱᴏɴ]", keyboard)
        if not text: return 
        parts = text.split(maxsplit=1)
        if not parts[0].isdigit(): 
            msg = await query.message.reply_photo(photo=START_PIC, caption="❌ ɪɴᴠᴀʟɪᴅ ɪᴅ", reply_markup=keyboard)
            return asyncio.create_task(delayed_delete(msg))
            
        uid = int(parts[0])
        reason = parts[1] if len(parts) > 1 else "ɴᴏ ʀᴇᴀꜱᴏɴ"
        await ban_user(uid, reason)
        msg = await query.message.reply_photo(photo=START_PIC, caption=f"✅ ᴜꜱᴇʀ {uid} ʙᴀɴɴᴇᴅ", reply_markup=keyboard)
        asyncio.create_task(delayed_delete(msg))

    elif data == "ban_unban_user":
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="ban_menu")
            ]
        ])
        text = await get_input(client, query.message, "ꜱᴇɴᴅ ᴜꜱᴇʀ_ɪᴅ", keyboard)
        if not text: return 
        if not text.isdigit(): 
            msg = await query.message.reply_photo(photo=START_PIC, caption="❌ ɪɴᴠᴀʟɪᴅ ɪᴅ", reply_markup=keyboard)
            return asyncio.create_task(delayed_delete(msg))
            
        uid = int(text)
        await unban_user(uid)
        msg = await query.message.reply_photo(photo=START_PIC, caption=f"✅ ᴜꜱᴇʀ {uid} ᴜɴʙᴀɴɴᴇᴅ", reply_markup=keyboard)
        asyncio.create_task(delayed_delete(msg))

    elif data == "ban_list":
        banned = await get_banned_users()
        if not banned: return await safe_edit(query.message, "ɴᴏ ʙᴀɴɴᴇᴅ ᴜꜱᴇʀꜱ ꜰᴏᴜɴᴅ.", InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="ban_menu")
            ]
        ]))
        text = "\n".join([f"• {u['_id']} - {u.get('reason','ɴᴏ ʀᴇᴀꜱᴏɴ')}" for u in banned[:100]])
        return await safe_edit(query.message, f"🚫 ʙᴀɴɴᴇᴅ ᴜꜱᴇʀꜱ:\n\n{text}", InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="ban_menu")
            ]
        ]))
        
