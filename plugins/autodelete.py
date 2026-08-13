import asyncio
from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from pyromod.exceptions import ListenerTimeout
from config import START_PIC
from helper_func import safe_edit, get_readable_time
from database.database import is_admin, get_auto_delete_status, set_auto_delete_status, get_auto_delete_time, set_auto_delete_time

async def delayed_delete(message, delay=7):
    await asyncio.sleep(delay)
    try: await message.delete()
    except: pass

def parse_time(time_str: str) -> int:
    time_str = time_str.lower().strip()
    if time_str.endswith('h') and time_str[:-1].isdigit(): 
        return int(time_str[:-1]) * 3600
    elif time_str.endswith('m') and time_str[:-1].isdigit(): 
        return int(time_str[:-1]) * 60
    elif time_str.endswith('s') and time_str[:-1].isdigit(): 
        return int(time_str[:-1])
    elif time_str.isdigit(): 
        return int(time_str)
    return 0

async def render_autodelete_menu(message):
    is_on = await get_auto_delete_status()
    status = "ᴏɴ ✅" if is_on else "ᴏꜰꜰ ❌"
    current_time = await get_auto_delete_time()
    text = f"🗑 <b>ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ</b>\n\nᴄᴜʀʀᴇɴᴛ ꜱᴛᴀᴛᴜꜱ: <b>{status}</b>\nᴅᴇʟᴇᴛᴇ ᴛɪᴍᴇ: <b>{get_readable_time(current_time)}</b>"
    markup = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ ᴇɴᴀʙʟᴇ", callback_data="autodelete_on"), 
            InlineKeyboardButton("❌ ᴅɪꜱᴀʙʟᴇ", callback_data="autodelete_off")
        ],
        [
            InlineKeyboardButton("⏱ ᴄʜᴀɴɢᴇ ᴛɪᴍᴇʀ", callback_data="autodelete_set_time")
        ],
        [
            InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="admin_panel")
        ]
    ])
    await safe_edit(message, text, markup)

@Client.on_callback_query(filters.regex(r"^autodelete_"))
async def autodelete_callbacks(client: Client, query: CallbackQuery):
    if not await is_admin(query.from_user.id): 
        return await query.answer("⚠️ ᴀᴄᴄᴇꜱꜱ ᴅᴇɴɪᴇᴅ: ᴀᴅᴍɪɴꜱ ᴏɴʟʏ!", show_alert=True)
    
    data = query.data

    if data == "autodelete_menu":
        await render_autodelete_menu(query.message)
        
    elif data == "autodelete_on":
        await set_auto_delete_status(True)
        await query.answer("✅ ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ ᴇɴᴀʙʟᴇᴅ!", show_alert=True)
        await render_autodelete_menu(query.message)
        
    elif data == "autodelete_off":
        await set_auto_delete_status(False)
        await query.answer("❌ ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ ᴅɪꜱᴀʙʟᴇᴅ!", show_alert=True)
        await render_autodelete_menu(query.message)
        
    elif data == "autodelete_set_time":
        back_keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="autodelete_menu")]])
        await safe_edit(query.message, "<b>ꜱᴇɴᴅ ᴍᴇ ᴀ ᴛɪᴍᴇ ɪɴ ʟɪᴋᴇ ᴛʜɪꜱ - 1ʜ ᴏʀ 15ᴍ\n\n/cancel - ᴄᴀɴᴄᴇʟ ᴛʜɪꜱ ᴘʀᴏᴄᴇꜱꜱ.</b>", back_keyboard)
        
        try:
            input_msg = await client.listen(query.message.chat.id, timeout=60)
        except ListenerTimeout:
            await query.answer("⌛ ᴛɪᴍᴇᴏᴜᴛ!", show_alert=True)
            return await render_autodelete_menu(query.message)
        
        text = input_msg.text or ""
        try: await input_msg.delete()
        except: pass
            
        if not text or text.lower() == "/cancel":
            await query.answer("❌ ᴄᴀɴᴄᴇʟʟᴇᴅ!", show_alert=True)
            return await render_autodelete_menu(query.message)
            
        time_in_seconds = parse_time(text)
        if time_in_seconds < 10: 
            msg = await query.message.reply_photo(photo=START_PIC, caption="❌ <b>ɪɴᴠᴀʟɪᴅ ꜰᴏʀᴍᴀᴛ!</b> ᴘʟᴇᴀꜱᴇ ᴜꜱᴇ ꜰᴏʀᴍᴀᴛꜱ ʟɪᴋᴇ <code>1h</code>, <code>15m</code>, ᴏʀ <code>30s</code>.", reply_markup=back_keyboard)
            asyncio.create_task(delayed_delete(msg))
            return await render_autodelete_menu(query.message)
            
        await set_auto_delete_time(time_in_seconds)
        
        msg = await query.message.reply_photo(photo=START_PIC, caption=f"✅ ᴀᴜᴛᴏ-ᴅᴇʟᴇᴛᴇ ᴛɪᴍᴇʀ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ꜱᴇᴛ ᴛᴏ <b>{get_readable_time(time_in_seconds)}</b>.", reply_markup=back_keyboard)
        asyncio.create_task(delayed_delete(msg))
        await render_autodelete_menu(query.message)
        
