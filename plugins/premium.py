from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from config import START_PIC
from helper_func import safe_edit, get_input
from database.database import is_admin, add_premium, remove_premium, premium_collection

@Client.on_callback_query(filters.regex(r"^premium_"))
async def premium_callbacks(client: Client, query: CallbackQuery):
    if not await is_admin(query.from_user.id): 
        return await query.answer("⚠️ ᴀᴄᴄᴇꜱꜱ ᴅᴇɴɪᴇᴅ: ᴘʀᴇᴍɪᴜᴍ ᴍᴇɴᴜ ɪꜱ ʀᴇꜱᴛʀɪᴄᴛᴇᴅ!", show_alert=True)
        
    data = query.data

    if data == "premium_menu":
        return await safe_edit(query.message, "💎 ᴘʀᴇᴍɪᴜᴍ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ\n\nᴘʀᴇᴍɪᴜᴍ ᴜꜱᴇʀꜱ ᴄᴀɴ ɢᴇɴᴇʀᴀᴛᴇ ʟɪɴᴋꜱ.", InlineKeyboardMarkup([
            [
                InlineKeyboardButton("➕ ᴀᴅᴅ ᴘʀᴇᴍɪᴜᴍ ᴜꜱᴇʀ", callback_data="premium_add"),
                InlineKeyboardButton("➖ ʀᴇᴍᴏᴠᴇ ᴘʀᴇᴍɪᴜᴍ ᴜꜱᴇʀ", callback_data="premium_remove")
            ],
            [
                InlineKeyboardButton("📋 ᴘʀᴇᴍɪᴜᴍ ᴜꜱᴇʀꜱ ʟɪꜱᴛ", callback_data="premium_list")
            ],
            [
                InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="settings")
            ]
        ]))

    elif data == "premium_add":
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="premium_menu")
            ]
        ])
        text = await get_input(client, query.message, "ꜱᴇɴᴅ ᴜꜱᴇʀ_ɪᴅ ᴀɴᴅ ɴᴜᴍʙᴇʀ ᴏꜰ ᴅᴀʏꜱ (ꜱᴘᴀᴄᴇ ꜱᴇᴘᴀʀᴀᴛᴇᴅ). ᴇxᴀᴍᴘʟᴇ: '123456789 30' ᴏʀ ꜱᴇɴᴅ /cancel ᴛᴏ ꜱᴛᴏᴘ ᴛʜɪꜱ ᴘʀᴏᴄᴇꜱꜱ", keyboard)
        if not text: return 
        parts = text.split()
        if len(parts) != 2 or not parts[0].isdigit() or not parts[1].isdigit(): return await query.message.reply_photo(photo=START_PIC, caption="❌ ɪɴᴠᴀʟɪᴅ ꜰᴏʀᴍᴀᴛ. ᴜꜱᴇ: `user_id ᴅᴀʏꜱ`", reply_markup=keyboard)
        uid, days = int(parts[0]), int(parts[1])
        await add_premium(uid, days)
        await query.message.reply_photo(photo=START_PIC, caption=f"✅ ᴜꜱᴇʀ {uid} ɢʀᴀɴᴛᴇᴅ ᴘʀᴇᴍɪᴜᴍ ꜰᴏʀ {days} ᴅᴀʏꜱ.", reply_markup=keyboard)

    elif data == "premium_remove":
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="premium_menu")
            ]
        ])
        text = await get_input(client, query.message, "ꜱᴇɴᴅ ᴜꜱᴇʀ_ɪᴅ ᴛᴏ ʀᴇᴠᴏᴋᴇ ᴘʀᴇᴍɪᴜᴍ ᴀᴄᴄᴇꜱꜱ ᴏʀ ꜱᴇɴᴅ /cancel ᴛᴏ ꜱᴛᴏᴘ ᴛʜɪꜱ ᴘʀᴏᴄᴇꜱꜱ", keyboard)
        if not text: return 
        if not text.isdigit(): return await query.message.reply_photo(photo=START_PIC, caption="❌ ɪɴᴠᴀʟɪᴅ ɪᴅ", reply_markup=keyboard)
        uid = int(text)
        await remove_premium(uid)
        await query.message.reply_photo(photo=START_PIC, caption=f"✅ ᴜꜱᴇʀ {uid}'ꜱ ᴘʀᴇᴍɪᴜᴍ ᴀᴄᴄᴇꜱꜱ ʀᴇᴠᴏᴋᴇᴅ.", reply_markup=keyboard)

    elif data == "premium_list":
        cursor = premium_collection.find({"is_premium": True})
        users = await cursor.to_list(length=100)
        if not users: return await safe_edit(query.message, "ɴᴏ ᴘʀᴇᴍɪᴜᴍ ᴜꜱᴇʀꜱ ꜰᴏᴜɴᴅ.", InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="premium_menu")
            ]
        ]))
        text = "".join([f"• <code>{u['_id']}</code> (Expires: {u.get('expires_at').strftime('%Y-%m-%d') if u.get('expires_at') else 'Never'})\n" for u in users])
        return await safe_edit(query.message, f"💎 ᴘʀᴇᴍɪᴜᴍ ᴜꜱᴇʀꜱ:\n\n{text}", InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="premium_menu")
            ]
        ]))
        
