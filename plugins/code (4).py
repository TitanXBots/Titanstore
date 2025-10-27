
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message

# --- Configuration ---
# IMPORTANT: Replace these with your actual values
ADMIN_USER_ID = 5356695781  # <--- MAKE SURE THIS IS YOUR CORRECT USER ID
F_SUB1 = -1001593340575   # Replace with your first channel ID (e.g., -100XXXXXXXXXX)
F_SUB2 = -1001917804203   # Replace with your second channel ID
F_SUB3 = -1002109163181   # Replace with your third channel ID
# --- End Configuration ---

# Global state variable for the feature
JOIN_CHANNELS_ENABLED = True # Default state: True (enabled)

# ==========================================================
#                  ADMIN FEATURE MANAGEMENT COMMAND
# ==========================================================
from pyrogram.errors import UserNotParticipant

# ==========================================================
#                  GLOBAL VARIABLES
# ==========================================================

# ==========================================================
#                  MANAGE JOIN CHANNELS FEATURE
# ==========================================================
@Client.on_message(filters.command("managejoinchannels") & filters.private)
async def manage_join_channels_feature(client: Client, message):
    """
    Admin command to display current status of join channels feature and provide toggle buttons.
    """
    if message.from_user.id != ADMIN_USER_ID:
        await message.reply_text("ᴏɴʟʏ ᴛʜᴇ ᴀᴅᴍɪɴ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ.")
        return

    text = f"⚙️ **Join Channels Feature:** {'ON ✅' if JOIN_CHANNELS_ENABLED else 'OFF ❌'}"
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text="🔁 Toggle Join Channels",
                    callback_data="toggle_joinchannels"
                )
            ],
            [
                InlineKeyboardButton(
                    text="❌ Close",
                    callback_data="close_settings"
                )
            ]
        ]
    )

    await message.reply_text(text, reply_markup=keyboard)


# ==========================================================
#                  CALLBACK HANDLER
# ==========================================================
@Client.on_callback_query(filters.regex("toggle_joinchannels"))
async def toggle_joinchannels_callback(client, callback_query):
    """
    Toggles the join channels feature ON/OFF from inline buttons.
    """
    global JOIN_CHANNELS_ENABLED

    if callback_query.from_user.id != ADMIN_USER_ID:
        await callback_query.answer("You’re not authorized ❌", show_alert=True)
        return

    JOIN_CHANNELS_ENABLED = not JOIN_CHANNELS_ENABLED
    status = "ON ✅" if JOIN_CHANNELS_ENABLED else "OFF ❌"

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text="🔁 Toggle Join Channels",
                    callback_data="toggle_joinchannels"
                )
            ],
            [
                InlineKeyboardButton(
                    text="❌ Close",
                    callback_data="close_settings"
                )
            ]
        ]
    )

    await callback_query.message.edit_text(
        f"⚙️ **Join Channels Feature:** {status}",
        reply_markup=keyboard
    )
    await callback_query.answer(f"Feature turned {status.replace('✅', '').replace('❌', '')}!")


@Client.on_callback_query(filters.regex("close_settings"))
async def close_settings_callback(client, callback_query):
    """Closes the manage menu."""
    await callback_query.message.delete()
    await callback_query.answer("Closed ✅", show_alert=False)


# ==========================================================
#                  JOIN CHANNELS COMMAND
# ==========================================================
@Client.on_message(filters.command("joinchannels") & filters.private)
async def join_channels(client: Client, message):
    """
    Checks user's membership in specified channels and prompts to join if not a member.
    """
    global JOIN_CHANNELS_ENABLED

    if not JOIN_CHANNELS_ENABLED:
        await message.reply_text("⚙️ ᴛʜɪꜱ ꜰᴇᴀᴛᴜʀᴇ ɪꜱ ᴅɪꜱᴀʙʟᴇᴅ ʙʏ ᴛʜᴇ ᴀᴅᴍɪɴ.")
        return

    user_id = message.from_user.id
    member_statuses = {}
    keyboard_buttons = []

    for channel_id in [F_SUB1, F_SUB2, F_SUB3]:
        try:
            member = await client.get_chat_member(channel_id, user_id)
            if member.status in [
                enums.ChatMemberStatus.MEMBER,
                enums.ChatMemberStatus.ADMINISTRATOR,
                enums.ChatMemberStatus.OWNER,
            ]:
                member_statuses[channel_id] = "✅"
        except UserNotParticipant:
            try:
                invite_link = await client.export_chat_invite_link(channel_id)
                channel = await client.get_chat(channel_id)
                keyboard_buttons.append(InlineKeyboardButton(text=channel.title, url=invite_link))
                member_statuses[channel_id] = "❌"
            except Exception as e:
                print(f"Error getting info for channel {channel_id}: {e}")
                member_statuses[channel_id] = "⚠️"

    response = "⚡️ **CHECK OUT OUR CHANNELS** ⚡️\n\n"
    for channel_id in [F_SUB1, F_SUB2, F_SUB3]:
        try:
            channel_title = (await client.get_chat(channel_id)).title
        except Exception:
            channel_title = f"Channel ID: {channel_id}"
        response += f"{channel_title} {member_statuses.get(channel_id, '⚠️')}\n"

    response += "\nJoin @TitanXBots For More 🔥"

    if keyboard_buttons:
        keyboard = InlineKeyboardMarkup([[btn] for btn in keyboard_buttons])
        await message.reply_text(response, reply_markup=keyboard)
    else:
        await message.reply_text(response)
