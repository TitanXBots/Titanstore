from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery

# Replace with your admin user ID
ADMIN_USER_ID = 123456789  

# Global toggle variable
JOIN_CHANNELS_ENABLED = True


# ------------------ SETTINGS KEYBOARD ------------------
def build_settings_keyboard():
    """Builds the settings keyboard with a close button."""
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "🔁 Toggle Join Channels", callback_data="toggle_joinchannels"
                )
            ],
            [
                InlineKeyboardButton("❌ Close Settings", callback_data="close_settings")
            ]
        ]
    )
    return keyboard


# ------------------ CLOSE BUTTON HANDLER ------------------
@Client.on_callback_query(filters.regex("^close_settings$"))
async def close_settings_callback(client: Client, callback_query: CallbackQuery):
    """Deletes the settings message when 'Close' is pressed."""
    try:
        await callback_query.message.delete()
    except Exception:
        await callback_query.answer("Unable to close the message.", show_alert=True)
    else:
        await callback_query.answer("Settings closed ✅", show_alert=False)


# ------------------ SETTINGS COMMAND ------------------
@Client.on_message(filters.command("settings") & filters.private)
async def settings_command(client: Client, message: Message):
    """Displays a settings menu (admin only)."""
    if message.from_user.id != ADMIN_USER_ID:
        await message.reply_text("⚠️ ᴏɴʟʏ ᴛʜᴇ ᴀᴅᴍɪɴ ᴄᴀɴ ᴀᴄᴄᴇꜱꜱ ꜱᴇᴛᴛɪɴɢꜱ.")
        return

    text = (
        "⚙️ **Bot Settings**\n\n"
        f"📢 **Join Channels:** {'✅ ON' if JOIN_CHANNELS_ENABLED else '❌ OFF'}\n\n"
        "You can use these commands:\n"
        "`/joinchannelon` - Enable join channels\n"
        "`/joinchanneloff` - Disable join channels"
    )

    await message.reply_text(text, reply_markup=build_settings_keyboard())


# ------------------ TOGGLE BUTTON HANDLER ------------------
@Client.on_callback_query(filters.regex("toggle_joinchannels"))
async def toggle_joinchannels_callback(client: Client, callback_query: CallbackQuery):
    """Handles the callback query for toggling the join channels feature."""
    global JOIN_CHANNELS_ENABLED

    if callback_query.from_user.id != ADMIN_USER_ID:
        await callback_query.answer("❌ You are not authorized to change settings.", show_alert=True)
        return

    # Toggle the feature
    JOIN_CHANNELS_ENABLED = not JOIN_CHANNELS_ENABLED

    # Update message
    text = (
        "⚙️ **Bot Settings**\n\n"
        f"📢 **Join Channels:** {'✅ ON' if JOIN_CHANNELS_ENABLED else '❌ OFF'}\n\n"
        "You can use these commands:\n"
        "`/joinchannelon` - Enable join channels\n"
        "`/joinchanneloff` - Disable join channels"
    )

    await callback_query.edit_message_text(text, reply_markup=build_settings_keyboard())
    await callback_query.answer(
        f"Join Channels feature is now {'ENABLED ✅' if JOIN_CHANNELS_ENABLED else 'DISABLED ❌'}."
    )


# ------------------ /JOINCHANNELON COMMAND ------------------
@Client.on_message(filters.command("joinchannelon") & filters.private)
async def join_channel_on(client: Client, message: Message):
    """Command to enable join channel requirement."""
    global JOIN_CHANNELS_ENABLED

    if message.from_user.id != ADMIN_USER_ID:
        await message.reply_text("❌ You are not authorized to use this command.")
        return

    JOIN_CHANNELS_ENABLED = True
    await message.reply_text("✅ Join Channels feature has been **ENABLED**.")


# ------------------ /JOINCHANNELOFF COMMAND ------------------
@Client.on_message(filters.command("joinchanneloff") & filters.private)
async def join_channel_off(client: Client, message: Message):
    """Command to disable join channel requirement."""
    global JOIN_CHANNELS_ENABLED

    if message.from_user.id != ADMIN_USER_ID:
        await message.reply_text("❌ You are not authorized to use this command.")
        return

    JOIN_CHANNELS_ENABLED = False
    await message.reply_text("🚫 Join Channels feature has been **DISABLED**.")
