
from pyrogram import Client, filters, enums
from pyrogram.types import *
from pyrogram.errors import *
import os
import asyncio  # Import the asyncio library

# --- Environment variables for channel IDs ---
F_SUB1 = int(os.environ.get('F_SUB1', '-1001593340575'))
F_SUB2 = int(os.environ.get('F_SUB2', '-1001917804203'))
F_SUB3 = int(os.environ.get('F_SUB3', '-1002109163181'))

# --- Admin user ID (replace with the actual admin user ID) ---
ADMIN_USER_ID = int(os.environ.get("ADMIN_USER_ID", "5356695781"))

# --- Variable to control the join channels feature ---
JOIN_CHANNELS_ENABLED = True  # Default ON

# --- Settings message deletion delay (in seconds) ---
SETTINGS_MESSAGE_DELAY = 30  # Example: 30 seconds

# ===============================
# /joinchannelon command
# ===============================
@Client.on_message(filters.command("joinchannelon") & filters.private)
async def join_channel_on(client: Client, message):
    global JOIN_CHANNELS_ENABLED

    if message.from_user.id != ADMIN_USER_ID:
        await message.reply_text("⚠️ ᴏɴʟʏ ᴛʜᴇ ᴀᴅᴍɪɴ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ.")
        return

    JOIN_CHANNELS_ENABLED = True
    await message.reply_text("✅ ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ ꜰᴇᴀᴛᴜʀᴇ ɪꜱ ɴᴏᴡ ᴇɴᴀʙʟᴇᴅ.")


# ===============================
# /joinchanneloff command
# ===============================
@Client.on_message(filters.command("joinchanneloff") & filters.private)
async def join_channel_off(client: Client, message):
    global JOIN_CHANNELS_ENABLED

    if message.from_user.id != ADMIN_USER_ID:
        await message.reply_text("⚠️ ᴏɴʟʏ ᴛʜᴇ ᴀᴅᴍɪɴ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ.")
        return

    JOIN_CHANNELS_ENABLED = False
    await message.reply_text("❌ ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ ꜰᴇᴀᴛᴜʀᴇ ʜᴀꜱ ʙᴇᴇɴ ᴅɪꜱᴀʙʟᴇᴅ.")


# ===============================
# /settings command
# ===============================
@Client.on_message(filters.command("settings") & filters.private)
async def settings_command(client: Client, message):
    """
    Admin settings panel showing join channel control buttons.
    """
    if message.from_user.id != ADMIN_USER_ID:
        await message.reply_text("⚠️ ᴏɴʟʏ ᴛʜᴇ ᴀᴅᴍɪɴ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ.")
        return

    status = "✅ ON" if JOIN_CHANNELS_ENABLED else "❌ OFF"

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("✅ Enable Join Channels", callback_data="joinchannelon_btn"),
                InlineKeyboardButton("❌ Disable Join Channels", callback_data="joinchanneloff_btn"),
            ]
        ]
    )

    await message.reply_text(
        text=f"⚙️ **Bot Settings Panel**\n\n📡 Join Channels: **{status}**",
        reply_markup=keyboard
    )


# ===============================
# Callback Query Handler
# ===============================
@Client.on_callback_query()
async def callback_handler(client: Client, query: CallbackQuery):
    global JOIN_CHANNELS_ENABLED

    data = query.data

    if query.from_user.id != ADMIN_USER_ID:
        await query.answer("⚠️ Admin only!", show_alert=True)
        return

    if data == "joinchannelon_btn":
        JOIN_CHANNELS_ENABLED = True
        await query.message.edit_text(
            "✅ ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ ꜰᴇᴀᴛᴜʀᴇ ɪꜱ ɴᴏᴡ ᴇɴᴀʙʟᴇᴅ."
        )

    elif data == "joinchanneloff_btn":
        JOIN_CHANNELS_ENABLED = False
        await query.message.edit_text(
            "❌ ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ ꜰᴇᴀᴛᴜʀᴇ ʜᴀꜱ ʙᴇᴇɴ ᴅɪꜱᴀʙʟᴇᴅ."
        )

# ==========================================================
#                  ADMIN ON / OFF COMMANDS
# ==========================================================


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
