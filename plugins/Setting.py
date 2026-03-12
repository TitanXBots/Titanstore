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

    # check owner or admin
    is_admin_user = user_id == OWNER_ID or user_id in ADMINS or await is_admin(user_id)


# -------------------------------
# NON ADMIN PANEL
# -------------------------------

    if not is_admin_user:

        buttons = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("⚓ Home", callback_data="start")],
                [InlineKeyboardButton("❌ Close", callback_data="close")]
            ]
        )

        await message.reply_text(
            text=(
                "⚙️ **Settings Panel (View Only)**\n\n"
                "❌ You do not have permission to modify bot settings.\n\n"
                f"👑 **Owner:** [Click Here](tg://user?id={OWNER_ID})"
            ),
            reply_markup=buttons,
            disable_web_page_preview=True
        )
        return


# -------------------------------
# ADMIN PANEL
# -------------------------------

    buttons = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("👑 Admin Menu", callback_data="admin_menu")],
            [InlineKeyboardButton("🚫 Ban Menu", callback_data="ban_menu")],
            [InlineKeyboardButton("⚓ Home", callback_data="start")],
            [InlineKeyboardButton("❌ Close", callback_data="close")]
        ]
    )

    await message.reply_text(
        "⚙️ **Bot Settings Panel**",
        reply_markup=buttons
    )
