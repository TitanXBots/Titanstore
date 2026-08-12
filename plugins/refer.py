from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from database.database import get_points, get_refer_status, get_refer_points

REFER_PIC = "https://envs.sh/WcW.jpg" 

@Client.on_message(filters.command("refer") & filters.private)
async def refer_command(client: Client, message: Message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name or "User"
    
    is_refer_active = await get_refer_status()
    if not is_refer_active:
        return await message.reply_text("⚠️ <b>ɴᴏᴛɪᴄᴇ:</b> The Referral System is currently disabled by the Admin.")
    
    bot = await client.get_me()
    
    # Clean and short t.me referral link
    referral_link = f"https://t.me/{bot.username}?start=ref_{user_id}"
    
    points = await get_points(user_id)
    pts_per_refer = await get_refer_points()
    
    # Clean text without the referral link shown in the caption
    text = (
        f"👋 Hey {first_name}.,\n\n"
        f"Share this link with your friends, Each time they join, you will get {pts_per_refer} referral points and after 100 points you will get 1 month premium subscription."
    )
    
    markup = InlineKeyboardMarkup([
        # Button contains pure clean link, hidden from text
        [InlineKeyboardButton("• INVITE LINK ↗️", url=referral_link)],
        [InlineKeyboardButton(f"⏳ {points} POINTS", callback_data="show_points")],
        [InlineKeyboardButton("• CLOSE •", callback_data="close")]
    ])
    
    await message.reply_photo(photo=REFER_PIC, caption=text, reply_markup=markup)

@Client.on_callback_query(filters.regex("^show_points$"))
async def show_points_cb(client: Client, query: CallbackQuery):
    user_id = query.from_user.id
    
    is_refer_active = await get_refer_status()
    points = await get_points(user_id)
    
    if not is_refer_active:
        await query.answer(
            f"⚠️ The Referral system is currently disabled.\n\n"
            f"📊 Your Points: {points}", 
            show_alert=True
        )
    else:
        await query.answer(
            f"📊 You currently have {points} points!\n\n"
            f"Get 100 points to instantly unlock 1 Month of Premium Access.", 
            show_alert=True
        )
        
