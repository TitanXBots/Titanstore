import asyncio
from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from pyromod.exceptions import ListenerTimeout
from helper_func import safe_edit
from database.database import (
    is_admin, get_protect_status, set_protect_status, 
    get_force_sub_status, set_force_sub_status,
    get_global_db_channel, set_global_db_channel,
    get_global_fs_channels, set_global_fs_channels
)

@Client.on_callback_query(filters.regex("^(protect_menu|protect_on|protect_off|forcesub_on|forcesub_off|global_db_menu|global_db_set|global_fs_menu|global_fs_set|add_channels_menu)$"))
async def settings_cb(client: Client, query: CallbackQuery):
    try: await query.answer()
    except: pass
    user_id = query.from_user.id
    
    if not await is_admin(user_id):
        return await query.answer("⚠️ ᴀᴄᴄᴇꜱꜱ ᴅᴇɴɪᴇᴅ: ᴀᴅᴍɪɴꜱ ᴏɴʟʏ!", show_alert=True)
        
    data = query.data

    if data == "add_channels_menu":
        return await safe_edit(query.message, "📁 <b>ᴀᴅᴅ ᴄʜᴀɴɴᴇʟꜱ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ</b>\n\nᴄᴏɴꜰɪɢᴜʀᴇ ɢʟᴏʙᴀʟ ᴅᴀᴛᴀʙᴀꜱᴇ ᴀɴᴅ ꜰᴏʀᴄᴇ-ꜱᴜʙꜱᴄʀɪᴘᴛɪᴏɴ ᴄʜᴀɴɴᴇʟꜱ.", InlineKeyboardMarkup([
            [InlineKeyboardButton("📁 ɢʟᴏʙᴀʟ ᴅʙ", callback_data="global_db_menu"), InlineKeyboardButton("📢 ɢʟᴏʙᴀʟ ꜰꜱ", callback_data="global_fs_menu")],
            [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="admin_panel")]
        ]))

    elif data == "protect_menu":
        is_on = await get_protect_status()
        status = "ᴏɴ ✅" if is_on else "ᴏꜰꜰ ❌"
        text = (
            f"🔒 <b>ᴘʀᴏᴛᴇᴄᴛ ᴄᴏɴᴛᴇɴᴛ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ</b>\n\n"
            f"ᴘʀᴇᴠᴇɴᴛꜱ ᴜꜱᴇʀꜱ ꜰʀᴏᴍ ꜰᴏʀᴡᴀʀᴅɪɴɢ, ꜱᴀᴠɪɴɢ, ᴏʀ ᴄᴏᴘʏɪɴɢ ꜰɪʟᴇꜱ.\n\n"
            f"ᴄᴜʀʀᴇɴᴛ ꜱᴛᴀᴛᴜꜱ: <b>{status}</b>"
        )
        return await safe_edit(query.message, text, InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ ᴇɴᴀʙʟᴇ", callback_data="protect_on"), InlineKeyboardButton("❌ ᴅɪꜱᴀʙʟᴇ", callback_data="protect_off")],
            [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="admin_panel")]
        ]))

    elif data in ["protect_on", "protect_off"]:
        await set_protect_status(data == "protect_on")
        is_on = await get_protect_status()
        status = "ᴏɴ ✅" if is_on else "ᴏꜰꜰ ❌"
        text = (
            f"🔒 <b>ᴘʀᴏᴛᴇᴄᴛ ᴄᴏɴᴛᴇɴᴛ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ</b>\n\n"
            f"ᴘʀᴇᴠᴇɴᴛꜱ ᴜꜱᴇʀꜱ ꜰʀᴏᴍ ꜰᴏʀᴡᴀʀᴅɪɴɢ, ꜱᴀᴠɪɴɢ, ᴏʀ ᴄᴏᴘʏɪɴɢ ꜰɪʟᴇꜱ.\n\n"
            f"ᴄᴜʀʀᴇɴᴛ ꜱᴛᴀᴛᴜꜱ: <b>{status}</b>"
        )
        return await safe_edit(query.message, text, InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ ᴇɴᴀʙʟᴇ", callback_data="protect_on"), InlineKeyboardButton("❌ ᴅɪꜱᴀʙʟᴇ", callback_data="protect_off")], 
            [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="admin_panel")]
        ]))

    elif data == "global_db_menu":
        current_db = await get_global_db_channel()
        text = (
            f"📁 <b>ᴅᴀᴛᴀʙᴀꜱᴇ ᴄʜᴀɴɴᴇʟ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ</b>\n\n"
            f"ᴄᴜʀʀᴇɴᴛ ᴅʙ ᴄʜᴀɴɴᴇʟ ɪᴅ: <code>{current_db}</code>"
        )
        return await safe_edit(query.message, text, InlineKeyboardMarkup([
            [InlineKeyboardButton("✏️ ᴄʜᴀɴɢᴇ ᴅʙ ᴄʜᴀɴɴᴇʟ", callback_data="global_db_set")],
            [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="add_channels_menu")]
        ]))

    elif data == "global_db_set":
        back_keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="global_db_menu")]])
        await safe_edit(query.message, "📁 <b>ꜱᴇᴛ ᴅᴀᴛᴀʙᴀꜱᴇ ᴄʜᴀɴɴᴇʟ</b>\n\nꜱᴇɴᴅ ɴᴇᴡ ᴅᴀᴛᴀʙᴀꜱᴇ ᴄʜᴀɴɴᴇʟ ɪᴅ (ᴍᴜꜱᴛ ꜱᴛᴀʀᴛ ᴡɪᴛʜ -100)\n\n/cancel - ᴄᴀɴᴄᴇʟ.", back_keyboard)
        try:
            input_msg = await client.listen(chat_id=query.message.chat.id, timeout=60)
        except ListenerTimeout:
            return await safe_edit(query.message, "📁 <b>ᴅᴀᴛᴀʙᴀꜱᴇ ᴄʜᴀɴɴᴇʟ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ</b>", back_keyboard)

        text_input = input_msg.text or ""
        try: await input_msg.delete()
        except: pass

        if not text_input or text_input.lower() == "/cancel":
            return await safe_edit(query.message, "❌ <b>ᴘʀᴏᴄᴇꜱꜱ ᴄᴀɴᴄᴇʟʟᴇᴅ!</b>\n\n📁 <b>ᴅᴀᴛᴀʙᴀꜱᴇ ᴄʜᴀɴɴᴇʟ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ</b>", InlineKeyboardMarkup([[InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="add_channels_menu")]]))

        try:
            new_id = int(text_input)
            if not str(new_id).startswith("-100"): raise ValueError
        except Exception:
            return await safe_edit(query.message, "❌ <b>ɪɴᴠᴀʟɪᴅ ɪᴅ!</b>\n\nᴍᴜꜱᴛ ꜱᴛᴀʀᴛ ᴡɪᴛʜ -100.", back_keyboard)

        current_db = await get_global_db_channel()
        if new_id == current_db:
            return await safe_edit(query.message, f"⚠️ <b>ᴛʜɪꜱ ɪꜱ ᴀʟʀᴇᴀᴅʏ ᴛʜᴇ ᴄᴜʀʀᴇɴᴛ ᴅʙ ᴄʜᴀɴɴᴇʟ!</b>\n\nᴄᴜʀʀᴇɴᴛ ᴅʙ: <code>{current_db}</code>", InlineKeyboardMarkup([[InlineKeyboardButton("✏️ ᴄʜᴀɴɢᴇ ᴅʙ ᴄʜᴀɴɴᴇʟ", callback_data="global_db_set")], [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="add_channels_menu")]]))

        await set_global_db_channel(new_id)
        current_db = await get_global_db_channel()
        text = (
            f"✅ <b>ᴅʙ ᴄʜᴀɴɴᴇʟ ᴜᴘᴅᴀᴛᴇᴅ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ!</b>\n\n"
            f"ᴄᴜʀʀᴇɴᴛ ᴅʙ ᴄʜᴀɴɴᴇʟ ɪᴅ: <code>{current_db}</code>"
        )
        return await safe_edit(query.message, text, InlineKeyboardMarkup([
            [InlineKeyboardButton("✏️ ᴄʜᴀɴɢᴇ ᴅʙ ᴄʜᴀɴɴᴇʟ", callback_data="global_db_set")],
            [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="add_channels_menu")]
        ]))

    elif data in ["global_fs_menu", "forcesub_on", "forcesub_off"]:
        if data == "forcesub_on":
            await set_force_sub_status(True)
        elif data == "forcesub_off":
            await set_force_sub_status(False)

        is_on = await get_force_sub_status()
        status = "ᴏɴ ✅" if is_on else "ᴏꜰꜰ ❌"
        current_fs = await get_global_fs_channels()
        fs_str = "\n".join([f"• <code>{ch}</code>" for ch in current_fs]) if current_fs else "ɴᴏɴᴇ"
        
        text = (
            f"📢 <b>ꜰᴏʀᴄᴇ ꜱᴜʙ ᴄʜᴀɴɴᴇʟꜱ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ</b>\n\n"
            f"ᴄᴜʀʀᴇɴᴛ ꜱᴛᴀᴛᴜꜱ: <b>{status}</b>\n\n"
            f"ᴄᴜʀʀᴇɴᴛ ᴄʜᴀɴɴᴇʟꜱ:\n{fs_str}"
        )
        return await safe_edit(query.message, text, InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ ᴇɴᴀʙʟᴇ", callback_data="forcesub_on"), InlineKeyboardButton("❌ ᴅɪꜱᴀʙʟᴇ", callback_data="forcesub_off")],
            [InlineKeyboardButton("✏️ ᴄʜᴀɴɢᴇ ᴄʜᴀɴɴᴇʟꜱ", callback_data="global_fs_set")],
            [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="add_channels_menu")]
        ]))

    elif data == "global_fs_set":
        back_keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="global_fs_menu")]])
        await safe_edit(query.message, "📢 <b>ꜱᴇᴛ ꜰᴏʀᴄᴇ ꜱᴜʙ ᴄʜᴀɴɴᴇʟꜱ</b>\n\nꜱᴇɴᴅ ɴᴇᴡ ꜰᴏʀᴄᴇ ꜱᴜʙ ᴄʜᴀɴɴᴇʟ ɪᴅꜱ (ꜱᴘᴀᴄᴇ ꜱᴇᴘᴀʀᴀᴛᴇᴅ, ᴏʀ 0 ᴛᴏ ᴄʟᴇᴀʀ)\n\n/cancel - ᴄᴀɴᴄᴇʟ.", back_keyboard)
        try:
            input_msg = await client.listen(chat_id=query.message.chat.id, timeout=60)
        except ListenerTimeout:
            return await safe_edit(query.message, "📢 <b>ꜰᴏʀᴄᴇ ꜱᴜʙ ᴄʜᴀɴɴᴇʟꜱ</b>", back_keyboard)

        text_input = input_msg.text or ""
        try: await input_msg.delete()
        except: pass

        if not text_input or text_input.lower() == "/cancel":
            return await safe_edit(query.message, "❌ <b>ᴘʀᴏᴄᴇꜱꜱ ᴄᴀɴᴄᴇʟʟᴇᴅ!</b>\n\n📢 <b>ꜰᴏʀᴄᴇ ꜱᴜʙ ᴄʜᴀɴɴᴇʟꜱ</b>", InlineKeyboardMarkup([[InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="global_fs_menu")]]))

        new_channels = []
        if text_input.strip() != "0":
            for item in text_input.split():
                try:
                    ch = int(item)
                    if str(ch).startswith("-100"): new_channels.append(ch)
                except Exception: pass

        await set_global_fs_channels(new_channels)
        is_on = await get_force_sub_status()
        status = "ᴏɴ ✅" if is_on else "ᴏꜰꜰ ❌"
        fs_str = "\n".join([f"• <code>{ch}</code>" for ch in new_channels]) if new_channels else "ɴᴏɴᴇ"
        text = (
            f"✅ <b>ꜰꜱ ᴄʜᴀɴɴᴇʟꜱ ᴜᴘᴅᴀᴛᴇᴅ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ!</b>\n\n"
            f"ᴄᴜʀʀᴇɴᴛ ꜱᴛᴀᴛᴜꜱ: {status}\n\n"
            f"ᴄᴜʀʀᴇɴᴛ ᴄʜᴀɴɴᴇʟꜱ:\n{fs_str}"
        )
        return await safe_edit(query.message, text, InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ ᴇɴᴀʙʟᴇ", callback_data="forcesub_on"), InlineKeyboardButton("❌ ᴅɪꜱᴀʙʟᴇ", callback_data="forcesub_off")],
            [InlineKeyboardButton("✏️ ᴄʜᴀɴɢᴇ ᴄʜᴀɴɴᴇʟꜱ", callback_data="global_fs_set")],
            [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="add_channels_menu")]
        ]))
        
