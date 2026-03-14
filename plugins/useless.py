from bot import Bot
from pyrogram.types import Message
from pyrogram import filters
from config import BOT_STATS_TEXT, USER_REPLY_TEXT
from datetime import datetime
from helper_func import get_readable_time, is_admin  # <-- use database-based admin check

# -------------------------------
# STATS COMMAND
# -------------------------------
@Bot.on_message(filters.command('stats') & filters.private)
async def stats(bot: Bot, message: Message):
    user_id = message.from_user.id
    if not await is_admin(user_id):  # check if user is admin/owner from DB
        return

    now = datetime.now()
    delta = now - bot.uptime
    time = get_readable_time(delta.seconds)
    await message.reply(BOT_STATS_TEXT.format(uptime=time))

# -------------------------------
# REPLY TO ALL USERS
# -------------------------------
@Bot.on_message(filters.private & filters.incoming)
async def useless(_, message: Message):
    if USER_REPLY_TEXT:
        await message.reply(USER_REPLY_TEXT)
