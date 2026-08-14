import asyncio
from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from config import START_PIC
from helper_func import safe_edit, get_user_input, send_cancel_notification
from database.database import is_admin, add_premium, remove_premium, premium_collection, delete_tenant_config

async def delayed_delete(message, delay=7):
    await asyncio.sleep(delay)
    try: await message.delete()
    except: pass

def get_premium_menu():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("➕ ᴀᴅᴅ ᴘʀᴇᴍɪᴜᴍ", callback_data="premium_add"),
            InlineKeyboardButton("➖ ʀᴇᴍᴏᴠᴇ ᴘʀᴇᴍɪᴜᴍ", callback_data="premium_remove")
        ],
        [
            InlineKeyboardButton("📋 ᴘʀᴇᴍɪᴜᴍ ʟɪꜱᴛ", callback_data="premium_list"),
            InlineKeyboardButton("🗑 ʀᴇᴍᴏᴠᴇ ᴄʜᴀɴɴᴇʟꜱ", callback_data="premium_remove_channels")
        ],
        [
            InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="admin_panel")
        ]
    ])

@Client.on_callback_query(filters.regex(r"^premium_(menu|add|remove|remove_channels|list)$"))
async def premium_callbacks(client: Client, query: CallbackQuery):
    try: await query.answer()
    except: pass
    if not await is_admin(query.from_user.id): 
        try: await query.answer("⚠️ ᴀᴄᴄᴇꜱꜱ ᴅᴇɴɪᴇᴅ: ᴘʀᴇᴍɪᴜᴍ ᴍᴇɴᴜ ɪꜱ ʀᴇꜱᴛʀɪᴄᴛᴇᴅ!", show_alert=True)
        except: pass
        return
        
    data = query.data

    if data == "premium_menu":
        return await safe_edit(query.message, "💎 <b>ᴘʀᴇᴍɪᴜᴍ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ</b>\n\nᴘʀᴇᴍɪᴜᴍ ᴜꜱᴇʀꜱ ᴄᴀɴ ɢᴇɴᴇʀᴀᴛᴇ ꜰɪʟᴇ ʟɪɴᴋꜱ ᴀɴᴅ ʜᴏꜱᴛ ᴛʜᴇɪʀ ᴏᴡɴ ᴄʜᴀɴɴᴇʟꜱ.", get_premium_menu())

    elif data == "premium_add":
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="premium_menu")]])
        res_type, res_msg = await get_user_input(client, query, "ꜱᴇɴᴅ ᴜꜱᴇʀ_ɪᴅ ᴀɴᴅ ᴅᴀʏꜱ. ᴇx: <code>123456789 30</code>\n\n/cancel - ᴄᴀɴᴄᴇʟ.", keyboard)
        if res_type != "message":
            await send_cancel_notification(client, query, InlineKeyboardMarkup([[InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="premium_menu")]]))
            return await safe_edit(query.message, "💎 <b>ᴘʀᴇᴍɪᴜᴍ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ</b>", get_premium_menu())
        
        text = res_msg.text or ""
        try: await res_msg.delete()
        except: pass
        
        if not text or text.lower() == "/cancel":
            await send_cancel_notification(client, query, InlineKeyboardMarkup([[InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="premium_menu")]]))
            return await safe_edit(query.message, "💎 <b>ᴘʀᴇᴍɪᴜᴍ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ</b>", get_premium_menu())
            
        parts = text.split()
        if len(parts) != 2 or not parts[0].isdigit() or not parts[1].isdigit(): 
            msg = await query.message.reply_photo(photo=START_PIC, caption="❌ ɪɴᴠᴀʟɪᴅ ꜰᴏʀᴍᴀᴛ. ᴜꜱᴇ: <code>user_id days</code>", reply_markup=keyboard)
            asyncio.create_task(delayed_delete(msg))
            return await safe_edit(query.message, "💎 <b>ᴘʀᴇᴍɪᴜᴍ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ</b>", get_premium_menu())
            
        uid, days = int(parts[0]), int(parts[1])
        await add_premium(uid, days)
        msg = await query.message.reply_photo(photo=START_PIC, caption=f"✅ ᴜꜱᴇʀ {uid} ɢʀᴀɴᴛᴇᴅ ᴘʀᴇᴍɪᴜᴍ ꜰᴏʀ {days} ᴅᴀʏꜱ.", reply_markup=keyboard)
        asyncio.create_task(delayed_delete(msg))
        return await safe_edit(query.message, "💎 <b>ᴘʀᴇᴍɪᴜᴍ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ</b>", get_premium_menu())

    elif data == "premium_remove":
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="premium_menu")]])
        res_type, res_msg = await get_user_input(client, query, "ꜱᴇɴᴅ ᴜꜱᴇʀ_ɪᴅ ᴛᴏ ʀᴇᴠᴏᴋᴇ ᴘʀᴇᴍɪᴜᴍ\n\n/cancel - ᴄᴀɴᴄᴇʟ.", keyboard)
        if res_type != "message":
            await send_cancel_notification(client, query, InlineKeyboardMarkup([[InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="premium_menu")]]))
            return await safe_edit(query.message, "💎 <b>ᴘʀᴇᴍɪᴜᴍ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ</b>", get_premium_menu())
        
        text = res_msg.text or ""
        try: await res_msg.delete()
        except: pass
        
        if not text or text.lower() == "/cancel":
            await send_cancel_notification(client, query, InlineKeyboardMarkup([[InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="premium_menu")]]))
            return await safe_edit(query.message, "💎 <b>ᴘʀᴇᴍɪᴜᴍ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ</b>", get_premium_menu())
            
        if not text.isdigit(): 
            msg = await query.message.reply_photo(photo=START_PIC, caption="❌ ɪɴᴠᴀʟɪᴅ ɪᴅ", reply_markup=keyboard)
            asyncio.create_task(delayed_delete(msg))
            return await safe_edit(query.message, "💎 <b>ᴘʀᴇᴍɪᴜᴍ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ</b>", get_premium_menu())
            
        uid = int(text)
        await remove_premium(uid)
        
        msg = await query.message.reply_photo(photo=START_PIC, caption=f"✅ ᴜꜱᴇʀ {uid}'ꜱ ᴘʀᴇᴍɪᴜᴍ ʀᴇᴠᴏᴋᴇᴅ.", reply_markup=keyboard)
        asyncio.create_task(delayed_delete(msg))
        return await safe_edit(query.message, "💎 <b>ᴘʀᴇᴍɪᴜᴍ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ</b>", get_premium_menu())

    elif data == "premium_remove_channels":
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="premium_menu")]])
        res_type, res_msg = await get_user_input(client, query, "ꜱᴇɴᴅ ᴜꜱᴇʀ_ɪᴅ ᴛᴏ ʀᴇᴠᴏᴋᴇ ᴛʜᴇɪʀ ᴄᴜꜱᴛᴏᴍ ᴄʜᴀɴɴᴇʟꜱ\n\n/cancel - ᴄᴀɴᴄᴇʟ.", keyboard)
        if res_type != "message":
            await send_cancel_notification(client, query, InlineKeyboardMarkup([[InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="premium_menu")]]))
            return await safe_edit(query.message, "💎 <b>ᴘʀᴇᴍɪᴜᴍ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ</b>", get_premium_menu())
        
        text = res_msg.text or ""
        try: await res_msg.delete()
        except: pass
        
        if not text or text.lower() == "/cancel":
            await send_cancel_notification(client, query, InlineKeyboardMarkup([[InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="premium_menu")]]))
            return await safe_edit(query.message, "💎 <b>ᴘʀᴇᴍɪᴜᴍ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ</b>", get_premium_menu())
            
        if not text.isdigit(): 
            msg = await query.message.reply_photo(photo=START_PIC, caption="❌ ɪɴᴠᴀʟɪᴅ ɪᴅ", reply_markup=keyboard)
            asyncio.create_task(delayed_delete(msg))
            return await safe_edit(query.message, "💎 <b>ᴘʀᴇᴍɪᴜᴍ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ</b>", get_premium_menu())
            
        uid = int(text)
        await delete_tenant_config(uid)
        
        try:
            await client.send_message(uid, "❌ <b>ɴᴏᴛɪᴄᴇ:</b> ʏᴏᴜʀ ᴄᴜꜱᴛᴏᴍ ᴅᴀᴛᴀʙᴀꜱᴇ & ꜰꜱ ᴄʜᴀɴɴᴇʟꜱ ʜᴀᴠᴇ ʙᴇᴇɴ ʀᴇᴍᴏᴠᴇᴅ.")
        except Exception:
            pass
        
        msg = await query.message.reply_photo(photo=START_PIC, caption=f"✅ ᴜꜱᴇʀ {uid}'ꜱ ᴄᴜꜱᴛᴏᴍ ᴄʜᴀɴɴᴇʟꜱ ᴅᴇʟᴇᴛᴇᴅ.", reply_markup=keyboard)
        asyncio.create_task(delayed_delete(msg))
        return await safe_edit(query.message, "💎 <b>ᴘʀᴇᴍɪᴜᴍ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ</b>", get_premium_menu())

    elif data == "premium_list":
        cursor = premium_collection.find({"is_premium": True})
        users = await cursor.to_list(length=100)
        if not users: return await safe_edit(query.message, "ɴᴏ ᴘʀᴇᴍɪᴜᴍ ᴜꜱᴇʀꜱ ꜰᴏᴜɴᴅ.", InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="premium_menu")]
        ]))
        text = "".join([f"• <code>{u['_id']}</code> (Expires: <code>{u.get('expires_at').strftime('%Y-%m-%d') if u.get('expires_at') else 'Never'}</code>)\n" for u in users])
        return await safe_edit(query.message, f"💎 <b>ᴘʀᴇᴍɪᴜᴍ ᴜꜱᴇʀꜱ:</b>\n\n{text}", InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="premium_menu")]
        ]))
        
