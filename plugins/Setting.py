from bot import Bot
from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from config import OWNER_ID, ADMINS
from database.database import is_admin

@Bot.on_message(filters.command("settings") & filters.private)
async def settings_command(client: Bot, message: Message):
    user_id = message.from_user.id
    is_admin_user = user_id == OWNER_ID or user_id in ADMINS or await is_admin(user_id)
    if not is_admin_user:
        return await message.reply_text("❌ You do not have permission to access bot settings.")

    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("🚫 Ban Menu", callback_data="ban_menu")],
        [InlineKeyboardButton("⬅ Back", callback_data="start"),
         InlineKeyboardButton("⚡ Close", callback_data="close")]
    ])
    await message.reply_text("⚙️ Bot Settings Panel", reply_markup=buttons)
