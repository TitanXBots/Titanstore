import logging
import datetime
import os
import sys  # Import sys for os.execv
import asyncio 
from pyrogram import Client, filters
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
logger = logging.getLogger(__name__)  # Use __name__ instead of name

@Client.on_message(filters.command("restart") & filters.private & filters.user(ADMINS))
async def send_restart_message(client, message):
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

@Client.on_message(filters.command("restart") & filters.private & filters.user(ADMINS))
async def not_admin_reply(client, message):
  await message.reply_text("You are not authorized to use this command.")


if __name__ == '__main__':  # Use __name__ for the main check
    app = Client("my_bot")  # Initialize your bot client (replace "my_bot" with your session name)
    app.run()  # Start the bot
