from bot import Bot
from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from config import OWNER_ID, ADMINS


# -------------------------------
# SETTINGS COMMAND
# -------------------------------

@Bot.on_message(filters.command("settings") & filters.private)
async def settings_command(client: Bot, message: Message):

    if not message.from_user:
        return

    user_id = message.from_user.id

    # OWNER + ADMIN CHECK
    if user_id != OWNER_ID and user_id not in ADMINS:
        return await message.reply_text("❌ Only admins can use this.")

    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("🚫 Ban Menu", callback_data="ban_menu")],
            [InlineKeyboardButton("❌ Close", callback_data="close")]
        ]
    )

    await message.reply_text(
        "⚙️ **Bot Settings Panel**",
        reply_markup=keyboard
    )
