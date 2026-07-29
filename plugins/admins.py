import asyncio
from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from config import START_PIC, OWNER_ID
from helper_func import safe_edit, get_input
from database.database import is_admin, add_admin, remove_admin, get_admins

async def delayed_delete(message, delay=7):
    await asyncio.sleep(delay)
    try: await message.delete()
    except: pass

@Client.on_callback_query(filters.regex(r"^admin_"))
async def admin_callbacks(client: Client, query: CallbackQuery):
    if not await is_admin(query.from_user.id): 
        return await query.answer("⚠️ ᴀᴄᴄᴇꜱꜱ ᴅᴇɴɪᴇᴅ: ᴀᴅᴍɪɴ ᴍᴇɴᴜ ɪꜱ ʀᴇꜱᴛʀɪᴄᴛᴇᴅ!", show_alert=True)
    
    data = query.data

    if data == "admin_menu":
        return await safe_edit(query.message, "👨‍💻 ᴀᴅᴍɪɴ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ", InlineKeyboardMarkup([
            [
                InlineKeyboardButton("➕ ᴀᴅᴅ ᴀᴅᴍɪɴ", callback_data="admin_add"), 
                InlineKeyboardButton("➖ ʀᴇᴍᴏᴠᴇ ᴀᴅᴍɪɴ", callback_data="admin_remove")
            ],
            [
                InlineKeyboardButton("📋 ᴀᴅᴍɪɴ ʟɪꜱᴛ", callback_data="admin_list")
            ],
            [
                InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="settings")
            ]
        ]))

    elif data == "admin_add":
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="admin_menu")
            ]
        ])
        text = await get_input(client, query.message, "ꜱᴇɴᴅ ᴜꜱᴇʀ_ɪᴅ ᴛᴏ ᴀᴅᴅ ᴀꜱ ᴀᴅᴍɪɴ", keyboard)
        if not text: return 
        if not text.isdigit(): 
            msg = await query.message.reply_photo(photo=START_PIC, caption="❌ ɪɴᴠᴀʟɪᴅ ɪᴅ", reply_markup=keyboard)
            return asyncio.create_task(delayed_delete(msg))
            
        uid = int(text)
        if uid == int(OWNER_ID): 
            msg = await query.message.reply_photo(photo=START_PIC, caption="⚠️ ᴏᴡɴᴇʀ ɪꜱ ᴀʟʀᴇᴀᴅʏ ᴀᴅᴍɪɴ", reply_markup=keyboard)
            return asyncio.create_task(delayed_delete(msg))
            
        await add_admin(uid)
        msg = await query.message.reply_photo(photo=START_PIC, caption=f"✅ ᴜꜱᴇʀ {uid} ᴀᴅᴅᴇᴅ ᴀꜱ ᴀᴅᴍɪɴ", reply_markup=keyboard)
        asyncio.create_task(delayed_delete(msg))

    elif data == "admin_remove":
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="admin_menu")
            ]
        ])
        text = await get_input(client, query.message, "ꜱᴇɴᴅ ᴜꜱᴇʀ_ɪᴅ ᴛᴏ ʀᴇᴍᴏᴠᴇ ꜰʀᴏᴍ ᴀᴅᴍɪɴ", keyboard)
        if not text: return 
        if not text.isdigit(): 
            msg = await query.message.reply_photo(photo=START_PIC, caption="❌ ɪɴᴠᴀʟɪᴅ ɪᴅ", reply_markup=keyboard)
            return asyncio.create_task(delayed_delete(msg))
            
        uid = int(text)
        if uid == int(OWNER_ID): 
            msg = await query.message.reply_photo(photo=START_PIC, caption="❌ ᴄᴀɴɴᴏᴛ ʀᴇᴍᴏᴠᴇ ᴏᴡɴᴇʀ", reply_markup=keyboard)
            return asyncio.create_task(delayed_delete(msg))
            
        await remove_admin(uid)
        msg = await query.message.reply_photo(photo=START_PIC, caption=f"✅ ᴜꜱᴇʀ {uid} ʀᴇᴍᴏᴠᴇᴅ ꜰʀᴏᴍ ᴀᴅᴍɪɴ", reply_markup=keyboard)
        asyncio.create_task(delayed_delete(msg))

    elif data == "admin_list":
        admins = await get_admins()
        if not admins: return await safe_edit(query.message, "ɴᴏ ᴀᴅᴍɪɴꜱ ꜰᴏᴜɴᴅ.", InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="admin_menu")
            ]
        ]))
        text = "\n".join([f"• {a}" for a in admins[:100]])
        return await safe_edit(query.message, f"👨‍💻 ᴀᴅᴍɪɴ ʟɪꜱᴛ:\n\n{text}", InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="admin_menu")
            ]
        ]))
        
