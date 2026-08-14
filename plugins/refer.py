from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from database.database import get_points, get_refer_status, get_refer_points, add_premium, deduct_points

REFER_PIC = "https://envs.sh/WcW.jpg" 

@Client.on_message(filters.command("refer") & filters.private)
async def refer_command(client: Client, message: Message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name or "User"
    
    is_refer_active = await get_refer_status()
    if not is_refer_active:
        return await message.reply_text("⚠️ <b>ɴᴏᴛɪᴄᴇ:</b> The Referral System is currently disabled by the Admin.")
    
    bot = await client.get_me()
    referral_link = f"https://t.me/{bot.username}?start=ref_{user_id}"
    
    points = await get_points(user_id)
    pts_per_refer = await get_refer_points()
    
    text = (
        f"👋 ʜᴇʏ <b>{first_name}</b>,\n\n"
        f"🔗 Share your link with friends! Each join gives you <b>{pts_per_refer} points</b>.\n"
        f"💎 Reach <b>100 points</b> to redeem 1 Month of Premium Access!"
    )
    
    markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("• ɪɴᴠɪᴛᴇ ʟɪɴᴋ ↗️", url=referral_link)],
        [InlineKeyboardButton(f"⏳ {points} ᴘᴏɪɴᴛꜱ", callback_data="show_points")],
        [InlineKeyboardButton("🎁 ʀᴇᴅᴇᴇᴍ ᴘᴏɪɴᴛꜱ", callback_data="redeem_points")],
        [InlineKeyboardButton("• ᴄʟᴏꜱᴇ •", callback_data="close")]
    ])
    
    await message.reply_photo(photo=REFER_PIC, caption=text, reply_markup=markup)

@Client.on_callback_query(filters.regex("^show_points$"))
async def show_points_cb(client: Client, query: CallbackQuery):
    await query.answer()
    user_id = query.from_user.id
    is_refer_active = await get_refer_status()
    points = await get_points(user_id)
    
    if not is_refer_active:
        await query.answer(f"⚠️ Referral system is disabled.\n\n📊 Your Points: {points}", show_alert=True)
    else:
        await query.answer(f"📊 You currently have {points} points!\n\nReach 100 points to redeem 1 Month of Premium Access.", show_alert=True)

@Client.on_callback_query(filters.regex("^redeem_points$"))
async def redeem_points_cb(client: Client, query: CallbackQuery):
    await query.answer()
    user_id = query.from_user.id
    points = await get_points(user_id)
    
    if points < 100:
        return await query.answer(f"❌ You need at least 100 points to redeem premium!\nYou currently have {points} points.", show_alert=True)
    
    from database.database import user_data
    await user_data.update_one({"_id": user_id}, {"$inc": {"points": -100}})
    await add_premium(user_id, 30)
    
    await query.answer("🎉 Success! 100 points deducted and 1 Month Premium Access activated!", show_alert=True)
    try:
        await query.message.edit_caption(
            caption="🎉 <b>ᴄᴏɴɢʀᴀᴛᴜʟᴀᴛɪᴏɴꜱ!</b> You successfully redeemed your points for 1 Month of Premium Access!",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("« ʙᴀᴄᴋ ᴛᴏ ʜᴏᴍᴇ", callback_data="start")]])
        )
    except Exception:
        pass
        
