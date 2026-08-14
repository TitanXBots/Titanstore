from datetime import datetime, timezone
from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from config import START_PIC, OWNER_ID
from database.database import is_premium, premium_collection, get_refer_status

PLAN_PIC = "https://envs.sh/WeX.jpg" 
QR_PIC = "https://envs.sh/TPh.jpg" 

@Client.on_message(filters.command("plan") & filters.private)
async def plan_command(client: Client, message: Message):
    first_name = message.from_user.first_name or "User"
    caption = (
        f"👋 ʜᴇʏ <b>{first_name}</b>,\n\n"
        f"🎁 <b>ᴘʀᴇᴍɪᴜᴍ ꜰᴇᴀᴛᴜʀᴇ ʙᴇɴᴇꜰɪᴛꜱ:</b>\n\n"
        f"☑️ ɴᴏ ɴᴇᴇᴅ ᴛᴏ ᴏᴘᴇɴ ʟɪɴᴋꜱ\n"
        f"☑️ ɢᴇᴛ ᴅɪʀᴇᴄᴛ ꜰɪʟᴇꜱ\n"
        f"☑️ ᴀᴅ-ꜰʀᴇᴇ ᴇxᴘᴇʀɪᴇɴᴄᴇ\n"
        f"☑️ ʜɪɢʜ-ꜱᴘᴇᴇᴅ ᴅᴏᴡɴʟᴏᴀᴅ ʟɪɴᴋ\n"
        f"☑️ ᴍᴜʟᴛɪ-ᴘʟᴀʏᴇʀ ꜱᴛʀᴇᴀᴍɪɴɢ ʟɪɴᴋꜱ\n"
        f"☑️ ᴜɴʟɪᴍɪᴛᴇᴅ ᴍᴏᴠɪᴇꜱ ᴀɴᴅ ꜱᴇʀɪᴇꜱ\n"
        f"☑️ ꜰᴜʟʟ ᴀᴅᴍɪɴ ꜱᴜᴘᴘᴏʀᴛ\n"
        f"☑️ ʀᴇǫᴜᴇꜱᴛ ᴡɪʟʟ ʙᴇ ᴄᴏᴍᴘʟᴇᴛᴇᴅ ɪɴ 1ʜ [ ɪꜰ ᴀᴠᴀɪʟᴀʙʟᴇ ]"
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🍁 ᴄʜᴇᴄᴋ ᴀʟʟ ᴘʟᴀɴꜱ & ᴘʀɪᴄᴇꜱ 🍁", callback_data="view_prices")],
        [InlineKeyboardButton("💎 CUSTOM PLAN 💎", callback_data="custom_plan")],
        [InlineKeyboardButton("🥤 ᴄʜᴇᴄᴋ ᴍʏ ᴘʟᴀɴ 🥤", callback_data="myplan")],
        [InlineKeyboardButton("« ʙᴀᴄᴋ ᴛᴏ ʜᴏᴍᴇ", callback_data="start")]
    ])
    await message.reply_photo(photo=PLAN_PIC, caption=caption, reply_markup=keyboard)

@Client.on_message(filters.command("myplan") & filters.private)
async def myplan_command(client: Client, message: Message):
    user_id = message.from_user.id
    is_prem = await is_premium(user_id)
    
    if is_prem:
        user_data = await premium_collection.find_one({"_id": user_id})
        if user_data and user_data.get("expires_at"):
            expires_at = user_data["expires_at"].replace(tzinfo=timezone.utc)
            now = datetime.now(timezone.utc)
            time_left = expires_at - now
            
            days = time_left.days
            hours, remainder = divmod(time_left.seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            
            expiry_str = expires_at.strftime("%Y-%m-%d %H:%M:%S UTC")
            time_left_str = f"{days} Days, {hours} Hours, {minutes} Minutes"
            
            text = (
                f"💎 <b>ʏᴏᴜ ᴀʀᴇ ᴀ ᴘʀᴇᴍɪᴜᴍ ᴍᴇᴍʙᴇʀ!</b>\n\n"
                f"📅 <b>ᴇxᴘɪʀʏ ᴅᴀᴛᴇ:</b> <code>{expiry_str}</code>\n"
                f"⏳ <b>ᴛɪᴍᴇ ʟᴇꜰᴛ:</b> <code>{time_left_str}</code>\n\n"
                f"<i>ʏᴏᴜ ʜᴀᴠᴇ ᴜɴʟɪᴍɪᴛᴇᴅ ᴀᴄᴄᴇꜱꜱ ᴛᴏ ᴀʟʟ ᴘʀᴇᴍɪᴜᴍ ꜰᴇᴀᴛᴜʀᴇꜱ!</i>"
            )
        else:
            text = (
                f"👑 <b>ʏᴏᴜ ᴀʀᴇ ᴀɴ ᴀᴅᴍɪɴ!</b>\n\n"
                f"📅 <b>ᴇxᴘɪʀʏ ᴅᴀᴛᴇ:</b> <code>Lifetime</code>\n"
                f"⏳ <b>ᴛɪᴍᴇ ʟᴇꜰᴛ:</b> <code>Unlimited</code>\n\n"
                f"<i>ʏᴏᴜ ʜᴀᴠᴇ ᴜɴʟɪᴍɪᴛᴇᴅ ᴀᴄᴄᴇꜱꜱ ᴛᴏ ᴀʟʟ ᴘʀᴇᴍɪᴜᴍ ꜰᴇᴀᴛᴜʀᴇꜱ.</i>"
            )
    else:
        is_refer_active = await get_refer_status()
        refer_promo = f"\n🎁 <i>ʏᴏᴜ ᴄᴀɴ ᴀʟꜱᴏ ᴜꜱᴇ /refer ᴛᴏ ᴇᴀʀɴ ꜰʀᴇᴇ ᴘʀᴇᴍɪᴜᴍ ᴀᴄᴄᴇꜱꜱ.</i>" if is_refer_active else ""
        
        text = (
            f"🆓 <b>ʏᴏᴜ ᴀʀᴇ ᴏɴ ᴛʜᴇ ꜰʀᴇᴇ ᴘʟᴀɴ.</b>\n\n"
            f"ᴜꜱᴇ /plan ᴛᴏ ᴠɪᴇᴡ ᴘʀᴇᴍɪᴜᴍ ʙᴇɴᴇꜰɪᴛꜱ ᴀɴᴅ ᴜᴘɢʀᴀᴅᴇ!\n"
            f"{refer_promo}"
        )
        
    await message.reply_text(text)

@Client.on_callback_query(filters.regex("^(buy_plans|view_prices|custom_plan|close_menu|plan_home|myplan)$"))
async def plans_cb(client: Client, query: CallbackQuery):
    try: await query.answer()
    except: pass
    user_id = query.from_user.id
    first_name = query.from_user.first_name or "User"
    data = query.data

    if data in ["buy_plans", "plan_home", "close_menu"]:
        if data == "close_menu":
            try:
                return await query.message.delete()
            except Exception:
                return
        caption = (
            f"👋 ʜᴇʏ <b>{first_name}</b>,\n\n"
            f"🎁 <b>ᴘʀᴇᴍɪᴜᴍ ꜰᴇᴀᴛᴜʀᴇ ʙᴇɴᴇꜰɪᴛꜱ:</b>\n\n"
            f"☑️ ɴᴏ ɴᴇᴇᴅ ᴛᴏ ᴏᴘᴇɴ ʟɪɴᴋꜱ\n"
            f"☑️ ɢᴇᴛ ᴅɪʀᴇᴄᴛ ꜰɪʟᴇꜱ\n"
            f"☑️ ᴀᴅ-ꜰʀᴇᴇ ᴇxᴘᴇʀɪᴇɴᴄᴇ\n"
            f"☑️ ʜɪɢʜ-ꜱᴘᴇᴇᴅ ᴅᴏᴡɴʟᴏᴀᴅ ʟɪɴᴋ\n"
            f"☑️ ᴍᴜʟᴛɪ-ᴘʟᴀʏᴇʀ ꜱᴛʀᴇᴀᴍɪɴɢ ʟɪɴᴋꜱ\n"
            f"☑️ ᴜɴʟɪᴍɪᴛᴇᴅ ᴍᴏᴠɪᴇꜱ ᴀɴᴅ ꜱᴇʀɪᴇꜱ\n"
            f"☑️ ꜰᴜʟʟ ᴀᴅᴍɪɴ ꜱᴜᴘᴘᴏʀᴛ\n"
            f"☑️ ʀᴇǫᴜᴇꜱᴛ ᴡɪʟʟ ʙᴇ ᴄᴏᴍᴘʟᴇᴛᴇᴅ ɪɴ 1ʜ [ ɪꜰ ᴀᴠᴀɪʟᴀʙʟᴇ ]"
        )
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🍁 ᴄʜᴇᴄᴋ ᴀʟʟ ᴘʟᴀɴꜱ & ᴘʀɪᴄᴇꜱ 🍁", callback_data="view_prices")],
            [InlineKeyboardButton("💎 CUSTOM PLAN 💎", callback_data="custom_plan")],
            [InlineKeyboardButton("🥤 ᴄʜᴇᴄᴋ ᴍʏ ᴘʟᴀɴ 🥤", callback_data="myplan")],
            [InlineKeyboardButton("« ʙᴀᴄᴋ ᴛᴏ ʜᴏᴍᴇ", callback_data="start")]
        ])
        try:
            if query.message.photo:
                await query.message.edit_caption(caption=caption, reply_markup=keyboard)
            else:
                await query.message.delete()
                await client.send_photo(chat_id=user_id, photo=PLAN_PIC, caption=caption, reply_markup=keyboard)
        except Exception:
            await client.send_photo(chat_id=user_id, photo=PLAN_PIC, caption=caption, reply_markup=keyboard)

    elif data == "view_prices":
        caption = (
            f"👋 ʜᴇʏ <b>{first_name}</b>,\n\n"
            f"🎖 <b>ᴀᴠᴀɪʟᴀʙʟᴇ ᴘʀᴇᴍɪᴜᴍ ᴘʟᴀɴꜱ :</b>\n\n"
            f"❏ 015₹ ➡️ 01 WEEKS\n"
            f"❏ 039₹ ➡️ 01 MONTH\n"
            f"❏ 075₹ ➡️ 02 MONTH\n"
            f"❏ 110₹ ➡️ 03 MONTH\n"
            f"❏ 199₹ ➡️ 06 MONTH\n"
            f"❏ 360₹ ➡️ 12 MONTH\n\n"
            f"🆔 UPI ID ➡️ <code>kushalhari@slc</code> [TAP TO COPY]\n\n"
            f"‼️ <b>MUST SEND SCREENSHOT AFTER PAYMENT.</b>\n"
            f"‼️ <b>GIVE US SOMETIME TO ADD YOU IN PREMIUM LIST.</b>"
        )
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("⭐📸 1. SEND SCREENSHOT 📸⭐", url=f"tg://user?id={OWNER_ID}")],
            [InlineKeyboardButton("📱 2. CONTACT OWNER", url=f"tg://user?id={OWNER_ID}")],
            [InlineKeyboardButton("🥤 3. CHECK MY PLAN 🥤", callback_data="myplan")],
            [InlineKeyboardButton("💎 CUSTOM PLAN 💎", callback_data="custom_plan")],
            [
                InlineKeyboardButton("• BACK •", callback_data="buy_plans"),
                InlineKeyboardButton("• CLOSE •", callback_data="close_menu")
            ]
        ])
        try:
            if query.message.photo:
                await query.message.edit_caption(caption=caption, reply_markup=keyboard)
            else:
                await query.message.delete()
                await client.send_photo(chat_id=user_id, photo=PLAN_PIC, caption=caption, reply_markup=keyboard)
        except Exception:
            await client.send_photo(chat_id=user_id, photo=PLAN_PIC, caption=caption, reply_markup=keyboard)

    elif data == "custom_plan":
        caption = (
            f"👋 ʜᴇʏ <b>{first_name}</b>,\n\n"
            f"🎁 <b>ᴏᴛʜᴇʀ ᴘʟᴀɴ</b>\n"
            f"⏰ <b>ᴄᴜꜱᴛᴏᴍɪꜱᴇᴅ ᴅᴀʏꜱ</b>\n"
            f"🪩 <b>ᴀᴄᴄᴏʀᴅɪɴɢ ᴛᴏ ᴅᴀʏꜱ ʏᴏᴜ ᴄʜᴏᴏꜱᴇ</b>\n\n"
            f"🏆 <b>ɪꜰ ʏᴏᴜ ᴡᴀɴᴛ ᴀ ɴᴇᴡ ᴘʟᴀɴ ᴀᴘᴀʀᴛ ꜰʀᴏᴍ ᴛʜᴇ ɢɪᴠᴇɴ ᴘʟᴀɴ, ᴛʜᴇɴ ʏᴏᴜ ᴄᴀɴ ᴛᴀʟᴋ ᴛᴏ ᴏᴜʀ ᴏᴡɴᴇʀ ᴅɪʀᴇᴄᴛʟʏ ʙʏ ᴄʟɪᴄᴋɪɴɢ ᴏɴ ᴛʜᴇ ᴄᴏɴᴛᴀᴄᴛ ʙᴜᴛᴛᴏɴ ɢɪᴠᴇɴ ʙᴇʟᴏᴡ.</b>\n\n"
            f"👩‍💻 <b>ᴄᴏɴᴛᴀᴄᴛ ᴛʜᴇ ᴏᴡɴᴇʀ ᴛᴏ ɢᴇᴛ ʏᴏᴜʀ ᴏᴛʜᴇʀ ᴘʟᴀɴ.</b>\n"
        )
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📱 ᴄᴏɴᴛᴀᴄᴛ ᴛᴏ ᴏᴡɴᴇʀ", url=f"tg://user?id={OWNER_ID}")],
            [InlineKeyboardButton("🥤 ᴄʜᴇᴄᴋ ᴍʏ ᴘʟᴀɴ 🥤", callback_data="myplan")],
            [InlineKeyboardButton("• BACK •", callback_data="view_prices")]
        ])
        try:
            if query.message.photo:
                await query.message.edit_caption(caption=caption, reply_markup=keyboard)
            else:
                await query.message.delete()
                await client.send_photo(chat_id=user_id, photo=QR_PIC, caption=caption, reply_markup=keyboard)
        except Exception:
            await client.send_photo(chat_id=user_id, photo=QR_PIC, caption=caption, reply_markup=keyboard)

    elif data == "myplan":
        is_prem = await is_premium(user_id)
        if is_prem:
            user_data = await premium_collection.find_one({"_id": user_id})
            if user_data and user_data.get("expires_at"):
                expires_at = user_data["expires_at"].replace(tzinfo=timezone.utc)
                now = datetime.now(timezone.utc)
                time_left = expires_at - now
                
                days = time_left.days
                hours, remainder = divmod(time_left.seconds, 3600)
                minutes, _ = divmod(remainder, 60)
                
                expiry_str = expires_at.strftime("%Y-%m-%d %H:%M:%S UTC")
                time_left_str = f"{days} Days, {hours} Hours, {minutes} Minutes"
                
                caption = (
                    f"💎 <b>ʏᴏᴜ ᴀʀᴇ ᴀ ᴘʀᴇᴍɪᴜᴍ ᴍᴇᴍʙᴇʀ!</b>\n\n"
                    f"📅 <b>ᴇxᴘɪʀʏ ᴅᴀᴛᴇ:</b> <code>{expiry_str}</code>\n"
                    f"⏳ <b>ᴛɪᴍᴇ ʟᴇꜰᴛ:</b> <code>{time_left_str}</code>\n\n"
                    f"<i>ʏᴏᴜ ʜᴀᴠᴇ ᴜɴʟɪᴍɪᴛᴇᴅ ᴀᴄᴄᴇꜱꜱ ᴛᴏ ᴀʟʟ ᴘʀᴇᴍɪᴜᴍ ꜰᴇᴀᴛᴜʀᴇꜱ!</i>"
                )
            else:
                caption = (
                    f"👑 <b>ʏᴏᴜ ᴀʀᴇ ᴀɴ ᴀᴅᴍɪɴ!</b>\n\n"
                    f"📅 <b>ᴇxᴘɪʀʏ ᴅᴀᴛᴇ:</b> <code>Lifetime</code>\n"
                    f"⏳ <b>ᴛɪᴍᴇ ʟᴇꜰᴛ:</b> <code>Unlimited</code>\n\n"
                    f"<i>ʏᴏᴜ ʜᴀᴠᴇ ᴜɴʟɪᴍɪᴛᴇᴅ ᴀᴄᴄᴇꜱꜱ ᴛᴏ ᴀʟʟ ᴘʀᴇᴍɪᴜᴍ ꜰᴇᴀᴛᴜʀᴇꜱ.</i>"
                )
        else:
            is_refer_active = await get_refer_status()
            refer_promo = f"\n🎁 <i>ʏᴏᴜ ᴄᴀɴ ᴀʟꜱᴏ ᴜꜱᴇ ᴛʜᴇ <b>/refer</b> ᴄᴏᴍᴍᴀɴᴅ ᴛᴏ ᴇᴀʀɴ ꜰʀᴇᴇ ᴘʀᴇᴍɪᴜᴍ ᴀᴄᴄᴇꜱꜱ.</i>" if is_refer_active else ""
            
            caption = (
                f"🆓 <b>ʏᴏᴜ ᴀʀᴇ ᴏɴ ᴛʜᴇ ꜰʀᴇᴇ ᴘʟᴀɴ.</b>\n\n"
                f"ᴜᴘɢʀᴀᴅᴇ ᴛᴏ ᴘʀᴇᴍɪᴜᴍ ᴛᴏ ᴇɴᴊᴏʏ ᴇxᴄʟᴜꜱɪᴠᴇ ʙᴇɴᴇꜰɪᴛꜱ!\n"
                f"{refer_promo}"
            )
            
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("• BACK •", callback_data="buy_plans")]
        ])
        
        try:
            if query.message.photo:
                await query.message.edit_caption(caption=caption, reply_markup=keyboard)
            else:
                await query.message.delete()
                await client.send_photo(chat_id=user_id, photo=PLAN_PIC, caption=caption, reply_markup=keyboard)
        except Exception:
            pass
            
