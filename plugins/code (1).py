
from pyrogram import Client, filters, enums
from pyrogram.types import *
from pyrogram.errors import *
import os

# Environment variables for channel IDs
F_SUB1 = int(os.environ.get('F_SUB1', '-1001593340575'))
F_SUB2 = int(os.environ.get('F_SUB2', '-1001917804203'))
F_SUB3 = int(os.environ.get('F_SUB3', '-1002109163181'))

# Admin user ID (replace with the actual admin user ID)
ADMIN_USER_ID = int(os.environ.get("ADMIN_USER_ID", "5356695781"))

# Variable to control the join channels feature
JOIN_CHANNELS_ENABLED = True  # Initialize as enabled

# --- Removed Admin Commands: joinchannelon, joinchanneloff ---
# These commands are no longer needed as the setting will be controlled via the /settings button.
# --- End Removed Admin Commands ---


@Client.on_message(filters.command("joinchannels") & filters.private)
async def join_channels(client: Client, message: Message):
    """
    Checks user's membership in specified channels and prompts to join if not a member.
    """
    global JOIN_CHANNELS_ENABLED

    if not JOIN_CHANNELS_ENABLED:
        await message.reply_text("This feature is currently disabled.")
        return

    user_id = message.from_user.id

    member_statuses = {}
    keyboard_buttons = []

    for channel_id in [F_SUB1, F_SUB2, F_SUB3]:
        # Skip if channel_id is 0 (or empty, as a safeguard if env var is missing)
        if not channel_id:
            continue
        try:
            member = await client.get_chat_member(channel_id, user_id)
            if member.status in [enums.ChatMemberStatus.MEMBER, enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER]:
                member_statuses[channel_id] = "✅"
        except UserNotParticipant:
            # Get the invite link for the channel
            try:
                invite_link = await client.export_chat_invite_link(channel_id)
            except Exception as e:
                print(f"Error getting invite link for channel ID {channel_id}: {e}")
                member_statuses[channel_id] = "⚠️ Error" # Indicate an issue retrieving the link
                continue # Skip to the next channel

            try:
                channel = await client.get_chat(channel_id)
                channel_title = channel.title
            except Exception as e:
                print(f"Error getting chat info for channel ID {channel_id}: {e}")
                channel_title = f"Channel ID: {channel_id}" # Fallback title
                member_statuses[channel_id] = "⚠️ Error"
                continue

            keyboard_button = InlineKeyboardButton(
                text=f"{channel_title}",
                url=invite_link
            )
            keyboard_buttons.append(keyboard_button)
            member_statuses[channel_id] = "❌"
        except Exception as e: # Catch other potential errors during get_chat_member
            print(f"Error checking chat member for channel ID {channel_id}: {e}")
            member_statuses[channel_id] = "⚠️ Error"
            continue


    response = "⚡️ 𝗖𝗵𝗲𝗰𝗸𝗼𝘂𝘁 𝗢𝘂𝗿 𝗖𝗵𝗮𝗻𝗻𝗲𝗹𝘀 ⚡️\n\n"
    for channel_id in [F_SUB1, F_SUB2, F_SUB3]:
        if not channel_id: # Skip if channel_id is 0
            continue
        try:
            channel_title = (await client.get_chat(channel_id)).title
        except Exception as e:
            print(f"Error getting channel title for channel ID {channel_id}: {e}")
            channel_title = f"Channel ID: {channel_id}"  # Fallback
        
        # Ensure channel_id exists in member_statuses before trying to access
        status_emoji = member_statuses.get(channel_id, "❓ Unknown")
        response += f"{channel_title} {status_emoji}\n"

    response += """
𝖩𝗈𝗂𝗇 @sd_bots 𝖥𝗈𝗋 𝖬𝗈𝗋𝖾"""

    if keyboard_buttons:
        keyboard = InlineKeyboardMarkup(
            [[button] for button in keyboard_buttons]
        )
        await message.reply_text(response, reply_markup=keyboard)
    else:
        await message.reply_text(response)


# --- Settings Keyboard and Callbacks ---

def build_settings_keyboard():
    """
    Builds the inline keyboard for bot settings, reflecting the current state.
    """
    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Join Channels: " + ("ON ✅" if JOIN_CHANNELS_ENABLED else "OFF 🚫"), callback_data="toggle_joinchannels")]
        ]
    )
    return keyboard


@Client.on_message(filters.command("settings") & filters.private)
async def settings_command(client: Client, message: Message):
    """
    Displays a settings menu with a button to toggle the join channels feature (admin only).
    """
    user_id = message.from_user.id

    if user_id != ADMIN_USER_ID:
        await message.reply_text("Only the admin can access settings.")
        return

    await message.reply_text("Bot Settings:", reply_markup=build_settings_keyboard())


@Client.on_callback_query(filters.regex("toggle_joinchannels"))
async def toggle_joinchannels_callback(client: Client, callback_query: CallbackQuery):
    """
    Handles the callback query for toggling the join channels feature ON/OFF.
    """
    global JOIN_CHANNELS_ENABLED
    user_id = callback_query.from_user.id

    if user_id != ADMIN_USER_ID:
        await callback_query.answer("You are not authorized to change settings.", show_alert=True)
        return

    JOIN_CHANNELS_ENABLED = not JOIN_CHANNELS_ENABLED  # Toggle the state
    await callback_query.edit_message_text("Bot Settings:", reply_markup=build_settings_keyboard())
    await callback_query.answer(f"Join channels feature is now {'ENABLED' if JOIN_CHANNELS_ENABLED else 'DISABLED'}.", show_alert=True)


print("Bot Started!")

