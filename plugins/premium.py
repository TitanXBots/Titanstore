from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyromod.exceptions import ListenerTimeout
from helper_func import safe_edit
from database.database import (
    get_premium_status, get_user, add_referral_points, set_premium, 
    remove_premium, is_admin, submit_channel, get_user_approved_channels, set_channel_status
)
from config import OWNER_USERNAME, POINTS_TO_PREMIUM, PREMIUM_DAYS, LOG_CHANNEL_ID

# --- UI RENDER FUNCTION ---
async def render_dashboard(client, message, user_id):
    user = await get_user(user_id)
    points = user.get("points", 0) if user else 0
    is_prem = await get_premium_status(user_id)
    
    status = "👑 ᴘʀᴇᴍɪᴜᴍ" if is_prem else "🆓 ꜰʀᴇᴇ"
    
    text = (
        f"👤 **ʏᴏᴜʀ ᴀᴄᴄᴏᴜɴᴛ ᴅᴀꜱʜʙᴏᴀʀᴅ**\n\n"
        f"🆔 **ᴜꜱᴇʀ ɪᴅ:** <code>{user_id}</code>\n"
        f"📊 **ꜱᴛᴀᴛᴜꜱ:** {status}\n"
        f"🪙 **ᴘᴏɪɴᴛꜱ:** {points}/{POINTS_TO_PREMIUM}\n\n"
        f"🎁 **ʜᴏᴡ ᴛᴏ ɢᴇᴛ ꜰʀᴇᴇ ᴘʀᴇᴍɪᴜᴍ?**\n"
        f"ꜱʜᴀʀᴇ ʏᴏᴜʀ ʟɪɴᴋ & ɢᴇᴛ 10 ᴘᴏɪɴᴛꜱ ᴘᴇʀ ɴᴇᴡ ᴜꜱᴇʀ.\n"
        f"🔗 <code>https://t.me/{client.me.username}?start=ref_{user_id}</code>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"🎖️ **ᴀᴠᴀɪʟᴀʙʟᴇ ᴘʀᴇᴍɪᴜᴍ ᴘʟᴀɴꜱ :**\n\n"
        f" ❏ 𝟶𝟷𝟻₹    ➠    𝟶𝟷 ᴡᴇᴇᴋꜱ\n"
        f" ❏ 𝟶𝟹𝟿₹    ➠    𝟶𝟷 ᴍᴏɴᴛʜ\n"
        f" ❏ 𝟶𝟽𝟻₹    ➠    𝟶𝟸 ᴍᴏɴᴛʜ\n"
        f" ❏ 𝟷𝟷𝟶₹    ➠    𝟶𝟹 ᴍᴏɴᴛʜ\n"
        f" ❏ 𝟷𝟿𝟿₹    ➠    𝟶𝟼 ᴍᴏɴᴛʜ\n"
        f" ❏ 𝟹𝟼𝟶₹    ➠    𝟷𝟸 ᴍᴏɴᴛʜ\n\n"
        f"🆔 ᴜᴘɪ ɪᴅ ➩ <code>kushalhari@slc</code> [ᴛᴀᴘ ᴛᴏ ᴄᴏᴘʏ]\n\n"
        f"‼️ ᴍᴜsᴛ sᴇɴᴅ sᴄʀᴇᴇɴsʜᴏᴛ ᴀғᴛᴇʀ ᴘᴀʏᴍᴇɴᴛ.\n"
        f"‼️ ɢɪᴠᴇ ᴜꜱ ꜱᴏᴍᴇᴛɪᴍᴇ ᴛᴏ ᴀᴅᴅ ʏᴏᴜ ɪɴ ᴘʀᴇᴍɪᴜᴍ ʟɪꜱᴛ.\n\n"
        f"**ᴏᴛʜᴇʀ ᴘʟᴀɴ**\n"
        f"⏰ ᴄᴜꜱᴛᴏᴍɪꜱᴇᴅ ᴅᴀʏꜱ\n"
        f"💸 ᴀᴄᴄᴏʀᴅɪɴɢ ᴛᴏ ᴅᴀʏꜱ ʏᴏᴜ ᴄʜᴏᴏꜱᴇ\n\n"
        f"🏆 ɪꜰ ʏᴏᴜ ᴡᴀɴᴛ ᴀ ɴᴇᴡ ᴘʟᴀɴ ᴀᴘᴀʀᴛ ꜰʀᴏᴍ ᴛʜᴇ ɢɪᴠᴇɴ ᴘʟᴀɴ, ᴛʜᴇɴ ʏᴏᴜ ᴄᴀɴ ᴛᴀʟᴋ ᴛᴏ ᴏᴜʀ ᴏᴡɴᴇʀ ᴅɪʀᴇᴄᴛʟʏ ʙʏ ᴄʟɪᴄᴋɪɴɢ ᴏɴ ᴛʜᴇ ᴄᴏɴᴛᴀᴄᴛ ʙᴜᴛᴛᴏɴ ɢɪᴠᴇɴ ʙᴇʟᴏᴡ."
    )
    
    buttons = [
        [InlineKeyboardButton("📸 ꜱᴇɴᴅ ꜱᴄʀᴇᴇɴꜱʜᴏᴛ", url=f"https://t.me/{OWNER_USERNAME}")],
        [InlineKeyboardButton("👨‍💻 ᴄᴏɴᴛᴀᴄᴛ ᴏᴡɴᴇʀ", url=f"https://t.me/{OWNER_USERNAME}"), InlineKeyboardButton("💳 ʀᴇᴅᴇᴇᴍ ᴘᴏɪɴᴛꜱ", callback_data="redeem_points")]
    ]
    
    if is_prem or await is_admin(user_id):
        buttons.append([InlineKeyboardButton("✏️ ꜱᴇᴛ ᴅʙ ᴄʜᴀɴɴᴇʟ", callback_data="set_user_db"), InlineKeyboardButton("📢 ꜱᴇᴛ ꜰꜱ ᴄʜᴀɴɴᴇʟꜱ", callback_data="set_user_fs")])
        buttons.append([InlineKeyboardButton("📊 ᴠɪᴇᴡ ᴍʏ ᴄʜᴀɴɴᴇʟꜱ", callback_data="view_user_channels")])
        
    buttons.append([InlineKeyboardButton("🔙 ʙᴀᴄᴋ ᴛᴏ ʜᴏᴍᴇ", callback_data="start")])
    await safe_edit(message, text, InlineKeyboardMarkup(buttons))


# --- COMMAND / PLAN ---
@Client.on_message(filters.command(["plan", "myplan", "mychannels"]) & filters.private)
async def plan_cmd(client, message):
    await render_dashboard(client, message, message.from_user.id)


# --- INLINE BUTTON CALLBACKS ---
@Client.on_callback_query(filters.regex("^(my_account|redeem_points|set_user_db|set_user_fs|view_user_channels)$"))
async def premium_ui_callbacks(client, query):
    try: await query.answer()
    except: pass
    
    user_id = query.from_user.id
    data = query.data

    if data == "my_account":
        return await render_dashboard(client, query.message, user_id)

    elif data == "redeem_points":
        user = await get_user(user_id)
        points = user.get("points", 0) if user else 0
        if points >= POINTS_TO_PREMIUM:
            await add_referral_points(user_id, -POINTS_TO_PREMIUM)
            await set_premium(user_id, PREMIUM_DAYS)
            await query.answer(f"🎉 ꜱᴜᴄᴄᴇꜱꜱ! ʏᴏᴜ ɴᴏᴡ ʜᴀᴠᴇ {PREMIUM_DAYS} ᴅᴀʏꜱ ᴏꜰ ᴘʀᴇᴍɪᴜᴍ.", show_alert=True)
            await render_dashboard(client, query.message, user_id)
        else:
            await query.answer(f"❌ ɴᴏᴛ ᴇɴᴏᴜɢʜ ᴘᴏɪɴᴛꜱ! (ʏᴏᴜ ʜᴀᴠᴇ {points}/{POINTS_TO_PREMIUM})", show_alert=True)

    elif data == "view_user_channels":
        u_db = await get_user_approved_channels(user_id, "db")
        u_fs = await get_user_approved_channels(user_id, "fs")
        db_txt = f"<code>{u_db[0]}</code>" if u_db else "None Approved"
        fs_txt = ", ".join([f"<code>{ch}</code>" for ch in u_fs]) if u_fs else "None Approved"
        text = f"📊 **ʏᴏᴜʀ ᴀᴘᴘʀᴏᴠᴇᴅ ᴄʜᴀɴɴᴇʟꜱ:**\n\n📁 **ᴅʙ ᴄʜᴀɴɴᴇʟ:** {db_txt}\n📢 **ꜰꜱ ᴄʜᴀɴɴᴇʟꜱ:** {fs_txt}"
        markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="my_account")]])
        await safe_edit(query.message, text, markup)

    elif data in ["set_user_db", "set_user_fs"]:
        if not await get_premium_status(user_id) and not await is_admin(user_id):
            return await query.answer("👑 ᴘʀᴇᴍɪᴜᴍ ʀᴇQᴜɪʀᴇᴅ ꜰᴏʀ ᴛʜɪꜱ ꜰᴇᴀᴛᴜʀᴇ!", show_alert=True)
            
        ch_type = "db" if data == "set_user_db" else "fs"
        prompt = "ꜱᴇɴᴅ ᴅʙ ᴄʜᴀɴɴᴇʟ ɪᴅ (-100xxx)\n/cancel ᴛᴏ ᴀʙᴏʀᴛ." if ch_type == "db" else "ꜱᴇɴᴅ ꜰꜱ ᴄʜᴀɴɴᴇʟ ɪᴅꜱ (ꜱᴘᴀᴄᴇ ꜱᴇᴘᴀʀᴀᴛᴇᴅ)\n/cancel ᴛᴏ ᴀʙᴏʀᴛ."
        
        markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="my_account")]])
        await safe_edit(query.message, f"⚙️ **ꜱᴇᴛᴜᴘ {ch_type.upper()} ᴄʜᴀɴɴᴇʟ**\n\n{prompt}", markup)
        
        try:
            input_msg = await client.listen(chat_id=query.message.chat.id, timeout=60)
        except ListenerTimeout: 
            return await render_dashboard(client, query.message, user_id)
        
        text = input_msg.text or ""
        try: await input_msg.delete()
        except: pass
        
        if text.lower() == "/cancel": 
            return await render_dashboard(client, query.message, user_id)
        
        channels = []
        for item in text.split():
            try: 
                if item.startswith("-100"): channels.append(int(item))
            except: pass
            
        if not channels: 
            await query.message.reply_text("❌ ɪɴᴠᴀʟɪᴅ ɪᴅꜱ ᴘʀᴏᴠɪᴅᴇᴅ. ᴛʀʏ ᴀɢᴀɪɴ.")
            return await render_dashboard(client, query.message, user_id)
            
        if ch_type == "db" and len(channels) > 1: 
            await query.message.reply_text("❌ ᴘʀᴏᴠɪᴅᴇ ᴏɴʟʏ ᴏɴᴇ ᴅᴀᴛᴀʙᴀꜱᴇ ᴄʜᴀɴɴᴇʟ.")
            return await render_dashboard(client, query.message, user_id)
        
        await submit_channel(user_id, ch_type, channels)
        await query.message.reply_text("✅ **ᴄʜᴀɴɴᴇʟ(ꜱ) ꜱᴜʙᴍɪᴛᴛᴇᴅ ꜰᴏʀ ᴀᴅᴍɪɴ ᴀᴘᴘʀᴏᴠᴀʟ!**")
        await render_dashboard(client, query.message, user_id)
        
        # Notify Admins
        admin_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Approve", callback_data=f"aprv_{ch_type}_{user_id}"), InlineKeyboardButton("❌ Reject", callback_data=f"rjct_{ch_type}_{user_id}")]
        ])
        ch_str = ", ".join(map(str, channels))
        await client.send_message(LOG_CHANNEL_ID, f"📝 **Channel Approval Request**\nUser: `{user_id}`\nType: `{ch_type.upper()}`\nChannels: `{ch_str}`", reply_markup=admin_markup)


# --- ADMIN CONTROLS FOR PREMIUM ---
@Client.on_callback_query(filters.regex(r"^(aprv|rjct)_(db|fs)_(\d+)$"))
async def handle_admin_approvals(client, query):
    action = query.matches[0].group(1)
    ch_type = query.matches[0].group(2)
    target_user = int(query.matches[0].group(3))
    
    if action == "aprv":
        await set_channel_status(target_user, ch_type, "approved")
        status_text = f"✅ Approved by {query.from_user.first_name}"
        alert_text = f"Approved {ch_type.upper()} channel!"
        try: await client.send_message(target_user, f"✅ ʏᴏᴜʀ {ch_type.upper()} ᴄʜᴀɴɴᴇʟ ʀᴇQᴜᴇꜱᴛ ᴡᴀꜱ ᴀᴘᴘʀᴏᴠᴇᴅ!")
        except: pass
    else:
        await set_channel_status(target_user, ch_type, "rejected")
        status_text = f"❌ Rejected by {query.from_user.first_name}"
        alert_text = f"Rejected {ch_type.upper()} channel!"
        try: await client.send_message(target_user, f"❌ ʏᴏᴜʀ {ch_type.upper()} ᴄʜᴀɴɴᴇʟ ʀᴇQᴜᴇꜱᴛ ᴡᴀꜱ ʀᴇᴊᴇᴄᴛᴇᴅ.")
        except: pass

    # Extract existing channels to reconstruct the formatted message
    ch_str = "Unknown"
    if query.message.text:
        lines = query.message.text.split('\n')
        for line in lines:
            if line.startswith("Channels:"):
                ch_str = line.replace("Channels:", "").strip()
                break
                
    new_text = (
        f"📝 **Channel Approval Request**\n"
        f"User: `{target_user}`\n"
        f"Type: `{ch_type.upper()}`\n"
        f"Channels: {ch_str}\n\n"
        f"**Status:** {status_text}"
    )

    # Edit the message text, but KEEP the original buttons (reply_markup)
    await query.message.edit_text(new_text, reply_markup=query.message.reply_markup)
    await query.answer(alert_text)


@Client.on_message(filters.command("addpremium") & filters.private)
async def add_prem_cmd(client, message):
    if not await is_admin(message.from_user.id): return
    try:
        user_id = int(message.command[1])
        days = int(message.command[2])
        await set_premium(user_id, days)
        await message.reply_text(f"✅ Premium granted to {user_id} for {days} days.")
        try: await client.send_message(user_id, f"🎉 **Congratulations!** An admin has granted you Premium for {days} days.")
        except: pass
    except Exception:
        await message.reply_text("Usage: /addpremium <user_id> <days>")


@Client.on_message(filters.command("rmpremium") & filters.private)
async def rm_prem_cmd(client, message):
    if not await is_admin(message.from_user.id): return
    try:
        user_id = int(message.command[1])
        await remove_premium(user_id)
        await message.reply_text(f"✅ Premium removed from {user_id}.")
        try: await client.send_message(user_id, "⚠️ Your Premium subscription has been revoked by an admin.")
        except: pass
    except Exception:
        await message.reply_text("Usage: /rmpremium <user_id>")


@Client.on_message(filters.command("revokechannel") & filters.private)
async def revoke_channel_cmd(client, message):
    if not await is_admin(message.from_user.id): return
    try:
        user_id = int(message.command[1])
        ch_type = message.command[2].lower()
        if ch_type not in ["db", "fs"]: raise ValueError
        await set_channel_status(user_id, ch_type, "rejected")
        await message.reply_text(f"✅ Revoked {ch_type.upper()} channel access for {user_id}.")
    except Exception:
        await message.reply_text("Usage: /revokechannel <user_id> <db/fs>")
        
