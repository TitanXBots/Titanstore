from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import MessageNotModified
from pyromod.exceptions import ListenerTimeout
from helper_func import safe_edit
from database.database import (
    get_premium_status, get_user, add_referral_points, set_premium, 
    remove_premium, is_admin, submit_channel, get_user_approved_channels, set_channel_status,
    has_claimed_trial, grant_free_trial
)
from config import OWNER_USERNAME, POINTS_TO_PREMIUM, PREMIUM_DAYS, LOG_CHANNEL_ID

# --- 1. COMMAND TO OPEN MENU ---
@Client.on_message(filters.command(["plan", "myplan", "mychannels"]) & filters.private)
async def plan_cmd(client, message):
    await render_dashboard(client, message, message.from_user.id)

# --- 2. THE UI RENDERER (Refer & Earn + Persistent Trial Button) ---
async def render_dashboard(client, message, user_id):
    is_prem = await get_premium_status(user_id)
    user = await get_user(user_id)
    points = user.get("points", 0) if user else 0
    first_name = user.get("first_name", "User") if user else "User"
    
    # 🌟 REFER & EARN TEXT FOR EVERYONE
    ref_text = (
        f"👋 ʜᴀʏ {first_name},\n\n"
        f"**HERE IS YOUR REFFERAL LINK:**\n"
        f"🔗 <code>https://t.me/{client.me.username}?start=ref_{user_id}</code>\n\n"
        f"Share this link with your friends, Each time they join, you will get 10 refferal points "
        f"and after {POINTS_TO_PREMIUM} points you will get {PREMIUM_DAYS} days premium subscription.\n"
        f"⏳ **Your Points:** `{points} / {POINTS_TO_PREMIUM}`\n"
        f"━━━━━━━━━━━━━━━━━\n\n"
    )
    
    if is_prem or await is_admin(user_id):
        status = "👑 ᴘʀᴇᴍɪᴜᴍ" if is_prem else "👨‍💻 ᴀᴅᴍɪɴ"
        text = ref_text + (
            f"👤 **ʏᴏᴜʀ ᴀᴄᴄᴏᴜɴᴛ ᴅᴀꜱʜʙᴏᴀʀᴅ**\n"
            f"🆔 **ᴜꜱᴇʀ ɪᴅ:** <code>{user_id}</code>\n"
            f"📊 **ꜱᴛᴀᴛᴜꜱ:** {status}"
        )
        buttons = [
            [InlineKeyboardButton("💳 ʀᴇᴅᴇᴇᴍ ᴘᴏɪɴᴛꜱ", callback_data="redeem_points"), InlineKeyboardButton("📜 ᴠɪᴇᴡ ᴘʟᴀɴꜱ", callback_data="show_plans")],
            [InlineKeyboardButton("✏️ ꜱᴇᴛ ᴅʙ ᴄʜᴀɴɴᴇʟ", callback_data="set_user_db"), InlineKeyboardButton("📢 ꜱᴇᴛ ꜰꜱ ᴄʜᴀɴɴᴇʟꜱ", callback_data="set_user_fs")],
            [InlineKeyboardButton("📊 ᴠɪᴇᴡ ᴍʏ ᴄʜᴀɴɴᴇʟꜱ", callback_data="view_user_channels")],
            [InlineKeyboardButton("🔙 ʙᴀᴄᴋ ᴛᴏ ʜᴏᴍᴇ", callback_data="start")]
        ]
        
    else:
        trial_claimed = await has_claimed_trial(user_id)
        
        # Text changes based on whether they claimed it, but buttons stay the same!
        if not trial_claimed:
            text = ref_text + (
                "😔 **YOU DON'T HAVE ANY PREMIUM SUBSCRIPTION. IF YOU WANT TO BUY PREMIUM CLICK ON BELOW BUTTON.**\n\n"
                "**TO USE OUR PREMIUM FEATURES FOR 10 MINUTES CLICK ON FREE TRAIL BUTTON.**"
            )
        else:
            text = ref_text + (
                "😔 **YOU DON'T HAVE ANY PREMIUM SUBSCRIPTION.**\n\n"
                "*(You have already used your 10-minute free trial)*\n\n"
                "**CLICK BELOW TO BUY PREMIUM AND REMOVE ADS.**"
            )
            
        buttons = [
            [InlineKeyboardButton("🎁 GET FREE TRAIL FOR 10 MINUTES ☺️", callback_data="claim_trial")],
            [InlineKeyboardButton("💳 BUY SUBSCRIPTION : REMOVE ADS", callback_data="show_plans")],
            [InlineKeyboardButton("🔙 ʙᴀᴄᴋ ᴛᴏ ʜᴏᴍᴇ", callback_data="start")]
        ]

    await safe_edit(message, text, InlineKeyboardMarkup(buttons))

# --- 3. THE BUTTON CLICKS (10-Min Trial Engine & Auto-Approve) ---
@Client.on_callback_query(filters.regex("^(my_account|redeem_points|set_user_db|set_user_fs|view_user_channels|claim_trial|show_plans)$"))
async def premium_ui_callbacks(client, query):
    try: await query.answer()
    except: pass
    user_id = query.from_user.id
    data = query.data

    if data == "my_account": return await render_dashboard(client, query.message, user_id)
    
    elif data == "claim_trial":
        if await has_claimed_trial(user_id): 
            # Persistent pop-up alert if they try to click it again
            return await query.answer("❌ You have already used your 10-minute free trial!", show_alert=True)
            
        # Grant 10 minutes!
        await grant_free_trial(user_id)
        await query.answer("🎉 ꜱᴜᴄᴄᴇꜱꜱ! ʏᴏᴜ ɴᴏᴡ ʜᴀᴠᴇ 10 ᴍɪɴᴜᴛᴇꜱ ᴏꜰ ᴘʀᴇᴍɪᴜᴍ ᴀᴄᴄᴇꜱꜱ.", show_alert=True)
        await render_dashboard(client, query.message, user_id)
        
    elif data == "show_plans":
        text = f"🎖️ **ᴀᴠᴀɪʟᴀʙʟᴇ ᴘʟᴀɴꜱ :**\n\n ❏ 𝟶𝟷𝟻₹ ➠ 𝟶𝟷 ᴡᴇᴇᴋ\n ❏ 𝟶𝟹𝟿₹ ➠ 𝟶𝟷 ᴍᴏɴᴛʜ\n\n🆔 ᴜᴘɪ ɪᴅ ➩ <code>kushalhari@slc</code>\n\n‼️ ꜱᴇɴᴅ ꜱᴄʀᴇᴇɴꜱʜᴏᴛ ᴀꜰᴛᴇʀ ᴘᴀʏᴍᴇɴᴛ."
        await safe_edit(query.message, text, InlineKeyboardMarkup([[InlineKeyboardButton("📸 ꜱᴇɴᴅ ꜱᴄʀᴇᴇɴꜱʜᴏᴛ", url=f"https://t.me/{OWNER_USERNAME}")], [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="my_account")]]))
        
    elif data == "redeem_points":
        user = await get_user(user_id)
        points = user.get("points", 0) if user else 0
        if points >= POINTS_TO_PREMIUM:
            await add_referral_points(user_id, -POINTS_TO_PREMIUM)
            await set_premium(user_id, PREMIUM_DAYS)
            await query.answer(f"🎉 ꜱᴜᴄᴄᴇꜱꜱ!", show_alert=True)
            await render_dashboard(client, query.message, user_id)
        else: await query.answer(f"❌ ɴᴏᴛ ᴇɴᴏᴜɢʜ ᴘᴏɪɴᴛꜱ! ({points}/{POINTS_TO_PREMIUM})", show_alert=True)
        
    elif data == "view_user_channels":
        u_db, u_fs = await get_user_approved_channels(user_id, "db"), await get_user_approved_channels(user_id, "fs")
        db_txt = f"<code>{u_db[0]}</code>" if u_db else "None"
        fs_txt = ", ".join([f"<code>{ch}</code>" for ch in u_fs]) if u_fs else "None"
        await safe_edit(query.message, f"📊 **ʏᴏᴜʀ ᴄʜᴀɴɴᴇʟꜱ:**\n\n📁 **ᴅʙ:** {db_txt}\n📢 **ꜰꜱ:** {fs_txt}", InlineKeyboardMarkup([[InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="my_account")]]))
        
    elif data in ["set_user_db", "set_user_fs"]:
        if not await get_premium_status(user_id) and not await is_admin(user_id): return await query.answer("👑 ᴘʀᴇᴍɪᴜᴍ ʀᴇQᴜɪʀᴇᴅ!", show_alert=True)
        ch_type = "db" if data == "set_user_db" else "fs"
        prompt = "ꜱᴇɴᴅ ᴅʙ ᴄʜᴀɴɴᴇʟ ɪᴅ (-100xxx)\n/cancel ᴛᴏ ᴀʙᴏʀᴛ." if ch_type == "db" else "ꜱᴇɴᴅ ꜰꜱ ᴄʜᴀɴɴᴇʟ ɪᴅꜱ (ꜱᴘᴀᴄᴇ ꜱᴇᴘᴀʀᴀᴛᴇᴅ)\n/cancel ᴛᴏ ᴀʙᴏʀᴛ."
        await safe_edit(query.message, f"⚙️ **ꜱᴇᴛᴜᴘ {ch_type.upper()}**\n\n{prompt}", InlineKeyboardMarkup([[InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="my_account")]]))
        
        try: input_msg = await client.listen(chat_id=query.message.chat.id, timeout=60)
        except ListenerTimeout: return await render_dashboard(client, query.message, user_id)
        text = input_msg.text or ""
        try: await input_msg.delete()
        except: pass
        if text.lower() == "/cancel": return await render_dashboard(client, query.message, user_id)
        
        channels = []
        for item in text.split():
            try:
                if item.startswith("-100"):
                    ch_id = int(item)
                    if ch_id not in channels: channels.append(ch_id)
            except: pass
            
        if not channels: return await render_dashboard(client, query.message, user_id)
        if ch_type == "db" and len(channels) > 1:
            await query.message.reply_text("❌ ᴘʀᴏᴠɪᴅᴇ ᴏɴʟʏ ᴏɴᴇ ᴅᴀᴛᴀʙᴀꜱᴇ ᴄʜᴀɴɴᴇʟ.")
            return await render_dashboard(client, query.message, user_id)
            
        # 🚀 AUTO-APPROVE LOGIC (Works for Trial Users instantly!)
        await submit_channel(user_id, ch_type, channels, status="approved")
        await query.message.reply_text("✅ **ᴄʜᴀɴɴᴇʟ(ꜱ) ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ᴀᴜᴛᴏ-ᴀᴘᴘʀᴏᴠᴇᴅ!**")
        await render_dashboard(client, query.message, user_id)
        
        ch_str = " ".join(map(str, channels))
        await client.send_message(LOG_CHANNEL_ID, f"📝 **Channel Auto-Approved**\nUser: `{user_id}`\nType: `{ch_type.upper()}`\nChannels: `{ch_str}`\n\nStatus: ✅ Auto-Approved")

# --- 4. MANUAL ADMIN COMMANDS ---
@Client.on_message(filters.command("addpremium") & filters.private)
async def add_prem_cmd(client, message):
    if not await is_admin(message.from_user.id): return
    try:
        user_id, days = int(message.command[1]), int(message.command[2])
        await set_premium(user_id, days)
        await message.reply_text(f"✅ Premium granted to {user_id} for {days} days.")
    except: await message.reply_text("Usage: /addpremium <user_id> <days>")

@Client.on_message(filters.command("rmpremium") & filters.private)
async def rm_prem_cmd(client, message):
    if not await is_admin(message.from_user.id): return
    try:
        user_id = int(message.command[1])
        await remove_premium(user_id)
        await message.reply_text(f"✅ Premium removed from {user_id}.")
    except: await message.reply_text("Usage: /rmpremium <user_id>")
        
