
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
@Client.on_message(filters.command("managejoinchannels") & filters.private)
async def manage_join_channels_feature(client: Client, message: Message):
    """
    Admin command to display the current status of the join channels feature
    and provide buttons to toggle it.
    """
    # --- DEBUGGING LINE ---
    print(f"Attempted /managejoinchannels. Sender ID: {message.from_user.id}, Configured Admin ID: {ADMIN_USER_ID}")
    # --- END DEBUGGING LINE ---

    if message.from_user.id != ADMIN_USER_ID:
        await message.reply_text("ᴏɴʟʏ ᴛʜᴇ ᴀᴅᴍɪɴ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ.")
        return

    status = "ᴇɴᴀʙʟᴇᴅ ✅" if JOIN_CHANNELS_ENABLED else "ᴅɪꜱᴀʙʟᴇᴅ 🚫"
    text = f"ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ ꜰᴇᴀᴛᴜʀᴇ ɪꜱ ᴄᴜʀʀᴇɴᴛʟʏ: {status}\n\n" \
           "ᴜꜱᴇ ᴛʜᴇ ʙᴜᴛᴛᴏɴꜱ ʙᴇʟᴏᴡ ᴛᴏ ᴛᴏɢɢʟᴇ ɪᴛ."

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("ᴇɴᴀʙʟᴇ ✅", callback_data="toggle_join_channels_on"),
                InlineKeyboardButton("ᴅɪꜱᴀʙʟᴇ 🚫", callback_data="toggle_join_channels_off")
            ]
        ]
    )
    await message.reply_text(text, reply_markup=keyboard)

# ==========================================================
#                  CALLBACK QUERY HANDLER FOR FEATURE TOGGLE
# ==========================================================
@Client.on_callback_query(filters.regex("^toggle_join_channels_"))
async def toggle_join_channels_callback(client: Client, callback_query: CallbackQuery):
    """
    Handles inline button presses to enable/disable the join channels feature.
    """
    global JOIN_CHANNELS_ENABLED

    # Ensure only admin can use these buttons
    if callback_query.from_user.id != ADMIN_USER_ID:
        await callback_query.answer("ᴏɴʟʏ ᴛʜᴇ ᴀᴅᴍɪɴ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ ʙᴜᴛᴛᴏɴ.", show_alert=True)
        return

    if callback_query.data == "toggle_join_channels_on":
        JOIN_CHANNELS_ENABLED = True
        response_text = "ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ ꜰᴇᴀᴛᴜʀᴇ ɪꜱ ɴᴏᴡ ᴇɴᴀʙʟᴇᴅ ✅."
    elif callback_query.data == "toggle_join_channels_off":
        JOIN_CHANNELS_ENABLED = False
        response_text = "ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ ꜰᴇᴀᴛᴜʀᴇ ɪꜱ ɴᴏᴡ ᴅɪꜱᴀʙʟᴇᴅ 🚫."
    else:
        await callback_query.answer("ᴜɴᴋɴᴏᴡɴ ᴀᴄᴛɪᴏɴ.", show_alert=True)
        return

    # Update the message with the new status and buttons
    status = "ᴇɴᴀʙʟᴇᴅ ✅" if JOIN_CHANNELS_ENABLED else "ᴅɪꜱᴀʙʟᴇᴅ 🚫"
    new_text = f"ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ ꜰᴇᴀᴛᴜʀᴇ ɪꜱ ᴄᴜʀʀᴇɴᴛʟʏ: {status}\n\n" \
               "ᴜꜱᴇ ᴛʜᴇ ʙᴜᴛᴛᴏɴꜱ ʙᴇʟᴏᴡ ᴛᴏ ᴛᴏɢɢʟᴇ ɪᴛ."

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("ᴇɴᴀʙʟᴇ ✅", callback_data="toggle_join_channels_on"),
                InlineKeyboardButton("ᴅɪꜱᴀʙʟᴇ 🚫", callback_data="toggle_join_channels_off")
            ]
        ]
    )
    await callback_query.edit_message_text(new_text, reply_markup=keyboard)
    await callback_query.answer(response_text) # Show a small toast notification to the admin


# ==========================================================
#                  JOIN CHANNELS COMMAND
# ==========================================================
@Client.on_message(filters.command("joinchannels") & filters.private)
async def join_channels(client: Client, message: Message):
    """
    Checks user's membership in specified channels and prompts to join if not a member.
    This command's functionality is controlled by the JOIN_CHANNELS_ENABLED flag.
    """
    global JOIN_CHANNELS_ENABLED

    if not JOIN_CHANNELS_ENABLED:
        await message.reply_text("⚙️ ᴛʜɪꜱ ꜰᴇᴀᴛᴜʀᴇ ɪꜱ ᴄᴜʀʀᴇɴᴛʟʏ ᴅɪꜱᴀʙʟᴇᴅ ʙʏ ᴛʜᴇ ᴀᴅᴍɪɴ.")
        return

    user_id = message.from_user.id
    member_statuses = {}
    keyboard_buttons = []

    # List of channels to check
    channels_to_check = [F_SUB1, F_SUB2, F_SUB3]

    for channel_id in channels_to_check:
        try:
            member = await client.get_chat_member(channel_id, user_id)
            if member.status in [
                enums.ChatMemberStatus.MEMBER,
                enums.ChatMemberStatus.ADMINISTRATOR,
                enums.ChatMemberStatus.OWNER,
            ]:
                member_statuses[channel_id] = "✅"
            else:
                # User is not a member (e.g., restricted, left, kicked)
                # Treat as not participating to prompt join
                raise Exception # Force the exception block below
        except Exception as e: # Catch UserNotParticipant and other potential errors
            # If user is not a participant or any other error occurs, prompt to join
            try:
                invite_link = await client.export_chat_invite_link(channel_id)
                channel = await client.get_chat(channel_id)
                channel_title = channel.title
                keyboard_buttons.append(InlineKeyboardButton(text=channel_title, url=invite_link))
                member_statuses[channel_id] = "❌"
            except Exception as inner_e:
                print(f"Error getting info or invite link for channel {channel_id}: {inner_e}")
                member_statuses[channel_id] = "⚠️" # Indicate an issue

    response = "⚡️ 𝐂𝐇𝐄𝐂𝐊 𝐎𝐔𝐓 𝐎𝐔𝐑 𝐂𝐇𝐀𝐍𝐍𝐄𝐋𝐒 ⚡️\n\n"
    for channel_id in channels_to_check:
        try:
            channel_title = (await client.get_chat(channel_id)).title
        except Exception:
            channel_title = f"Channel ID: {channel_id}" # Fallback if title can't be fetched
        response += f"{channel_title} {member_statuses.get(channel_id, '⚠️')}\n"

    response += "\nJoin @TitanXBots For More 🔥"

    if keyboard_buttons:
        # If there are channels the user needs to join, show buttons
        keyboard = InlineKeyboardMarkup([[btn] for btn in keyboard_buttons])
        await message.reply_text(response, reply_markup=keyboard)
    else:
        # If user is already a member of all channels, just send the text
        await message.reply_text(response)


# --- IMPORTANT: You need to start your Pyrogram client somewhere in your main script ---
# Example:
# app = Client("my_bot_session", api_id=YOUR_API_ID, api_hash=YOUR_API_HASH, bot_token=YOUR_BOT_TOKEN)
# app.run()
