# useless.py

from bot import Bot
from pyrogram import filters
from pyrogram.types import Message
from config import USER_REPLY_TEXT, BOT_STATS_TEXT
from database.database import is_admin  # dynamic admin/owner check
from datetime import datetime
from helper_func import get_readable_time

# -------------------------------
# Private messages auto-reply for all users
# -------------------------------
@Bot.on_message(filters.private & filters.incoming)
async def user_reply(_, message: Message):
    if USER_REPLY_TEXT:
        await message.reply(USER_REPLY_TEXT)


# -------------------------------
# Admin-only /stats command with feedback for normal users
# -------------------------------
@Bot.on_message(filters.command("stats"))
async def stats(bot: Bot, message: Message):
    user_id = message.from_user.id
    if not await is_admin(user_id):  # only allow admins/owner
        await message.reply("❌ You are not authorized to use this command.")
        return

    uptime = getattr(bot, "uptime", None)
    if uptime is None:
        await message.reply("Bot uptime not initialized.")
        return

    now = datetime.now()
    delta = now - bot.uptime
    readable_time = get_readable_time(delta.seconds)

    await message.reply(BOT_STATS_TEXT.format(uptime=readable_time))
