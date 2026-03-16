from bot import Bot
from pyrogram.types import Message
from pyrogram import filters
from config import USER_REPLY_TEXT
from datetime import datetime
from helper_func import get_readable_time
from database.database import is_admin

#-------------------------------
#STATS COMMAND (Admin Only)
#-------------------------------

@Bot.on_message(filters.command("stats") & filters.private)
async def stats(bot: Bot, message: Message):

user_id = message.from_user.id

# Check admin from database
if not await is_admin(user_id):
    await message.reply("❌ You are not authorized to use this command.")
    return

now = datetime.now()
delta = now - bot.uptime
uptime = get_readable_time(delta.seconds)

await message.reply(f"⏱ Bot Uptime : {uptime}")

#-------------------------------
#AUTO USER REPLY
#-------------------------------

@Bot.on_message(filters.private & filters.incoming)
async def useless(_, message: Message):

# Ignore commands
if message.text and message.text.startswith("/"):
    return

if USER_REPLY_TEXT:
    await message.reply(USER_REPLY_TEXT)
