from pyrogram import Client, filters, enums
from pyrogram.types import *
from pyrogram.errors import *
import os
import asyncio

# --- Environment variables for channel IDs ---
F_SUB1 = int(os.environ.get('F_SUB1', '-1001593340575'))
F_SUB2 = int(os.environ.get('F_SUB2', '-1001917804203'))
F_SUB3 = int(os.environ.get('F_SUB3', '-1002109163181'))

# --- Admin user ID ---
ADMIN_USER_ID = int(os.environ.get("ADMIN_USER_ID", "5356695781"))

# --- Feature toggle variable ---
JOIN_CHANNELS_ENABLED = True

# --- Settings message deletion delay (in seconds) ---
SETTINGS_MESSAGE_DELAY = 30

# ==========================================================
#                     ADMIN TOGGLE COMMANDS (Removed direct commands)
# ==========================================================

# ==========================================================
#                  JOIN CHANNELS COMMAND
# ==========================================================
@Client.on_message(filters.command("joinchannels") & filters.private)
async def join_channels(client: Client, message: Message):
    global JOIN_CHANNELS_ENABLED

    if not JOIN_CHANNELS_ENABLED:
        await message.reply_text("⚙️ This feature is currently disabled by the admin.")
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
#                     SETTINGS MENU WITH TOGGLE
# ==========================================================
@Client.on_message(filters.command("settings") & filters.private)
async def settings_command(client: Client, message: Message):
    """
    Displays settings menu with inline toggle button (admin only)
    """
    if message.from_user.id != ADMIN_USER_ID:
        await message.reply_text("ᴏɴʟʏ ᴛʜᴇ ᴀᴅᴍɪɴ ᴄᴀɴ ᴀᴄᴄᴇꜱꜱ ꜱᴇᴛᴛɪɴɢꜱ.")
        return

    text = (
        "⚙️ ʙᴏᴛ ꜱᴇᴛᴛɪɴɢꜱ\n\n"
        f"ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟꜱ: {'✅ ON' if JOIN_CHANNELS_ENABLED else '❌ OFF'}\n\n"
        "ᴘʀᴇꜱꜱ ᴛʜᴇ ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ ᴛᴏ ᴛᴏɢɢʟᴇ ⬇️"
    )

    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(
                text=f"Toggle Join Channels: {'ON ✅' if JOIN_CHANNELS_ENABLED else 'OFF ❌'}",
                callback_data="toggle_joinchannels"
            )],
            [InlineKeyboardButton("Close ❌", callback_data="close_settings")]
        ]
    )

    sent_message = await message.reply_text(text, reply_markup=keyboard)

    asyncio.create_task(delete_message_after_delay(client, sent_message.chat.id, sent_message.id, SETTINGS_MESSAGE_DELAY))


async def delete_message_after_delay(client, chat_id, message_id, delay):
    await asyncio.sleep(delay)
    try:
        await client.delete_messages(chat_id, message_id)
    except Exception as e:
        print(f"Error deleting message: {e}")


# ==========================================================
#                  CALLBACK HANDLERS
# ==========================================================
@Client.on_callback_query(filters.regex("toggle_joinchannels"))
async def toggle_joinchannels_callback(client: Client, query: CallbackQuery):
    """
    Handles the toggle of the Join Channels feature.
    """
    global JOIN_CHANNELS_ENABLED

    if query.from_user.id != ADMIN_USER_ID:
        await query.answer("Only admin can toggle this.", show_alert=True)
        return

    # Toggle state
    JOIN_CHANNELS_ENABLED = not JOIN_CHANNELS_ENABLED

    # Update text and button
    new_text = (
        "⚙️ ʙᴏᴛ ꜱᴇᴛᴛɪɴɢꜱ\n\n"
        f"ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟꜱ: {'✅ ON' if JOIN_CHANNELS_ENABLED else '❌ OFF'}\n\n"
        "ᴘʀᴇꜱꜱ ᴛʜᴇ ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ ᴛᴏ ᴛᴏɢɢʟᴇ ⬇️"
    )

    new_keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(
                text=f"Toggle Join Channels: {'ON ✅' if JOIN_CHANNELS_ENABLED else 'OFF ❌'}",
                callback_data="toggle_joinchannels"
            )],
            [InlineKeyboardButton("Close ❌", callback_data="close_settings")]
        ]
    )

    await query.message.edit_text(new_text, reply_markup=new_keyboard)
    await query.answer(f"Join Channels feature {'enabled ✅' if JOIN_CHANNELS_ENABLED else 'disabled 🚫'}!")


@Client.on_callback_query(filters.regex("close_settings"))
async def close_settings_callback(client: Client, query: CallbackQuery):
    try:
        await query.message.delete()
    except:
        pass
    await query.answer("Closed settings menu.")


# ==========================================================
print("✅ Bot Started!")
