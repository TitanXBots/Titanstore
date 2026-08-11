import urllib.parse
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from database.database import get_points

# You can change this link to your actual "Refer & Earn" image link
REFER_PIC = "https://envs.sh/WcW.jpg" 

@Client.on_message(filters.command("refer") & filters.private)
async def refer_command(client: Client, message: Message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name or "User"
    
    # Generate link automatically using the bot's actual username
    bot = await client.get_me()
    referral_link = f"https://telegram.dog/{bot.username}?start=ref_{user_id}"
    
    # Get user's current points from the database
    points = await get_points(user_id)
    
    # Cleaned up text without the raw link
    text = (
        f"👋 Hey {first_name}.,\n\n"
        f"Share this link with your friends, Each time they join, you will get 10 referral points and after 100 points you will get 1 month premium subscription."
    )
    
    # Create a pre-filled share message for Telegram
    share_text = f"Hey! Check out this awesome File Store bot. Use my link to start:\n\n{referral_link}"
    share_url = urllib.parse.quote(share_text)
    
    # Buttons stacked in separate rows
    markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("• INVITE LINK ↗️", url=f"https://telegram.me/share/url?url={share_url}")],
        [InlineKeyboardButton(f"⏳ {points} POINTS", callback_data="show_points")],
        [InlineKeyboardButton("• CLOSE •", callback_data="close")]
    ])
    
    await message.reply_photo(photo=REFER_PIC, caption=text, reply_markup=markup)

