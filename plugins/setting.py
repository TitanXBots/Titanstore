import asyncio
from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from pyromod.exceptions import ListenerTimeout
from config import START_PIC
from helper_func import safe_edit
from database.database import (
    is_admin, is_premium, get_tenant_config,
    get_protect_status, set_protect_status, 
    get_force_sub_status, set_force_sub_status,
    get_file_again_status, set_file_again_status,
    get_global_db_channel, set_global_db_channel,
    get_global_fs_channels, set_global_fs_channels,
    get_refer_status, set_refer_status, 
    get_refer_points, set_refer_points
)

async def delayed_delete(message, delay=7):
    await asyncio.sleep(delay)
    try: await message.delete()
    except: pass

@Client.on_callback_query(filters.regex("^(settings|admin_panel|protect_menu|protect_on|protect_off|forcesub_on|forcesub_off|getfileagain_menu|getfileagain_on|getfileagain_off|global_db_menu|global_db_set|global_fs_menu|global_fs_set|refer_menu|refer_on|refer_off|refer_set_points)$"))
async def settings_cb(client: Client, query: CallbackQuery):
    user_id = query.from_user.id
    is_user_admin = await is_admin(user_id)
    data = query.data

    if data == "settings":
        if is_user_admin:
            return await safe_edit(query.message, "⚙️ ᴀᴅᴍɪɴ ꜱᴇᴛᴛɪɴɢ ᴘᴀɴᴇʟ", InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("👨‍💻 ᴀᴅᴍɪɴ ᴍᴇɴᴜ", callback_data="admin_menu"), 
                    InlineKeyboardButton("🚫 ʙᴀɴ ᴍᴇɴᴜ", callback_data="ban_menu")
                ],
                [
                    InlineKeyboardButton("💎 ᴘʀᴇᴍɪᴜᴍ ᴍᴇɴᴜ", callback_data="premium_menu"), 
                    InlineKeyboardButton("🗑 ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ", callback_data="autodelete_menu")
                ],
                [
                    InlineKeyboardButton("🔒 ᴘʀᴏᴛᴇᴄᴛ ᴄᴏɴᴛᴇɴᴛ", callback_data="protect_menu"),
                    InlineKeyboardButton("♻️ ɢᴇᴛ ꜰɪʟᴇ ᴀɢᴀɪɴ", callback_data="getfileagain_menu")
                ],
                [
                    InlineKeyboardButton("📁 ɢʟᴏʙᴀʟ ᴅʙ", callback_data="global_db_menu"),
                    InlineKeyboardButton("📢 ɢʟᴏʙᴀʟ ꜰꜱ", callback_data="global_fs_menu")
                ],
                [
                    InlineKeyboardButton("🎁 ʀᴇꜰᴇʀʀᴀʟ ᴍᴇɴᴜ", callback_data="refer_menu")
                ],
                [
                    InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="start")
                ]
            ]))
        else:
            is_prem = await is_premium(user_id)
            status = "💎 ᴘʀᴇᴍɪᴜﾑ" if is_prem else "🆓 ꜰʀᴇᴇ"
            
            text = (
                f"👤 <b>ᴜꜱᴇʀ ᴘʀᴏꜰɪʟᴇ & ꜱᴇᴛᴛɪɴɢꜱ</b>\n\n"
                f"🆔 <b>ᴜꜱᴇʀ ɪᴅ:</b> <code>{user_id}</code>\n"
                f"📊 <b>ꜱᴛᴀᴛᴜꜱ:</b> {status}\n\n"
            )
            
            buttons = []
            
            # --- NEW FIX: SHOW BUTTON TO EVERYONE! ---
            if not is_prem:
                text += "<i>ᴜᴘɢʀᴀᴅᴇ ᴛᴏ ᴘʀᴇᴍɪᴜᴍ ᴛᴏ ʜᴏꜱᴛ ʏᴏᴜʀ ᴏᴡɴ ꜰɪʟᴇ ᴄʜᴀɴɴᴇʟꜱ.</i>"
                buttons.append([InlineKeyboardButton("🍁 ᴄʜᴇᴄᴋ ᴀʟʟ ᴘʟᴀɴꜱ & ᴘʀɪᴄᴇꜱ 🍁", callback_data="buy_plans")])
                # Show the button with a Lock to free users
                buttons.append([InlineKeyboardButton("🔒 ꜱᴇᴛᴜᴘ ᴄʜᴀɴɴᴇʟꜱ", callback_data="user_connect_req")])
            
            if is_prem:
                tenant = await get_tenant_config(user_id)
                if tenant:
                    fs_str = ", ".join([f"<code>{x}</code>" for x in tenant['fs_channels']])
                    text += (
                        f"📁 <b>ʏᴏᴜʀ ᴅʙ ᴄʜᴀɴɴᴇʟ:</b> <code>{tenant['db_channel']}</code>\n"
                        f"📢 <b>ʏᴏᴜʀ ꜰꜱ ᴄʜᴀɴɴᴇʟꜱ:</b> {fs_str}\n\n"
                    )
                    buttons.append([InlineKeyboardButton("🔌 ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟꜱ", callback_data="user_connect_req")])
                else:
                    text += "<i>ʏᴏᴜ ᴀʀᴇ ᴀ ᴘʀᴇᴍɪᴜᴍ ᴍᴇᴍʙᴇʀ!\nᴄʟɪᴄᴋ ʙᴇʟᴏᴡ ᴛᴏ ꜱᴇᴛᴜᴘ ʏᴏᴜʀ ᴏᴡɴ ꜰɪʟᴇ ꜱᴛᴏʀᴇ ᴄʜᴀɴɴᴇʟꜱ.</i>"
                    buttons.append([InlineKeyboardButton("🔌 ꜱᴇᴛᴜᴘ ᴄʜᴀɴɴᴇʟꜱ", callback_data="user_connect_req")])
            
            buttons.append([InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="start")])
            return await safe_edit(query.message, text, InlineKeyboardMarkup(buttons))

    if not is_user_admin:
        return await query.answer("⚠️ ᴀᴄᴄᴇꜱꜱ ᴅᴇɴɪᴇᴅ: ᴀᴅᴍɪɴꜱ ᴏɴʟʏ!", show_alert=True)

    if data == "refer_menu":
        is_on = await get_refer_status()
        status = "ᴏɴ ✅" if is_on else "ᴏꜰꜰ ❌"
        points = await get_refer_points()
        
        text = (
            f"🎁 <b>ʀᴇꜰᴇʀ & ᴇᴀʀɴ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ</b>\n\n"
            f"ᴄᴜʀʀᴇɴᴛ ꜱᴛᴀᴛᴜꜱ: <b>{status}</b>\n"
            f"ᴘᴏɪɴᴛꜱ ᴘᴇʀ ʀᴇꜰᴇʀʀᴀʟ: <b>{points}</b>"
        )
        return await safe_edit(query.message, text, InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ ᴇɴᴀʙʟᴇ", callback_data="refer_on"), InlineKeyboardButton("❌ ᴅɪꜱᴀʙʟᴇ", callback_data="refer_off")],
            [InlineKeyboardButton("✏️ ᴄʜᴀɴɢᴇ ᴘᴏɪɴᴛꜱ", callback_data="refer_set_points")],
            [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="settings")]
        ]))

    elif data == "refer_on":
        if await get_refer_status():
            return await query.answer("⚠️ ʀᴇꜰᴇʀ ꜱʏꜱᴛᴇᴍ ɪꜱ ᴀʟʀᴇᴀᴅʏ ᴏɴ!", show_alert=True)
        await set_refer_status(True)
        await query.answer("✅ ʀᴇꜰᴇʀ ꜱʏꜱᴛᴇᴍ ᴇɴᴀʙʟᴇᴅ!", show_alert=True)
        points = await get_refer_points()
        text = (
            f"🎁 <b>ʀᴇꜰᴇʀ & ᴇᴀʀɴ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ</b>\n\n"
            f"ᴄᴜʀʀᴇɴᴛ ꜱᴛᴀᴛᴜꜱ: <b>ᴏɴ ✅</b>\n"
            f"ᴘᴏɪɴᴛꜱ ᴘᴇʀ ʀᴇꜰᴇʀʀᴀʟ: <b>{points}</b>"
        )
        return await safe_edit(query.message, text, InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ ᴇɴᴀʙʟᴇ", callback_data="refer_on"), InlineKeyboardButton("❌ ᴅɪꜱᴀʙʟᴇ", callback_data="refer_off")],
            [InlineKeyboardButton("✏️ ᴄʜᴀɴɢᴇ ᴘᴏɪɴᴛꜱ", callback_data="refer_set_points")],
            [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="settings")]
        ]))

    elif data == "refer_off":
        if not await get_refer_status():
            return await query.answer("⚠️ ʀᴇꜰᴇʀ ꜱʏꜱᴛᴇᴍ ɪꜱ ᴀʟʀᴇᴀᴅʏ ᴏꜰꜰ!", show_alert=True)
        await set_refer_status(False)
        await query.answer("❌ ʀᴇꜰᴇʀ ꜱʏꜱᴛᴇᴍ ᴅɪꜱᴀʙʟᴇᴅ!", show_alert=True)
        points = await get_refer_points()
        text = (
            f"🎁 <b>ʀᴇꜰᴇʀ & ᴇᴀʀɴ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ</b>\n\n"
            f"ᴄᴜʀʀᴇɴᴛ ꜱᴛᴀᴛᴜꜱ: <b>ᴏꜰꜰ ❌</b>\n"
            f"ᴘᴏɪɴᴛꜱ ᴘᴇʀ ʀᴇꜰᴇʀʀᴀʟ: <b>{points}</b>"
        )
        return await safe_edit(query.message, text, InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ ᴇɴᴀʙʟᴇ", callback_data="refer_on"), InlineKeyboardButton("❌ ᴅɪꜱᴀʙʟᴇ", callback_data="refer_off")],
            [InlineKeyboardButton("✏️ ᴄʜᴀɴɢᴇ ᴘᴏɪɴᴛꜱ", callback_data="refer_set_points")],
            [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="settings")]
        ]))

    elif data == "refer_set_points":
        back_keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="refer_menu")]])
        prompt_text = (
            "<b>ꜱᴇɴᴅ ɴᴇᴡ ᴘᴏɪɴᴛꜱ ᴘᴇʀ ʀᴇꜰᴇʀʀᴀʟ (ᴇ.ɢ., 10, 20)\n\n"
            "/cancel - ᴄᴀɴᴄᴇʟ ᴛʜɪꜱ ᴘʀᴏᴄᴇꜱꜱ.</b>"
        )
        await safe_edit(query.message, prompt_text, back_keyboard)
        try:
            input_msg = await client.listen(query.message.chat.id, timeout=60)
        except ListenerTimeout:
            await query.answer("⌛ ᴛɪᴍᴇᴏᴜᴛ!", show_alert=True)
            is_on = await get_refer_status()
            status = "ᴏɴ ✅" if is_on else "ᴏꜰꜰ ❌"
            points = await get_refer_points()
            text = (
                f"🎁 <b>ʀᴇꜰᴇʀ & ᴇᴀʀɴ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ</b>\n\n"
                f"ᴄᴜʀʀᴇɴᴛ ꜱᴛᴀᴛᴜꜱ: <b>{status}</b>\n"
                f"ᴘᴏɪɴᴛꜱ ᴘᴇʀ ʀᴇꜰᴇʀʀᴀʟ: <b>{points}</b>"
            )
            return await safe_edit(query.message, text, InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ ᴇɴᴀʙʟᴇ", callback_data="refer_on"), InlineKeyboardButton("❌ ᴅɪꜱᴀʙʟᴇ", callback_data="refer_off")],
                [InlineKeyboardButton("✏️ ᴄʜᴀɴɢᴇ ᴘᴏɪɴᴛꜱ", callback_data="refer_set_points")],
                [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="settings")]
            ]))

        text_input = input_msg.text or ""
        try: await input_msg.delete()
        except: pass

        if not text_input or text_input.lower() == "/cancel":
            await query.answer("❌ ᴄᴀɴᴄᴇʟʟᴇᴅ!", show_alert=True)
            is_on = await get_refer_status()
            status = "ᴏɴ ✅" if is_on else "ᴏꜰꜰ ❌"
            points = await get_refer_points()
            text = (
                f"🎁 <b>ʀᴇꜰᴇʀ & ᴇᴀʀɴ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ</b>\n\n"
                f"ᴄᴜʀʀᴇɴᴛ ꜱᴛᴀᴛᴜꜱ: <b>{status}</b>\n"
                f"ᴘᴏɪɴᴛꜱ ᴘᴇʀ ʀᴇꜰᴇʀʀᴀʟ: <b>{points}</b>"
            )
            return await safe_edit(query.message, text, InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ ᴇɴᴀʙʟᴇ", callback_data="refer_on"), InlineKeyboardButton("❌ ᴅɪꜱᴀʙʟᴇ", callback_data="refer_off")],
                [InlineKeyboardButton("✏️ ᴄʜᴀɴɢᴇ ᴘᴏɪɴᴛꜱ", callback_data="refer_set_points")],
                [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="settings")]
            ]))

        try:
            new_pts = int(text_input)
            if new_pts < 0: raise ValueError
        except Exception:
            msg = await query.message.reply_photo(photo=START_PIC, caption="❌ <b>ɪɴᴠᴀʟɪᴅ ɪɴᴘᴜᴛ!</b> ᴍᴜꜱᴛ ʙᴇ ᴀ ᴘᴏꜱɪᴛɪᴠᴇ ɴᴜᴍʙᴇʀ.", reply_markup=back_keyboard)
            asyncio.create_task(delayed_delete(msg))
            is_on = await get_refer_status()
            status = "ᴏɴ ✅" if is_on else "ᴏꜰꜰ ❌"
            points = await get_refer_points()
            text = (
                f"🎁 <b>ʀᴇꜰᴇʀ & ᴇᴀʀɴ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ</b>\n\n"
                f"ᴄᴜʀʀᴇɴᴛ ꜱᴛᴀᴛᴜꜱ: <b>{status}</b>\n"
                f"ᴘᴏɪɴᴛꜱ ᴘᴇʀ ʀᴇꜰᴇʀʀᴀʟ: <b>{points}</b>"
            )
            return await safe_edit(query.message, text, InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ ᴇɴᴀʙʟᴇ", callback_data="refer_on"), InlineKeyboardButton("❌ ᴅɪꜱᴀʙʟᴇ", callback_data="refer_off")],
                [InlineKeyboardButton("✏️ ᴄʜᴀɴɢᴇ ᴘᴏɪɴᴛꜱ", callback_data="refer_set_points")],
                [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="settings")]
            ]))

        await set_refer_points(new_pts)
        msg = await query.message.reply_photo(photo=START_PIC, caption=f"✅ <b>ʀᴇꜰᴇʀʀᴀʟ ᴘᴏɪɴᴛꜱ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ᴜᴘᴅᴀᴛᴇᴅ ᴛᴏ:</b> <code>{new_pts}</code>", reply_markup=back_keyboard)
        asyncio.create_task(delayed_delete(msg))
        is_on = await get_refer_status()
        status = "ᴏɴ ✅" if is_on else "ᴏꜰꜰ ❌"
        text = (
            f"🎁 <b>ʀᴇꜰᴇʀ & ᴇᴀʀɴ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ</b>\n\n"
            f"ᴄᴜʀʀᴇɴᴛ ꜱᴛᴀᴛᴜꜱ: <b>{status}</b>\n"
            f"ᴘᴏɪɴᴛꜱ ᴘᴇʀ ʀᴇꜰᴇʀʀᴀʟ: <b>{new_pts}</b>"
        )
        return await safe_edit(query.message, text, InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ ᴇɴᴀʙʟᴇ", callback_data="refer_on"), InlineKeyboardButton("❌ ᴅɪꜱᴀʙʟᴇ", callback_data="refer_off")],
            [InlineKeyboardButton("✏️ ᴄʜᴀɴɢᴇ ᴘᴏɪɴᴛꜱ", callback_data="refer_set_points")],
            [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="settings")]
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
            [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="settings")]
        ]))

    elif data == "protect_on":
        if await get_protect_status():
            return await query.answer("⚠️ ᴘʀᴏᴛᴇᴄᴛ ᴄᴏɴᴛᴇɴᴛ ɪꜱ ᴀʟʀᴇᴀᴅʏ ᴏɴ!", show_alert=True)
        await set_protect_status(True)
        await query.answer("✅ ᴘʀᴏᴛᴇᴄᴛ ᴄᴏɴᴛᴇɴᴛ ᴇɴᴀʙʟᴇᴅ!", show_alert=True)
        text = (
            f"🔒 <b>ᴘʀᴏᴛᴇᴄᴛ ᴄᴏɴᴛᴇɴᴛ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ</b>\n\n"
            f"ᴄᴜʀʀᴇɴᴛ ꜱᴛᴀᴛᴜꜱ: <b>ᴏɴ ✅</b>"
        )
        return await safe_edit(query.message, text, InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ ᴇɴᴀʙʟᴇ", callback_data="protect_on"), InlineKeyboardButton("❌ ᴅɪꜱᴀʙʟᴇ", callback_data="protect_off")], 
            [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="settings")]
        ]))

    elif data == "protect_off":
        if not await get_protect_status():
            return await query.answer("⚠️ ᴘʀᴏᴛᴇᴄᴛ ᴄᴏɴᴛᴇɴᴛ ɪꜱ ᴀʟʀᴇᴀᴅʏ ᴏꜰꜰ!", show_alert=True)
        await set_protect_status(False)
        await query.answer("❌ ᴘʀᴏᴛᴇᴄᴛ ᴄᴏɴᴛᴇɴᴛ ᴅɪꜱᴀʙʟᴇᴅ!", show_alert=True)
        text = (
            f"🔒 <b>ᴘʀᴏᴛᴇᴄᴛ ᴄᴏɴᴛᴇɴᴛ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ</b>\n\n"
            f"ᴄᴜʀʀᴇɴᴛ ꜱᴛᴀᴛᴜꜱ: <b>ᴏꜰꜰ ❌</b>"
        )
        return await safe_edit(query.message, text, InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ ᴇɴᴀʙʟᴇ", callback_data="protect_on"), InlineKeyboardButton("❌ ᴅɪꜱᴀʙʟᴇ", callback_data="protect_off")], 
            [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="settings")]
        ]))

    elif data == "getfileagain_menu":
        is_on = await get_file_again_status()
        status = "ᴏɴ ✅" if is_on else "ᴏꜰꜰ ❌"
        text = (
            f"♻️ <b>ɢᴇᴛ ꜰɪʟᴇ ᴀɢᴀɪɴ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ</b>\n\n"
            f"ꜱʜᴏᴡ 'ɢᴇᴛ ꜰɪʟᴇ ᴀɢᴀɪɴ' ʙᴜᴛᴛᴏɴ ᴀꜰᴛᴇʀ ꜰɪʟᴇ ᴀᴜᴛᴏ-ᴅᴇʟᴇᴛɪᴏɴ.\n\n"
            f"ᴄᴜʀʀᴇɴᴛ ꜱᴛᴀᴛᴜꜱ: <b>{status}</b>"
        )
        return await safe_edit(query.message, text, InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ ᴇɴᴀʙʟᴇ", callback_data="getfileagain_on"), InlineKeyboardButton("❌ ᴅɪꜱᴀʙʟᴇ", callback_data="getfileagain_off")],
            [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="settings")]
        ]))

    elif data == "getfileagain_on":
        if await get_file_again_status():
            return await query.answer("⚠️ ɢᴇᴛ ꜰɪʟᴇ ᴀɢᴀɪɴ ɪꜱ ᴀʟʀᴇᴀᴅʏ ᴏɴ!", show_alert=True)
        await set_file_again_status(True)
        await query.answer("✅ ɢᴇᴛ ꜰɪʟᴇ ᴀɢᴀɪɴ ᴇɴᴀʙʟᴇᴅ!", show_alert=True)
        text = (
            f"♻️ <b>ɢᴇᴛ ꜰɪʟᴇ ᴀɢᴀɪɴ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ</b>\n\n"
            f"ᴄᴜʀʀᴇɴᴛ ꜱᴛᴀᴛᴜꜱ: <b>ᴏɴ ✅</b>"
        )
        return await safe_edit(query.message, text, InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ ᴇɴᴀʙʟᴇ", callback_data="getfileagain_on"), InlineKeyboardButton("❌ ᴅɪꜱᴀʙʟᴇ", callback_data="getfileagain_off")], 
            [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="settings")]
        ]))

    elif data == "getfileagain_off":
        if not await get_file_again_status():
            return await query.answer("⚠️ ɢᴇᴛ ꜰɪʟᴇ ᴀɢᴀɪɴ ɪꜱ ᴀʟʀᴇᴀᴅʏ ᴏꜰꜰ!", show_alert=True)
        await set_file_again_status(False)
        await query.answer("❌ ɢᴇᴛ ꜰɪʟᴇ ᴀɢᴀɪɴ ᴅɪꜱᴀʙʟᴇᴅ!", show_alert=True)
        text = (
            f"♻️ <b>ɢᴇᴛ ꜰɪʟᴇ ᴀɢᴀɪɴ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ</b>\n\n"
            f"ᴄᴜʀʀᴇɴᴛ ꜱᴛᴀᴛᴜꜱ: <b>ᴏꜰꜰ ❌</b>"
        )
        return await safe_edit(query.message, text, InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ ᴇɴᴀʙʟᴇ", callback_data="getfileagain_on"), InlineKeyboardButton("❌ ᴅɪꜱᴀʙʟᴇ", callback_data="getfileagain_off")], 
            [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="settings")]
        ]))

    elif data == "global_db_menu":
        current_db = await get_global_db_channel()
        text = (
            f"📁 <b>ᴅᴀᴛᴀʙᴀꜱᴇ ᴄʜᴀɴɴᴇʟ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ</b>\n\n"
            f"ᴄᴜʀʀᴇɴᴛ ᴅʙ ᴄʜᴀɴɴᴇʟ ɪᴅ: <code>{current_db}</code>"
        )
        return await safe_edit(query.message, text, InlineKeyboardMarkup([
            [InlineKeyboardButton("✏️ ᴄʜᴀɴɢᴇ ᴅʙ ᴄʜᴀɴɴᴇʟ", callback_data="global_db_set")],
            [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="settings")]
        ]))

    elif data == "global_db_set":
        back_keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="global_db_menu")]])
        prompt_text = (
            "<b>ꜱᴇɴᴅ ɴᴇᴡ ᴅᴀᴛᴀʙᴀꜱᴇ ᴄʜᴀɴɴᴇʟ ɪᴅ (ᴍᴜꜱᴛ ꜱᴛᴀʀᴛ ᴡɪᴛʜ -100)\n\n"
            "/cancel - ᴄᴀɴᴄᴇʟ ᴛʜɪꜱ ᴘʀᴏᴄᴇꜱꜱ.</b>"
        )
        await safe_edit(query.message, prompt_text, back_keyboard)
        try:
            input_msg = await client.listen(query.message.chat.id, timeout=60)
        except ListenerTimeout:
            await query.answer("⌛ ᴛɪᴍᴇᴏᴜᴛ!", show_alert=True)
            current_db = await get_global_db_channel()
            text = (
                f"📁 <b>ᴅᴀᴛᴀʙᴀꜱᴇ ᴄʜᴀɴɴᴇʟ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ</b>\n\n"
                f"ᴄᴜʀʀᴇɴᴛ ᴅʙ ᴄʜᴀɴɴᴇʟ ɪᴅ: <code>{current_db}</code>"
            )
            return await safe_edit(query.message, text, InlineKeyboardMarkup([
                [InlineKeyboardButton("✏️ ᴄʜᴀɴɢᴇ ᴅʙ ᴄʜᴀɴɴᴇʟ", callback_data="global_db_set")],
                [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="settings")]
            ]))

        text_input = input_msg.text or ""
        try: await input_msg.delete()
        except: pass

        if not text_input or text_input.lower() == "/cancel":
            await query.answer("❌ ᴄᴀɴᴄᴇʟʟᴇᴅ!", show_alert=True)
            current_db = await get_global_db_channel()
            text = (
                f"📁 <b>ᴅᴀᴛᴀʙᴀꜱᴇ ᴄʜᴀɴɴᴇʟ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ</b>\n\n"
                f"ᴄᴜʀʀᴇɴᴛ ᴅʙ ᴄʜᴀɴɴᴇʟ ɪᴅ: <code>{current_db}</code>"
            )
            return await safe_edit(query.message, text, InlineKeyboardMarkup([
                [InlineKeyboardButton("✏️ ᴄʜᴀɴɢᴇ ᴅʙ ᴄʜᴀɴɴᴇʟ", callback_data="global_db_set")],
                [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="settings")]
            ]))

        try:
            new_id = int(text_input)
            if not str(new_id).startswith("-100"):
                raise ValueError("Must start with -100")
        except Exception:
            msg = await query.message.reply_photo(photo=START_PIC, caption="❌ <b>ɪɴᴠᴀʟɪᴅ ɪᴅ!</b> ᴍᴜꜱᴛ ʙᴇ A ᴠᴀʟɪᴅ Nᴜᴍʙᴇʀ ꜱᴛᴀʀᴛɪɴɢ ᴡɪᴛʜ -100.", reply_markup=back_keyboard)
            asyncio.create_task(delayed_delete(msg))
            current_db = await get_global_db_channel()
            text = (
                f"📁 <b>ᴅᴀᴛᴀʙᴀꜱᴇ ᴄʜᴀɴɴᴇʟ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ</b>\n\n"
                f"ᴄᴜʀʀᴇɴᴛ ᴅʙ ᴄʜᴀɴɴᴇʟ ɪᴅ: <code>{current_db}</code>"
            )
            return await safe_edit(query.message, text, InlineKeyboardMarkup([
                [InlineKeyboardButton("✏️ ᴄʜᴀɴɢᴇ ᴅʙ ᴄʜᴀɴɴᴇʟ", callback_data="global_db_set")],
                [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="settings")]
            ]))

        await set_global_db_channel(new_id)
        try: client.db_channel = await client.get_chat(new_id)
        except Exception as e:
            msg = await query.message.reply_photo(photo=START_PIC, caption=f"⚠️ <b>Wᴀʀɴɪɴɢ:</b> ID ᴜᴘᴅᴀᴛᴇᴅ, ʙᴜᴛ ʙᴏᴛ ᴍɪɢʜᴛ ɴᴏᴛ ʙᴇ ᴀᴅᴍɪɴ! Eʀʀᴏʀ: {e}", reply_markup=back_keyboard)
            asyncio.create_task(delayed_delete(msg))
        
        msg = await query.message.reply_photo(photo=START_PIC, caption=f"✅ <b>ɢʟᴏʙᴀʟ ᴅᴀᴛᴀʙᴀꜱᴇ ᴄʜᴀɴɴᴇʟ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ᴜᴘᴅᴀᴛᴇᴅ:</b> <code>{new_id}</code>", reply_markup=back_keyboard)
        asyncio.create_task(delayed_delete(msg))
        
        text = (
            f"📁 <b>ᴅᴀᴛᴀʙᴀꜱᴇ ᴄʜᴀɴɴᴇʟ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ</b>\n\n"
            f"ᴄᴜʀʀᴇɴᴛ ᴅʙ ᴄʜᴀɴɴᴇʟ ɪᴅ: <code>{new_id}</code>"
        )
        return await safe_edit(query.message, text, InlineKeyboardMarkup([
            [InlineKeyboardButton("✏️ ᴄʜᴀɴɢᴇ ᴅʙ ᴄʜᴀɴɴᴇʟ", callback_data="global_db_set")],
            [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="settings")]
        ]))

    elif data in ["global_fs_menu", "forcesub_on", "forcesub_off"]:
        if data == "forcesub_on":
            if await get_force_sub_status(): await query.answer("⚠️ ꜰᴏʀᴄᴇ ꜱᴜʙ ɪꜱ ᴀʟʀᴇᴀᴅʏ ᴏɴ!", show_alert=True)
            else:
                await set_force_sub_status(True)
                await query.answer("✅ ꜰᴏʀᴄᴇ ꜱᴜʙ ᴇɴᴀʙʟᴇᴅ!", show_alert=True)
        elif data == "forcesub_off":
            if not await get_force_sub_status(): await query.answer("⚠️ ꜰᴏʀᴄᴇ ꜱᴜʙ ɪꜱ ᴀʟʀᴇᴀᴅʏ ᴏꜰꜰ!", show_alert=True)
            else:
                await set_force_sub_status(False)
                await query.answer("❌ ꜰᴏʀᴄᴇ ꜱᴜʙ ᴅɪꜱᴀʙʟᴇᴅ!", show_alert=True)

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
            [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="settings")]
        ]))

    elif data == "global_fs_set":
        back_keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="global_fs_menu")]])
        prompt_text = (
            "<b>ꜱᴇɴᴅ ɴᴇᴡ ꜰᴏʀᴄᴇ ꜱᴜʙ ᴄʜᴀɴɴᴇʟ ɪᴅꜱ (ꜱᴘᴀᴄᴇ ꜱᴇᴘᴀʀᴀᴛᴇᴅ, ᴏʀ 0 ᴛᴏ ᴄʟᴇᴀʀ)\n\n"
            "ᴇxᴀᴍᴘʟᴇ: <code>-100123456789 -100987654321</code>\n\n"
            "/cancel - ᴄᴀɴᴄᴇʟ ᴛʜɪꜱ ᴘʀᴏᴄᴇꜱꜱ.</b>"
        )
        await safe_edit(query.message, prompt_text, back_keyboard)
        
        try:
            input_msg = await client.listen(query.message.chat.id, timeout=60)
        except ListenerTimeout:
            await query.answer("⌛ ᴛɪᴍᴇᴏᴜᴛ!", show_alert=True)
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
                [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="settings")]
            ]))

        text_input = input_msg.text or ""
        try: await input_msg.delete()
        except: pass

        if not text_input or text_input.lower() == "/cancel":
            await query.answer("❌ ᴄᴀɴᴄᴇʟʟᴇᴅ!", show_alert=True)
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
                [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="settings")]
            ]))

        new_channels = []
        if text_input.strip() != "0":
            for item in text_input.split():
                try:
                    ch = int(item)
                    if str(ch).startswith("-100"): new_channels.append(ch)
                except Exception: pass

        await set_global_fs_channels(new_channels)
        
        msg = await query.message.reply_photo(photo=START_PIC, caption=f"✅ <b>ɢʟᴏʙᴀʟ ꜰᴏʀᴄᴇ ꜱᴜʙ ᴄʜᴀɴɴᴇʟꜱ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ᴜᴘᴅᴀᴛᴇᴅ!</b>", reply_markup=back_keyboard)
        asyncio.create_task(delayed_delete(msg))
        
        is_on = await get_force_sub_status()
        status = "ᴏɴ ✅" if is_on else "ᴏꜰꜰ ❌"
        fs_str = "\n".join([f"• <code>{ch}</code>" for ch in new_channels]) if new_channels else "ɴᴏɴᴇ"
        text = (
            f"📢 <b>ꜰᴏʀᴄᴇ ꜱᴜʙ ᴄʜᴀɴɴᴇʟꜱ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ</b>\n\n"
            f"ᴄᴜʀʀᴇɴᴛ ꜱᴛᴀᴛᴜꜱ: {status}\n\n"
            f"ᴄᴜʀʀᴇɴᴛ ᴄʜᴀɴɴᴇʟꜱ:\n{fs_str}"
        )
        return await safe_edit(query.message, text, InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ ᴇɴᴀʙʟᴇ", callback_data="forcesub_on"), InlineKeyboardButton("❌ ᴅɪꜱᴀʙʟᴇ", callback_data="forcesub_off")],
            [InlineKeyboardButton("✏️ ᴄʜᴀɴɢᴇ ᴄʜᴀɴɴᴇʟꜱ", callback_data="global_fs_set")],
            [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="settings")]
        ]))
