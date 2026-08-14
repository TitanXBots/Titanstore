import asyncio
from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from pyromod.exceptions import ListenerTimeout
from helper_func import safe_edit, get_readable_time
from database.database import (
    is_admin, get_auto_delete_status, set_auto_delete_status, 
    get_auto_delete_time, set_auto_delete_time,
    get_file_again_status, set_file_again_status
)

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

async def render_autodelete_menu(message, status_text=None):
    is_on = await get_auto_delete_status()
    get_file_on = await get_file_again_status()
    status = "ᴏɴ ✅" if is_on else "ᴏꜰꜰ ❌"
    gf_status = "ᴏɴ ✅" if get_file_on else "ᴏꜰꜰ ❌"
    current_time = await get_auto_delete_time()
    
    text = "🗑 <b>ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ & ɢᴇᴛ ꜰɪʟᴇ ᴀɢᴀɪɴ</b>\n\n"
    if status_text:
        text += f"{status_text}\n\n"
    
    text += (
        f"ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ: <b>{status}</b>\n"
        f"ᴅᴇʟᴇᴛᴇ ᴛɪᴍᴇ: <b>{get_readable_time(current_time)}</b>\n"
        f"ɢᴇᴛ ꜰɪʟᴇ ᴀɢᴀɪɴ ʙᴜᴛᴛᴏɴ: <b>{gf_status}</b>"
    )
    markup = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ ᴀᴜᴛᴏ ᴅᴇʟ ᴏɴ", callback_data="autodelete_on"), 
            InlineKeyboardButton("❌ ᴀᴜᴛᴏ ᴅᴇʟ ᴏꜰꜰ", callback_data="autodelete_off")
        ],
        [
            InlineKeyboardButton(f"♻️ ɢᴇᴛ ꜰɪʟᴇ ᴀɢᴀɪɴ: {gf_status}", callback_data="autodelete_toggle_gf")
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
        try: await query.answer("⚠️ ᴀᴄᴄᴇꜱꜱ ᴅᴇɴɪᴇᴅ: ᴀᴅᴍɪɴꜱ ᴏɴʟʏ!", show_alert=True)
        except: pass
        return
    
    data = query.data

    if data == "autodelete_menu":
        try: await query.answer()
        except: pass
        await render_autodelete_menu(query.message)
        
    elif data == "autodelete_on":
        try: await query.answer()
        except: pass
        if await get_auto_delete_status():
            return await render_autodelete_menu(query.message, "⚠️ <b>ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ ɪꜱ ᴀʟʀᴇᴀᴅʏ ᴇɴᴀʙʟᴇᴅ!</b>")
        await set_auto_delete_status(True)
        await render_autodelete_menu(query.message, "✅ <b>ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ ᴇɴᴀʙʟᴇᴅ!</b>")
        
    elif data == "autodelete_off":
        try: await query.answer()
        except: pass
        if not await get_auto_delete_status():
            return await render_autodelete_menu(query.message, "⚠️ <b>ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ ɪꜱ ᴀʟʀᴇᴀᴅʏ ᴅɪꜱᴀʙʟᴇᴅ!</b>")
        await set_auto_delete_status(False)
        await render_autodelete_menu(query.message, "❌ <b>ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ ᴅɪꜱᴀʙʟᴇᴅ!</b>")

    elif data == "autodelete_toggle_gf":
        current_gf = await get_file_again_status()
        await set_file_again_status(not current_gf)
        try: await query.answer()
        except: pass
        status_word = "ᴇɴᴀʙʟᴇᴅ" if not current_gf else "ᴅɪꜱᴀʙʟᴇᴅ"
        await render_autodelete_menu(query.message, f"✅ <b>'ɢᴇᴛ ꜰɪʟᴇ ᴀɢᴀɪɴ' {status_word}!</b>")
        
    elif data == "autodelete_set_time":
        try: await query.answer()
        except: pass
        back_keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="autodelete_menu")]])
        await safe_edit(query.message, "⏱ <b>ꜱᴇᴛ ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ ᴛɪᴍᴇʀ</b>\n\nꜱᴇɴᴅ ᴍᴇ ᴀ ᴛɪᴍᴇ ɪɴ ʟɪᴋᴇ ᴛʜɪꜱ - <code>1h</code> ᴏʀ <code>15m</code>\n\n/cancel - ᴄᴀɴᴄᴇʟ.", back_keyboard)
        try:
            input_msg = await client.listen(query.message.chat.id, timeout=60)
        except ListenerTimeout:
            return await render_autodelete_menu(query.message)
        
        text = input_msg.text or ""
        try: await input_msg.delete()
        except: pass
            
        if not text or text.lower() == "/cancel":
            await safe_edit(query.message, "❌ <b>ᴘʀᴏᴄᴇꜱꜱ ᴄᴀɴᴄᴇʟʟᴇᴅ!</b>")
            await asyncio.sleep(2)
            return await render_autodelete_menu(query.message)
            
        time_in_seconds = parse_time(text)
        if time_in_seconds < 10: 
            return await render_autodelete_menu(query.message, "❌ <b>ɪɴᴠᴀʟɪᴅ ꜰᴏʀᴍᴀᴛ!</b> ᴜꜱᴇ <code>1h</code>, <code>15m</code>, ᴏʀ <code>30s</code>.")
            
        await set_auto_delete_time(time_in_seconds)
        await render_autodelete_menu(query.message, f"✅ <b>ᴛɪᴍᴇʀ ᴜᴘᴅᴀᴛᴇᴅ ᴛᴏ {get_readable_time(time_in_seconds)}!</b>")
        
