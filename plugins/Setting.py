import asyncio
from bot import Bot
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
from config import *
from database.database import ban_user, unban_user, is_banned, get_ban_reason, banned_users
from database.database import is_admin
from pyrogram.errors import PeerIdInvalid


# -------------------------------
# SETTINGS COMMAND
# -------------------------------

@Bot.on_message(filters.command("settings") & filters.private)
async def settings_command(client: Bot, message: Message):

    user_id = message.from_user.id

    if not (user_id == OWNER_ID or await is_admin(user_id)):
        return await message.reply("❌ You are not allowed to use this.")

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🚫 Ban Menu", callback_data="ban_menu")],
        [InlineKeyboardButton("❌ Close", callback_data="close")]
    ])

    await message.reply(
        "⚙️ **Bot Settings Panel**",
        reply_markup=keyboard
    )
