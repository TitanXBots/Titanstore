from pyrogram import Client, filters, enums
from pyrogram.types import *
from pyrogram.errors import *
import os

# --- Environment variables for channel IDs ---
F_SUB1 = int(os.environ.get('F_SUB1', '-1001593340575'))
F_SUB2 = int(os.environ.get('F_SUB2', '-1001917804203'))
F_SUB3 = int(os.environ.get('F_SUB3', '-1002109163181'))

# --- Admin user ID (replace with the actual admin user ID) ---
ADMIN_USER_ID = int(os.environ.get("ADMIN_USER_ID", "5356695781"))

# --- Variable to control the join channels feature ---
JOIN_CHANNELS_ENABLED = True  # Default ON

# ==========================================================
#                  ADMIN ON / OFF COMMANDS
# ==========================================================
@Client.on_message(filters.command("joinchannelon") & filters.private)
async def join_channel_on(client: Client, message: Message):
    """
    Enables the join channels feature (admin only).
    """
    global JOIN_CHANNELS_ENABLED

    if message.from_user.id != ADMIN_USER_ID:
        await message.reply_text("ONLY THE ADMIN CAN USE THIS COMMAND.")
        return

    JOIN_CHANNELS_ENABLED = True
    await message.reply_text("JOIN CHANNEL FEATURE IS NOW ENABLED ✅.")


@Client.on_message(filters.command("joinchanneloff") & filters.private)
async def join_channel_off(client: Client, message: Message):
    """
    Disables the join channels feature (admin only).
    """
    global JOIN_CHANNELS_ENABLED

    if message.from_user.id != ADMIN_USER_ID:
        await message.reply_text("ONLY THE ADMIN CAN USE THIS COMMAND.")
        return

    JOIN_CHANNELS_ENABLED = False
    await message.reply_text("ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ ꜰᴇᴀᴛᴜʀᴇ ɪꜱ ɴᴏᴡ ᴅɪꜱᴀʙʟᴇᴅ 🚫.")


# ==========================================================
#                  JOIN CHANNELS COMMAND
# ==========================================================
@Client.on_message(filters.command("joinchannels") & filters.private)
async def join_channels(client: Client, message: Message):
    """
    Checks user's membership in specified channels and prompts to join if not a member.
    """
    global JOIN_CHANNELS_ENABLED

    if not JOIN_CHANNELS_ENABLED:
        await message.reply_text("⚙️ ᴛʜɪꜱ ꜰᴇᴀᴛᴜʀᴇ ɪꜱ ᴄᴜʀʀᴇɴᴛʟʏ ᴅɪꜱᴀʙʟᴇᴅ ʙʏ ᴛʜᴇ ᴀᴅᴍɪɴ.")
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
                channel_title = channel.title
                keyboard_buttons.append(InlineKeyboardButton(text=channel_title, url=invite_link))
                member_statuses[channel_id] = "❌"
            except Exception as e:
                print(f"Error getting info for channel {channel_id}: {e}")
                member_statuses[channel_id] = "⚠️"

    response = "⚡️ **Checkout Our Channels** ⚡️\n\n"
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


# ==========================================================
#                     SETTINGS MENU
# ==========================================================
def build_settings_keyboard():
    """
    Builds the inline keyboard for settings.
    """
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    f"Join Channels: {'ON ✅' if JOIN_CHANNELS_ENABLED else 'OFF ❌'}",
                    callback_data="toggle_joinchannels",
                )
            ]
        ]
    )
    return keyboard


@Client.on_message(filters.command("settings") & filters.private)
async def settings_command(client: Client, message: Message):
    """
    Displays a settings menu (admin only).
    """
    if message.from_user.id != ADMIN_USER_ID:
        await message.reply_text("ᴏɴʟʏ ᴛʜᴇ ᴀᴅᴍɪɴ ᴄᴀɴ ᴀᴄᴄᴇꜱꜱ ꜱᴇᴛᴛɪɴɢꜱ.")
        return

    text = (
        "⚙️ BOT SETTINGS\n\n"
        f"ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟꜱ: {'✅ ON' if JOIN_CHANNELS_ENABLED else '❌ OFF'}\n\n"
        "ʏᴏᴜ ᴄᴀɴ ᴇɴᴀʙʟᴇ ᴏʀ ᴅɪꜱᴀʙʟᴇᴅ:\n"
        "ᴛʜᴇ ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟꜱ ᴄᴏᴍᴍᴀɴᴅ ʜᴇʀᴇ`/joinchannelon` or `/joinchanneloff` 👈."
    )

    await message.reply_text(text, reply_markup=build_settings_keyboard())


@Client.on_callback_query(filters.regex("toggle_joinchannels"))
async def toggle_joinchannels_callback(client: Client, callback_query: CallbackQuery):
    """
    Handles the callback query for toggling the join channels feature.
    """
    global JOIN_CHANNELS_ENABLED

    if callback_query.from_user.id != ADMIN_USER_ID:
        await callback_query.answer("ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀᴜᴛʜᴏʀɪᴢᴇᴅ ᴛᴏ ᴄʜᴀɴɢᴇ ꜱᴇᴛᴛɪɴɢꜱ.", show_alert=True)
        return

    # Toggle the feature
    JOIN_CHANNELS_ENABLED = not JOIN_CHANNELS_ENABLED

    # Update message
    text = (
        "⚙️ BOT SETTINGS\n\n"
        f"ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟꜱ: {'✅ ON' if JOIN_CHANNELS_ENABLED else '❌ OFF'}\n\n"
        "ʏᴏᴜ ᴄᴀɴ ᴇɴᴀʙʟᴇ ᴏʀ ᴅɪꜱᴀʙʟᴇᴅ:\n"
        "ᴛʜᴇ ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟꜱ ᴄᴏᴍᴍᴀɴᴅ ʜᴇʀᴇ`/joinchannelon` or `/joinchanneloff` 👈."
    )

    await callback_query.edit_message_text(text, reply_markup=build_settings_keyboard())

    await callback_query.answer(
        f"ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟꜱ ꜰᴇᴀᴛᴜʀᴇ ɪꜱ ɴᴏᴡ {'ENABLED ✅' if JOIN_CHANNELS_ENABLED else 'DISABLED ❌'}."
    )


# ==========================================================
print("✅ Bot Started!")
