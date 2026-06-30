from datetime import datetime

from pyrogram import filters
from pyrogram.types import Message

from bot import Bot
from config import BOT_STATS_TEXT, USER_REPLY_TEXT
from helper_func import get_readable_time
from database.database import is_admin


@Bot.on_message(filters.command("stats") & filters.private)
async def stats(bot: Bot, message: Message):

    if not await is_admin(message.from_user.id):
        return

    now = datetime.now()
    delta = now - bot.uptime
    uptime = get_readable_time(delta.seconds)

    await message.reply_text(
        BOT_STATS_TEXT.format(uptime=uptime)
    )


@Bot.on_message(filters.private & filters.incoming & ~filters.command(["stats"]))
async def useless(_, message: Message):

    if USER_REPLY_TEXT:
        await message.reply_text(USER_REPLY_TEXT)
