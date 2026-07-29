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

@Client.on_callback_query(filters.regex(r"^autodelete_"))
async def autodelete_callbacks(client: Client, query: CallbackQuery):
    if not await is_admin(query.from_user.id): 
        return await query.answer("⚠️ ᴀᴄᴄᴇꜱꜱ ᴅᴇɴɪᴇᴅ: ᴀᴅᴍɪɴꜱ ᴏɴʟʏ!", show_alert=True)
    
    data = query.data

    if data == "autodelete_menu":
        is_on = await get_auto_delete_status()
        status = "ᴏɴ ✅" if is_on else "ᴏꜰꜰ ❌"
        current_time = await get_auto_delete_time()
        return await safe_edit(query.message, f"🗑 <b>ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ</b>\n\nᴄᴜʀʀᴇɴᴛ ꜱᴛᴀᴛᴜꜱ: <b>{status}</b>\nᴅᴇʟᴇᴛᴇ ᴛɪᴍᴇ: <b>{get_readable_time(current_time)}</b>", InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ ᴇɴᴀʙʟᴇ", callback_data="autodelete_on"), 
                InlineKeyboardButton("❌ ᴅɪꜱᴀʙʟᴇ", callback_data="autodelete_off")
            ],
            [
                InlineKeyboardButton("⏱ ᴄʜᴀɴɢᴇ ᴛɪᴍᴇʀ", callback_data="autodelete_set_time")
            ],
            [
                InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="settings")
            ]
        ]))
        
    elif data == "autodelete_on":
        await set_auto_delete_status(True)
        await query.answer("✅ ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ ᴇɴᴀʙʟᴇᴅ!", show_alert=True)
        current_time = await get_auto_delete_time()
        return await safe_edit(query.message, f"🗑 <b>ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ</b>\n\nᴄᴜʀʀᴇɴᴛ ꜱᴛᴀᴛᴜꜱ: <b>ᴏɴ ✅</b>\nᴅᴇʟᴇᴛᴇ ᴛɪᴍᴇ: <b>{get_readable_time(current_time)}</b>", InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ ᴇɴᴀʙʟᴇ", callback_data="autodelete_on"), 
                InlineKeyboardButton("❌ ᴅɪꜱᴀʙʟᴇ", callback_data="autodelete_off")
            ],
            [
                InlineKeyboardButton("⏱ ᴄʜᴀɴɢᴇ ᴛɪᴍᴇʀ", callback_data="autodelete_set_time")
            ],
            [
                InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="settings")
            ]
        ]))
        
    elif data == "autodelete_off":
        await set_auto_delete_status(False)
        await query.answer("❌ ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ ᴅɪꜱᴀʙʟᴇᴅ!", show_alert=True)
        current_time = await get_auto_delete_time()
        return await safe_edit(query.message, f"🗑 <b>ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ</b>\n\nᴄᴜʀʀᴇɴᴛ ꜱᴛᴀᴛᴜꜱ: <b>ᴏꜰꜰ ❌</b>\nᴅᴇʟᴇᴛᴇ ᴛɪᴍᴇ: <b>{get_readable_time(current_time)}</b>", InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ ᴇɴᴀʙʟᴇ", callback_data="autodelete_on"), 
                InlineKeyboardButton("❌ ᴅɪꜱᴀʙʟᴇ", callback_data="autodelete_off")
            ],
            [
                InlineKeyboardButton("⏱ ᴄʜᴀɴɢᴇ ᴛɪᴍᴇʀ", callback_data="autodelete_set_time")
            ],
            [
                InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="settings")
            ]
        ]))
        
    elif data == "autodelete_set_time":
        back_keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="autodelete_menu")
            ]
        ])
        prompt_text = "<b>ꜱᴇɴᴅ ᴍᴇ ᴀ ᴛɪᴍᴇ ɪɴ ʟɪᴋᴇ ᴛʜɪꜱ - 1ʜ ᴏʀ 15ᴍ\n\n/cancel - ᴄᴀɴᴄᴇʟ ᴛʜɪꜱ ᴘʀᴏᴄᴇꜱꜱ.</b>"
        
        await safe_edit(query.message, prompt_text, back_keyboard)
        
        try:
            input_msg = await client.listen(query.message.chat.id, timeout=300)
        except ListenerTimeout:
            await safe_edit(query.message, "⌛ ᴛɪᴍᴇᴏᴜᴛ!", back_keyboard)
            return asyncio.create_task(delayed_delete(query.message))
        
        text = input_msg.text
        
        try:
            await input_msg.delete()
        except Exception:
            pass
            
        if not text or text.lower() == "/cancel":
            await safe_edit(query.message, "❌ ᴄᴀɴᴄᴇʟʟᴇᴅ!", back_keyboard)
            return asyncio.create_task(delayed_delete(query.message))
            
        time_in_seconds = parse_time(text)
        if time_in_seconds < 10: 
            await safe_edit(
                query.message,
                "❌ <b>ɪɴᴠᴀʟɪᴅ ꜰᴏʀᴍᴀᴛ!</b> ᴘʟᴇᴀꜱᴇ ᴜꜱᴇ ꜰᴏʀᴍᴀᴛꜱ ʟɪᴋᴇ <code>1h</code>, <code>15m</code>, ᴏʀ <code>30s</code>.", 
                back_keyboard
            )
            return asyncio.create_task(delayed_delete(query.message))
            
        await set_auto_delete_time(time_in_seconds)
        
        await safe_edit(
            query.message,
            f"✅ ᴀᴜᴛᴏ-ᴅᴇʟᴇᴛᴇ ᴛɪᴍᴇʀ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ꜱᴇᴛ ᴛᴏ <b>{get_readable_time(time_in_seconds)}</b>.", 
            back_keyboard
        )
        asyncio.create_task(delayed_delete(query.message))
        
