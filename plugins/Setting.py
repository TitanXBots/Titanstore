from bot import Bot
from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from config import OWNER_ID
from database.database import is_admin


# -------------------------------
# SETTINGS COMMAND
# -------------------------------

@Bot.on_message(filters.command("settings") & filters.private)
async def settings_command(client: Bot, message: Message):

    user_id = message.from_user.id

    if not (user_id == OWNER_ID
        return await message.reply("❌ Only admins can use this.")

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🚫 Ban Menu", callback_data="ban_menu")],
        [InlineKeyboardButton("❌ Close", callback_data="close")]
    ])

    await message.reply(
        "⚙️ **Bot Settings Panel**",
        reply_markup=keyboard
    )
