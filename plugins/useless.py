from bot import Bot
from pyrogram.types import Message
from pyrogram import filters
from datetime import datetime
from helper_func import get_readable_time
from config import BOT_STATS_TEXT, USER_REPLY_TEXT
from database.database import is_admin  # <- Correct import from DB module

# -------------------------------
# Stats command (admin only)
# -------------------------------
@Bot.on_message(filters.command('stats'))
async def stats(bot: Bot, message: Message):
    user_id = message.from_user.id
    if not await is_admin(user_id):  # Check if sender is admin/owner
        return  # Ignore non-admins

    now = datetime.now()
    delta = now - bot.uptime  # Make sure bot.uptime is initialized at startup
    readable_time = get_readable_time(delta.seconds)
    await message.reply(BOT_STATS_TEXT.format(uptime=readable_time))


# -------------------------------
# Private messages auto-reply
# -------------------------------
@Bot.on_message(filters.private & filters.incoming)
async def user_reply(_, message: Message):
    if USER_REPLY_TEXT:
        await message.reply(USER_REPLY_TEXT)
