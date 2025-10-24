import logging
import datetime
import os
import sys
from pyrogram import Client, filters, types
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import ADMINS, LOG_CHANNEL_ID

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Persistent Toggle Variable ---
RESTART_ENABLED = True  # Default value (True = restart works)

RESTART_TXT = """
Bᴏᴛ Rᴇsᴛᴀʀᴛᴇᴅ !

📅 Dᴀᴛᴇ : {date}
⏰ Tɪᴍᴇ : {time}
🌐 Tɪᴍᴇᴢᴏɴᴇ : Asia/Kolkata
🛠️ Bᴜɪʟᴅ Sᴛᴀᴛᴜs: v2.7.1 [ Sᴛᴀʙʟᴇ ]
"""

# --- Restart Command ---
@Client.on_message(filters.command("restart") & filters.private & filters.user(ADMINS))
async def send_restart_message(client, message):
    global RESTART_ENABLED

    if not RESTART_ENABLED:
        await message.reply_text("⚠️ Restart feature is currently **disabled**.")
        return

    try:
        now = datetime.datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H:%M:%S")
        formatted_text = RESTART_TXT.format(date=date_str, time=time_str)

        await message.reply_text(formatted_text)
        logger.info(f"Restart command received from user {message.from_user.id}.")

        if LOG_CHANNEL_ID:
            try:
                await client.send_message(LOG_CHANNEL_ID, formatted_text)
            except Exception as e:
                logger.error(f"Failed to send restart notification: {e}")

        await message.reply_text("Bot Restarted ✅")
        os.execv(sys.executable, [sys.executable] + sys.argv)

    except Exception as e:
        logger.error(f"Error during restart: {e}")
        await message.reply_text("An error occurred during restart. Check logs.")


# --- Non-Admin Restart Block ---
@Client.on_message(filters.command("restart") & filters.private & ~filters.user(ADMINS))
async def not_admin_reply(client, message):
    await message.reply_text("🚫 You are not authorized to use this command.")


# --- Settings Command ---
@Client.on_message(filters.command("settings") & filters.private & filters.user(ADMINS))
async def settings_command(client, message):
    global RESTART_ENABLED

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    f"Restart: {'ON ✅' if RESTART_ENABLED else 'OFF ❌'}",
                    callback_data="toggle_restart"
                )
            ]
        ]
    )
    await message.reply_text("⚙️ Bot Settings:", reply_markup=keyboard)


# --- Callback Handler ---
@Client.on_callback_query(filters.regex("toggle_restart") & filters.user(ADMINS))
async def restart_toggle_callback(client, callback_query):
    global RESTART_ENABLED

    RESTART_ENABLED = not RESTART_ENABLED  # Flip state
    new_status = "ON ✅" if RESTART_ENABLED else "OFF ❌"

    await callback_query.answer(f"Restart is now {new_status}")
    await callback_query.edit_message_text(
        f"⚙️ Bot Settings:\nRestart is now **{new_status}**",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton(f"Restart: {new_status}", callback_data="toggle_restart")]]
        )
    )
    logger.info(f"Restart feature toggled to {RESTART_ENABLED} by user {callback_query.from_user.id}")


# --- Run Bot ---
if __name__ == "__main__":
    app = Client("my_bot")
    app.run()
