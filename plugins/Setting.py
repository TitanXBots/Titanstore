from bot import Bot
from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from config import *
from database.database import is_admin

# -------------------------------
# SETTINGS COMMAND
# -------------------------------
@Bot.on_message(filters.command("settings") & filters.private)
async def settings_command(client: Bot, message: Message):
    user_id = message.from_user.id

    # Check if owner or admin
    is_admin_user = user_id == OWNER_ID or user_id in ADMINS or await is_admin(user_id)

    # Only admins/owner can access settings
    if not is_admin_user:
        # Optional: you can send a small notice or just ignore
        return await message.reply_text(
            "❌ You do not have permission to access the Settings panel."
        )

    # -------------------------------
    # ADMIN SETTINGS PANEL
    # -------------------------------
    buttons = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("🚫 Ban Menu", callback_data="ban_menu")],
            [InlineKeyboardButton("⚓ Home", callback_data="start")],
            [InlineKeyboardButton("❌ Close", callback_data="close")]
        ]
    )
    await message.reply_text(
        text="⚙️ **Bot Settings Panel**",
        reply_markup=buttons
    )
