from bot import Bot
from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from config import *

# -------------------------------
# SETTINGS COMMAND
# -------------------------------

@Bot.on_message(filters.command("settings") & filters.private)
async def settings_command(client: Bot, message: Message):
    user_id = message.from_user.id
    is_admin_user = user_id == OWNER_ID or user_id in ADMINS

    if not is_admin_user:
        # View-only panel for non-admins
        await client.send_message(
            chat_id=user_id,
            text=(
                "⚙️ **Settings Panel (View Only)**\n\n"
                "❌ You do not have admin rights to modify settings.\n"
                f"- Owner: [{OWNER_ID}](tg://user?id={OWNER_ID})\n"
                "- Only admins can access Ban Controls.\n"
            ),
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("⚓ Home", callback_data="start")]]
            ),
            disable_web_page_preview=True
        )
        return

    # Admin panel
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
