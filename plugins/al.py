import os
import sys
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message

# --- Global Settings (for demo, PERSISTENCE IS RECOMMENDED FOR PRODUCTION) ---
# In a real bot, these would be loaded from a database or config file.
bot_settings = {
    "join_channel_enabled": True,  # Default state for join channel messages
    "auto_delete_enabled": False   # Default state for auto delete
}

# --- Helper Function to Generate Settings Keyboard ---
def generate_settings_keyboard():
    """Generates the inline keyboard for the settings menu."""
    join_channel_status = "ON" if bot_settings["join_channel_enabled"] else "OFF"
    auto_delete_status = "ON" if bot_settings["auto_delete_enabled"] else "OFF"

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    f"Join Channel Messages: {join_channel_status}",
                    callback_data="toggle_join_channel"
                )
            ],
            [
                InlineKeyboardButton(
                    f"Auto Delete Messages: {auto_delete_status}",
                    callback_data="toggle_auto_delete"
                )
            ],
            [
                InlineKeyboardButton(
                    "♻️ Restart Bot",
                    callback_data="restart_bot"
                )
            ]
        ]
    )
    return keyboard

# --- Command Handler for /settings ---
@client.on_message(filters.command("settings") & filters.user(ADMIN_ID))
async def settings_command(client: Client, message: Message):
    """Handles the /settings command, showing the current bot settings."""
    await message.reply_text(
        "⚙️ Bot Settings:",
        reply_markup=generate_settings_keyboard()
    )

# --- Callback Query Handler for Buttons ---
@client.on_callback_query()
async def callback_handler(client: Client, callback_query: CallbackQuery):
    """Handles button presses from the settings menu."""
    user_id = callback_query.from_user.id

 # Ensure only the admin can interact with these buttons
    if user_id != ADMIN_ID:
        await callback_query.answer("You are not authorized to change settings.", show_alert=True)
        return

    data = callback_query.data
    message = callback_query.message

    if data == "toggle_join_channel":
        bot_settings["join_channel_enabled"] = not bot_settings["join_channel_enabled"]
        status = "enabled" if bot_settings["join_channel_enabled"] else "disabled"
        await message.edit_reply_markup(reply_markup=generate_settings_keyboard())
        await callback_query.answer(f"Join Channel messages {status}.")
        print(f"Join Channel messages {status}.")

    elif data == "toggle_auto_delete":
        bot_settings["auto_delete_enabled"] = not bot_settings["auto_delete_enabled"]
        status = "enabled" if bot_settings["auto_delete_enabled"] else "disabled"
        await message.edit_reply_markup(reply_markup=generate_settings_keyboard())
        await callback_query.answer(f"Auto Delete messages {status}.")
        print(f"Auto Delete messages {status}.")

    elif data == "restart_bot":
        await callback_query.answer("Restarting bot...", show_alert=True)
        await message.edit_text("🔄 Bot is restarting...")
        print("Bot is restarting...")
        # This will restart the current Python script
        os.execv(sys.executable, ['python'] + sys.argv)

    else:
        await callback_query.answer("Unknown action.")
