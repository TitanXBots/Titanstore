import logging
import datetime
import os
import sys  # Import sys for os.execv
import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import ADMINS, LOG_CHANNEL_ID

RESTART_TXT = """
Bᴏᴛ Rᴇsᴛᴀʀᴛᴇᴅ !

📅 Dᴀᴛᴇ : {date}
⏰ Tɪᴍᴇ : {time}
🌐 Tɪᴍᴇᴢᴏɴᴇ : Asia/Kolkata
🛠️ Bᴜɪʟᴅ Sᴛᴀᴛᴜs: v2.7.1 [ Sᴛᴀʙʟᴇ ]
"""

# Setup Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)  # Changed name to __name__

# Global variable to control restart functionality
RESTART_ENABLED = True

@Client.on_message(filters.command("restart") & filters.private & filters.user(ADMINS))
async def send_restart_message(client, message):
    global RESTART_ENABLED
    if not RESTART_ENABLED:
        await message.reply_text("Restart functionality is currently disabled.")
        return

    try:
        now = datetime.datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H:%M:%S")
        formatted_text = RESTART_TXT.format(date=date_str, time=time_str)

        # Send restart message to the user
        await message.reply_text(formatted_text)
        logger.info(f"Restart command received from user {message.from_user.id} in chat {message.chat.id}.")

        # Send restart message to the log channel (optional)
        if LOG_CHANNEL_ID:
            try:
                await client.send_message(LOG_CHANNEL_ID, formatted_text)
                logger.info(f"Sent restart notification to the log channel {LOG_CHANNEL_ID}")
            except Exception as e:
                logger.error(f"Failed to send restart notification to the log channel: {e}")

        # Perform the actual restart (using os.execv)
        logger.info("Initiating bot restart.")
        await message.reply_text("Bot Restarted ✅")
        os.execv(sys.executable, [sys.executable] + sys.argv)  # Use sys.executable and sys.argv for correct restart

    except Exception as e:
        logger.error(f"Error processing restart command: {e}")
        await client.send_message(
            message.chat.id,
            "An error occurred during restart. Please check the logs.",
        )

@Client.on_message(filters.command("restart") & filters.private & ~filters.user(ADMINS))
async def not_admin_reply(client, message):
  await message.reply_text("You are not authorized to use this command.")

@Client.on_message(filters.command("toggle_restart") & filters.private & filters.user(ADMINS))
async def toggle_restart(client, message):
    global RESTART_ENABLED
    RESTART_ENABLED = not RESTART_ENABLED
    status = "enabled" if RESTART_ENABLED else "disabled"
    await message.reply_text(f"Restart functionality is now {status}.")
    logger.info(f"Restart functionality toggled to {status} by user {message.from_user.id}")

@Client.on_message(filters.command("restart_status") & filters.private & filters.user(ADMINS))
async def restart_status(client, message):
    global RESTART_ENABLED
    status = "enabled" if RESTART_ENABLED else "disabled"
    await message.reply_text(f"Restart functionality is currently {status}.")

if __name__ == '__main__':  # Use __name__ for the main check
    app = Client("my_bot")  # Initialize your bot client (replace "my_bot" with your session name)
    app.run()  # Start the bot
