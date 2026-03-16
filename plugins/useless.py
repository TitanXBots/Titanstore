from bot import Bot
from pyrogram.types import Message
from pyrogram import filters
from config import BOT_STATS_TEXT, USER_REPLY_TEXT
from datetime import datetime
from helper_func import get_readable_time
from database.database import is_admin   # import admin check from database


@Bot.on_message(filters.command("stats") & filters.private)
async def stats(bot: Bot, message: Message):

user_id = message.from_user.id

# Check admin from database
if not await is_admin(user_id):
    await message.reply("❌ You are not authorized to use this command.")
    return

now = datetime.now()
delta = now - bot.uptime
time = get_readable_time(delta.seconds)

await message.reply(BOT_STATS_TEXT.format(uptime=time))


@Bot.on_message(filters.private & filters.incoming)
async def useless(_, message: Message):

# Ignore commands like /start /stats
if message.text and message.text.startswith("/"):
    return

if USER_REPLY_TEXT:
    await message.reply(USER_REPLY_TEXT)
