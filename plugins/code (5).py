
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

# ============================
# Environment Variables
# =======================



# ============================
# /settings Command
# ============================
@Client.on_message(filters.command("settings") & filters.private)
async def settings_command(client: Client, message: Message):
    if message.from_user.id != ADMIN_USER_ID:
        await message.reply_text("⚙️ Only the admin can access settings.")
        return

    text = "⚙️ **Bot Settings**\n\nUse the buttons below to manage features."

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text=f"Join Channels: {'ON ✅' if JOIN_CHANNELS_ENABLED else 'OFF ❌'}",
                    callback_data="toggle_joinchannels",
                )
            ],
            [
                InlineKeyboardButton(text="View Join Channels", callback_data="view_joinchannels")
            ],
        ]
    )

    await message.reply_text(text, reply_markup=keyboard)


# ============================
# Callback Handler
# ============================
@Client.on_callback_query()
async def settings_callback(client: Client, query: CallbackQuery):
    global JOIN_CHANNELS_ENABLED

    data = query.data

    # Toggle Join Channels Feature
    if data == "toggle_joinchannels":
        if query.from_user.id != ADMIN_USER_ID:
            await query.answer("Only admin can toggle this!", show_alert=True)
            return

        JOIN_CHANNELS_ENABLED = not JOIN_CHANNELS_ENABLED
        status = "ON ✅" if JOIN_CHANNELS_ENABLED else "OFF ❌"
        await query.message.edit_text(
            f"⚙️ **Bot Settings**\n\nJoin Channels feature is now **{status}**.",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text=f"Join Channels: {status}",
                            callback_data="toggle_joinchannels",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="View Join Channels", callback_data="view_joinchannels"
                        )
                    ],
                ]
            ),
        )
        return

    # View Join Channels list
    if data == "view_joinchannels":
        await join_channels(client, query.message)
        await query.answer()


# ============================
# /joinchannels Command
# ============================
@Client.on_message(filters.command("joinchannels") & filters.private)
async def join_channels(client: Client, message: Message):
    user_id = message.from_user.id

    if not JOIN_CHANNELS_ENABLED:
        await message.reply_text("🚫 Join Channels feature is currently disabled.")
        return

    channels = [F_SUB1, F_SUB2, F_SUB3]
    response_lines = ["⚡️ **Checkout Our Channels** ⚡️\n"]
    keyboard_buttons = []

    for channel_id in channels:
        if not channel_id:
            continue

        try:
            member = await client.get_chat_member(channel_id, user_id)
            if member.status in [
                enums.ChatMemberStatus.MEMBER,
                enums.ChatMemberStatus.ADMINISTRATOR,
                enums.ChatMemberStatus.OWNER,
            ]:
                status = "✅"
            else:
                status = "❌"
        except UserNotParticipant:
            channel = await client.get_chat(channel_id)
            invite_link = await client.export_chat_invite_link(channel_id)
            keyboard_buttons.append([InlineKeyboardButton(text=channel.title, url=invite_link)])
            status = "❌"

        try:
            channel_title = (await client.get_chat(channel_id)).title
        except Exception:
            channel_title = f"Channel {channel_id}"

        response_lines.append(f"{channel_title} {status}")

    response_lines.append("\n📢 Join @sd_bots For More Updates")
    response = "\n".join(response_lines)

    if keyboard_buttons:
        await message.reply_text(response, reply_markup=InlineKeyboardMarkup(keyboard_buttons))
    else:
        await message.reply_text("✅ You’ve already joined all required channels!\n\n" + response)
