
import os
import asyncio
import logging
from pyrogram import Client, filters, enums
from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    Message,
    CallbackQuery,
)
from config import ADMINS, LOG_CHANNEL_ID

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Define global variables to store settings states.  In a real bot, these
# should be stored in a database or persistent storage.  This is a simplified example.
JOIN_CHANNELS_ENABLED = True  # Default: Join Channels feature ON
AUTO_DELETE_ENABLED = True  # Default: Auto Delete feature ON


@Client.on_message(filters.command("settings") & filters.private & filters.user(ADMINS))
async def settings_command(client: Client, message: Message):
    """
    Displays the bot settings with inline buttons to enable/disable features.
    """
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "Restart Bot", callback_data="restart_bot"
                )
            ],
            [
                InlineKeyboardButton(
                    f"Join Channels: {'ON ✅' if JOIN_CHANNELS_ENABLED else 'OFF ❌'}",
                    callback_data="toggle_joinchannels",
                )
            ],
            [
                InlineKeyboardButton(
                    f"Auto Delete: {'ON ✅' if AUTO_DELETE_ENABLED else 'OFF ❌'}",
                    callback_data="toggle_autodelete",
                )
            ],
        ]
    )

    await message.reply_text("Bot Settings:", reply_markup=keyboard)


@Client.on_callback_query(filters.regex("^restart_bot$"))
async def restart_bot_callback(client: Client, query: CallbackQuery):
    """
    Restarts the bot.  This is a basic example.
    """
    try:
        await query.answer("Restarting bot...")
        await query.message.reply_text("Bot Restarting...")

        # Perform the actual restart (using os.execv)
        logger.info("Initiating bot restart using os.execv.")
        os.execv(sys.executable, [sys.executable] + sys.argv)
    except Exception as e:
        logger.error(f"Error during restart: {e}")
        await query.message.reply_text(
            f"An error occurred during restart: {e}. Check logs."
        )


@Client.on_callback_query(filters.regex("^toggle_joinchannels$"))
async def toggle_joinchannels_callback(client: Client, query: CallbackQuery):
    """
    Toggles the Join Channels feature on or off.
    """
    global JOIN_CHANNELS_ENABLED
    JOIN_CHANNELS_ENABLED = not JOIN_CHANNELS_ENABLED
    await query.answer(
        f"Join Channels is now {'ON' if JOIN_CHANNELS_ENABLED else 'OFF'}"
    )

    # Update the button text
    new_keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "Restart Bot", callback_data="restart_bot"
                )
            ],
            [
                InlineKeyboardButton(
                    f"Join Channels: {'ON ✅' if JOIN_CHANNELS_ENABLED else 'OFF ❌'}",
                    callback_data="toggle_joinchannels",
                )
            ],
            [
                InlineKeyboardButton(
                    f"Auto Delete: {'ON ✅' if AUTO_DELETE_ENABLED else 'OFF ❌'}",
                    callback_data="toggle_autodelete",
                )
            ],
        ]
    )
    try:
        await query.edit_message_reply_markup(reply_markup=new_keyboard)
    except Exception as e:
        logger.error(f"Error updating message markup: {e}")


@Client.on_callback_query(filters.regex("^toggle_autodelete$"))
async def toggle_autodelete_callback(client: Client, query: CallbackQuery):
    """
    Toggles the Auto Delete feature on or off.
    """
    global AUTO_DELETE_ENABLED
    AUTO_DELETE_ENABLED = not AUTO_DELETE_ENABLED
    await query.answer(f"Auto Delete is now {'ON' if AUTO_DELETE_ENABLED else 'OFF'}")

    # Update the button text
    new_keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "Restart Bot", callback_data="restart_bot"
                )
            ],
            [
                InlineKeyboardButton(
                    f"Join Channels: {'ON ✅' if JOIN_CHANNELS_ENABLED else 'OFF ❌'}",
                    callback_data="toggle_joinchannels",
                )
            ],
            [
                InlineKeyboardButton(
                    f"Auto Delete: {'ON ✅' if AUTO_DELETE_ENABLED else 'OFF ❌'}",
                    callback_data="toggle_autodelete",
                )
            ],
        ]
    )

    try:
        await query.edit_message_reply_markup(reply_markup=new_keyboard)
    except Exception as e:
        logger.error(f"Error updating message markup: {e}")


# Example of how to use the AUTO_DELETE_ENABLED setting (adapt to your needs)
async def some_function_with_auto_delete(client: Client, chat_id: int, message_ids: list):
    """
    Example function that demonstrates the usage of AUTO_DELETE_ENABLED.
    """
    if AUTO_DELETE_ENABLED:
        try:
            await asyncio.sleep(30)  # Example delay
            await client.delete_messages(chat_id=chat_id, message_ids=message_ids)
            logger.info(f"Deleted {len(message_ids)} messages from chat {chat_id}.")
        except Exception as e:
            logger.error(f"Error deleting messages: {e}")
    else:
        logger.info("Auto Delete is disabled. Messages will not be deleted.")

# Example of how to use the JOIN_CHANNELS_ENABLED setting (adapt to your needs)
async def some_function_requiring_join_channels(client: Client, message: Message):
        if JOIN_CHANNELS_ENABLED:
            #Your logic that required join channels
            await message.reply_text("Join channel is enabled")
        else:
            # send messages to user to join the channel.
            await message.reply_text("Join channel is disabled. Please enable it.")

