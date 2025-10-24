import logging
import datetime
import os
import sys  # Import sys for os.execv
import asyncio
from pyrogram import Client, filters, types
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
logger = logging.getLogger(__name__)  # Use __name__ for logging module name

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

@Client.on_message(filters.command("restart") & filters.private & ~filters.user(ADMINS))
async def not_admin_reply(client, message):
  await message.reply_text("ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀᴜᴛʜᴏʀɪᴢᴇᴅ ᴛᴏ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ.")

# Example settings command with inline buttons
@Client.on_message(filters.command("settings") & filters.private & filters.user(ADMINS))
async def settings_command(client, message):
    keyboard = types.InlineKeyboardMarkup(
        [
            [
                types.InlineKeyboardButton("Restart On", callback_data="restarton"),
                types.InlineKeyboardButton("Restart Off", callback_data="restartoff"),
            ]
        ]
    )

    await message.reply_text("Bot Settings:", reply_markup=keyboard)

# Callback query handler for the buttons
@Client.on_callback_query(filters.regex("restarton|restartoff") & filters.user(ADMINS))
async def restart_callback(client, callback_query):
    action = callback_query.data
    user_id = callback_query.from_user.id

    if action == "restarton":
        # Implement logic to turn restart on (e.g., set a flag)
        await callback_query.answer("Restart is now ON.")
        await callback_query.edit_message_text("Restart is now **ON**.")
        logger.info(f"Restart turned ON by user {user_id}")
    elif action == "restartoff":
        # Implement logic to turn restart off (e.g., unset a flag)
        await callback_query.answer("Restart is now OFF.")
        await callback_query.edit_message_text("Restart is now **OFF**.")
        logger.info(f"Restart turned OFF by user {user_id}")
    else:
        await callback_query.answer("Invalid action.")


if __name__ == '__main__':
    app = Client("my_bot")  # Initialize your bot client (replace "my_bot" with your session name)
    app.run()  # Start the bot
