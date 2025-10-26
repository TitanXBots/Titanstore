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
        await message.reply_text("ᴏɴʟʏ ᴛʜᴇ ᴀᴅᴍɪɴ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ.")
        return

    JOIN_CHANNELS_ENABLED = True
    await message.reply_text("ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ ꜰᴇᴀᴛᴜʀᴇ ɪꜱ ɴᴏᴡ ᴇɴᴀʙʟᴇᴅ ✅.")


@Client.on_message(filters.command("joinchanneloff") & filters.private)
async def join_channel_off(client: Client, message: Message):
    """
    Disables the join channels feature (admin only).
    """
    global JOIN_CHANNELS_ENABLED

    if message.from_user.id != ADMIN_USER_ID:
        await message.reply_text("ᴏɴʟʏ ᴛʜᴇ ᴀᴅᴍɪɴ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ.")
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

    response = "⚡️ 𝐂𝐇𝐄𝐂𝐊 𝐎𝐔𝐓 𝐎𝐔𝐑 𝐂𝐇𝐀𝐍𝐍𝐄𝐋𝐒 ⚡️\n\n"
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
    Builds the settings keyboard with the Join Channels toggle button and a close button.
    """
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text=f"Join Channels: {'ON ✅' if JOIN_CHANNELS_ENABLED else 'OFF ❌'}",
                    callback_data="toggle_joinchannels"
                )
            ],
            [
                InlineKeyboardButton(
                    text="Close ❌",
                    callback_data="close_settings"
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
        await message.reply_text("⚠️ Only the admin can access settings.")
        return

    text = (
        "⚙️ Bot Settings\n\n"
        f"Join Channels: {'✅ ON' if JOIN_CHANNELS_ENABLED else '❌ OFF'}\n\n"
        "Use /joinchannelon or /joinchanneloff to toggle manually.\n"
        "Or press the buttons below 👇"
    )

    await message.reply_text(
        text,
        reply_markup=build_settings_keyboard(),
        disable_web_page_preview=True
    )


@Client.on_callback_query(filters.regex(r"^close_settings$"))
async def close_settings(client: Client, callback_query: CallbackQuery):
    """
    Handles the 'Close' button.
    """
    await callback_query.answer("Closing settings...", show_alert=False)

    try:
        # Try deleting the message
        await callback_query.message.delete()
    except Exception as e:
        # If it can't delete (e.g. older than 48 hours), fallback to editing
        try:
            await callback_query.message.edit_text("✅ Settings closed.", reply_markup=None) # Added reply_markup=None
        except Exception as e:
            print(f"Close button error: {e}")
            pass


@Client.on_callback_query(filters.regex(r"^toggle_joinchannels$"))
async def toggle_joinchannels(client: Client, callback_query: CallbackQuery):
    """
    Toggles the Join Channels setting.
    """
    global JOIN_CHANNELS_ENABLED
    JOIN_CHANNELS_ENABLED = not JOIN_CHANNELS_ENABLED

    await callback_query.answer(
        f"Join Channels is now {'ON ✅' if JOIN_CHANNELS_ENABLED else 'OFF ❌'}",
        show_alert=False
    )

    # Update keyboard state dynamically
    try:
        await callback_query.message.edit_reply_markup(
            reply_markup=build_settings_keyboard()
        )
    except Exception as e:
        print(f"Toggle button error: {e}")
        pass

# ==========================================================
print("✅ Bot Started!")
