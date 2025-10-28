from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Message
import os
import asyncio

# ==========================================================
#                     BOT CONFIGURATION
# ==========================================================

API_ID = int(os.environ.get("API_ID", "123456"))  # replace if needed
API_HASH = os.environ.get("API_HASH", "your_api_hash_here")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "your_bot_token_here")

# --- Channels ---
F_SUB1 = int(os.environ.get('F_SUB1', '-1001593340575'))
F_SUB2 = int(os.environ.get('F_SUB2', '-1001917804203'))
F_SUB3 = int(os.environ.get('F_SUB3', '-1002109163181'))

# --- Admin ID ---
ADMIN_USER_ID = int(os.environ.get("ADMIN_USER_ID", "5356695781"))

# --- Bot Settings ---
JOIN_CHANNELS_ENABLED = True   # Default: ON
SETTINGS_MESSAGE_DELAY = 30    # Auto-delete after 30s

# ==========================================================
#                     START BOT CLIENT
# ==========================================================
app = Client("TitanStoreBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)


# ==========================================================
#                     AUTO DELETE MESSAGE
# ==========================================================
async def delete_message_after_delay(client, chat_id, message_id, delay):
    await asyncio.sleep(delay)
    try:
        await client.delete_messages(chat_id, message_id)
    except Exception as e:
        print("Delete message error:", e)


# ==========================================================
#                     SETTINGS COMMAND
# ==========================================================
@app.on_message(filters.command("settings") & filters.private)
async def settings_command(client: Client, message: Message):
    global JOIN_CHANNELS_ENABLED

    if message.from_user.id != ADMIN_USER_ID:
        await message.reply_text("Only the admin can access settings.")
        return

    text = (
        "⚙️ **BOT SETTINGS**\n\n"
        f"Join Channels: {'✅ ON' if JOIN_CHANNELS_ENABLED else '❌ OFF'}\n\n"
        "Press the button below to toggle ⬇️"
    )

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text=f"Toggle Join Channels: {'ON ✅' if JOIN_CHANNELS_ENABLED else 'OFF ❌'}",
                    callback_data="toggle_joinchannels"
                )
            ],
            [InlineKeyboardButton("Close ❌", callback_data="close_settings")]
        ]
    )

    sent = await message.reply_text(text, reply_markup=keyboard)

    # Schedule auto-deletion after 30 seconds
    asyncio.create_task(delete_message_after_delay(client, sent.chat.id, sent.id, SETTINGS_MESSAGE_DELAY))


# ==========================================================
#                     CALLBACK HANDLER
# ==========================================================
@app.on_callback_query()
async def callback_handler(client: Client, query: CallbackQuery):
    global JOIN_CHANNELS_ENABLED

    print(f"Callback received: {query.data} from {query.from_user.id}")

    if query.data == "toggle_joinchannels":
        if query.from_user.id != ADMIN_USER_ID:
            await query.answer("Only the admin can toggle this.", show_alert=True)
            return

        # Toggle ON/OFF
        JOIN_CHANNELS_ENABLED = not JOIN_CHANNELS_ENABLED

        new_text = (
            "⚙️ **BOT SETTINGS**\n\n"
            f"Join Channels: {'✅ ON' if JOIN_CHANNELS_ENABLED else '❌ OFF'}\n\n"
            "Press the button below to toggle ⬇️"
        )

        new_keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text=f"Toggle Join Channels: {'ON ✅' if JOIN_CHANNELS_ENABLED else 'OFF ❌'}",
                        callback_data="toggle_joinchannels"
                    )
                ],
                [InlineKeyboardButton("Close ❌", callback_data="close_settings")]
            ]
        )

        try:
            await query.message.edit_text(new_text, reply_markup=new_keyboard)
        except Exception as e:
            print("Edit error:", e)

        await query.answer(f"Join Channels feature {'enabled ✅' if JOIN_CHANNELS_ENABLED else 'disabled 🚫'}!")

    elif query.data == "close_settings":
        try:
            await query.message.delete()
        except Exception as e:
            print("Close error:", e)
        await query.answer("Closed settings menu.")


# ==========================================================
#                     JOIN CHANNELS COMMAND
# ==========================================================
@app.on_message(filters.command("joinchannels") & filters.private)
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
        except Exception:
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


# ==========================================================
#                     BOT START
# ==========================================================
