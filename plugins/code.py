from pyrogram import Client, filters, enums
from pyrogram.types import *
from pyrogram.errors import *
import os

# --- Environment Variables ---
F_SUB1 = int(os.environ.get('F_SUB1', '-1001593340575'))
F_SUB2 = int(os.environ.get('F_SUB2', '-1001917804203'))
F_SUB3 = int(os.environ.get('F_SUB3', '-1002109163181'))

# Admin user ID
ADMIN_USER_ID = int(os.environ.get("ADMIN_USER_ID", "5356695781"))

# Variable to control the join channels feature
JOIN_CHANNELS_ENABLED = True  # Default: enabled

# --- Settings Menu ---

def build_settings_keyboard():
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "Join Channels: ON" if JOIN_CHANNELS_ENABLED else "Join Channels: OFF",
                    callback_data="toggle_joinchannels"
                )
            ]
        ]
    )
    return keyboard


@Client.on_message(filters.command("settings") & filters.private)
async def settings_command(client: Client, message: Message):
    """
    Displays a settings menu (admin only) using an inline keyboard.
    """
    user_id = message.from_user.id

    if user_id != ADMIN_USER_ID:
        await message.reply_text("Only the admin can access settings.")
        return

    await message.reply_text("⚙️ **Bot Settings:**", reply_markup=build_settings_keyboard())


@Client.on_callback_query(filters.regex("toggle_joinchannels"))
async def toggle_joinchannels_callback(client: Client, callback_query: CallbackQuery):
    """
    Handles toggling the join channels feature via inline button.
    """
    global JOIN_CHANNELS_ENABLED
    user_id = callback_query.from_user.id

    if user_id != ADMIN_USER_ID:
        await callback_query.answer("You are not authorized to change settings.", show_alert=True)
        return

    JOIN_CHANNELS_ENABLED = not JOIN_CHANNELS_ENABLED
    await callback_query.edit_message_text("⚙️ **Bot Settings:**", reply_markup=build_settings_keyboard())
    await callback_query.answer(
        f"Join channels feature is now {'ENABLED ✅' if JOIN_CHANNELS_ENABLED else 'DISABLED ❌'}."
    )

# --- Admin Commands (/joinchannelon, /joinchanneloff) ---

@Client.on_message(filters.command("joinchannelon") & filters.private)
async def join_channel_on(client: Client, message: Message):
    """
    Enables the join channels feature (admin only).
    """
    global JOIN_CHANNELS_ENABLED
    user_id = message.from_user.id

    if user_id != ADMIN_USER_ID:
        await message.reply_text("Only the admin can use this command.")
        return

    JOIN_CHANNELS_ENABLED = True
    await message.reply_text("✅ Join channels feature is now **ENABLED**.")


@Client.on_message(filters.command("joinchanneloff") & filters.private)
async def join_channel_off(client: Client, message: Message):
    """
    Disables the join channels feature (admin only).
    """
    global JOIN_CHANNELS_ENABLED
    user_id = message.from_user.id

    if user_id != ADMIN_USER_ID:
        await message.reply_text("Only the admin can use this command.")
        return

    JOIN_CHANNELS_ENABLED = False
    await message.reply_text("🚫 Join channels feature is now **DISABLED**.")

# --- Main Join Channel Command ---

@Client.on_message(filters.command("joinchannels") & filters.private)
async def join_channels(client: Client, message: Message):
    """
    Checks user's membership in specified channels and prompts to join if not a member.
    """
    global JOIN_CHANNELS_ENABLED

    if not JOIN_CHANNELS_ENABLED:
        await message.reply_text("This feature is currently disabled by the admin.")
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
                print(f"Error with channel {channel_id}: {e}")
                member_statuses[channel_id] = "⚠️ Error"

    response = "⚡️ **Checkout Our Channels** ⚡️\n\n"
    for channel_id in [F_SUB1, F_SUB2, F_SUB3]:
        try:
            title = (await client.get_chat(channel_id)).title
        except:
            title = f"Channel ID: {channel_id}"
        response += f"{title} {member_statuses.get(channel_id, '❓')}\n"

    response += "\nJoin @TitanXBots for more updates 💥"

    if keyboard_buttons:
        keyboard = InlineKeyboardMarkup([[btn] for btn in keyboard_buttons])
        await message.reply_text(response, reply_markup=keyboard)
    else:
        await message.reply_text(response)

print("✅ Bot Started Successfully!")
