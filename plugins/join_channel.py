# bot.py
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Message
import os
import asyncio
from bot import Bot 

# -------------------------
# Configuration (use env vars)
# ----------------------
ADMIN_USER_ID = int(os.environ.get("ADMIN_USER_ID", "5356695781"))

F_SUB1 = int(os.environ.get('F_SUB1', '-1001593340575'))
F_SUB2 = int(os.environ.get('F_SUB2', '-1001917804203'))
F_SUB3 = int(os.environ.get('F_SUB3', '-1002109163181'))

# -------------------------
# State
# -------------------------
JOIN_CHANNELS_ENABLED = True
SETTINGS_MESSAGE_DELAY = 30

# -------------------------
# Client
# --------------------


async def delete_message_after_delay(client, chat_id, message_id, delay):
    await asyncio.sleep(delay)
    try:
        await client.delete_messages(chat_id, message_id)
        print(f"Auto-deleted settings message {message_id} in chat {chat_id}")
    except Exception as e:
        print("Auto-delete failed:", e)


# -------------------------
# /settings command
# -------------------------
@Client.on_message(filters.command("settings") & filters.private)
async def settings_command(client: Client, message: Message):
    global JOIN_CHANNELS_ENABLED
    print(f"/settings called by {message.from_user.id}")

    if message.from_user.id != ADMIN_USER_ID:
        await message.reply_text("Only the admin can access settings.")
        return

    text = (
        "⚙️  BOT SETTINGS\n\n"
        f"JOIN CHANNELS: {'✅ ON' if JOIN_CHANNELS_ENABLED else '❌ OFF'}\n\n"
        "Press the button below to toggle ⬇️"
    )
    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(text=f"Toggle Join Channels: {'ON ✅' if JOIN_CHANNELS_ENABLED else 'OFF ❌'}",
                                  callback_data="toggle_joinchannels")],
            [InlineKeyboardButton("Close ❌", callback_data="close_settings")]
        ]
    )

    sent = await message.reply_text(text, reply_markup=keyboard)
    print("Sent settings message id:", sent.id)
    # optional auto-delete
    asyncio.create_task(delete_message_after_delay(client, sent.chat.id, sent.id, SETTINGS_MESSAGE_DELAY))


# -------------------------
# Callback handler (catch-all)
# -------------------------
@Bot.on_callback_query()
async def callback_handler(client: Client, query: CallbackQuery):
    global JOIN_CHANNELS_ENABLED

    # DEBUG INFO: always log
    print("----- Callback received -----")
    print("data:", query.data)
    print("from:", query.from_user.id, query.from_user.first_name)
    print("message id:", getattr(query.message, "message_id", None))
    print("-----------------------------")

    # Always acknowledge the callback first (important)
    try:
        # If user is not admin, inform them and stop.
        if query.from_user.id != ADMIN_USER_ID:
            await query.answer("Only the admin can use this.", show_alert=True)
            print("Non-admin tried to use callback:", query.from_user.id)
            return
        else:
            # Acknowledge quickly so the client doesn't show a loading spinner indefinitely
            await query.answer()  # silent ack
    except Exception as e:
        print("query.answer() exception:", e)

    # Handle actions:
    if query.data == "toggle_joinchannels":
        # toggle the state
        JOIN_CHANNELS_ENABLED = not JOIN_CHANNELS_ENABLED
        print("Toggled JOIN_CHANNELS_ENABLED ->", JOIN_CHANNELS_ENABLED)

        new_text = (
            "⚙️  BOT SETTINGS\n\n"
            f"JOIN CHANNELS: {'✅ ON' if JOIN_CHANNELS_ENABLED else '❌ OFF'}\n\n"
            "Press the button below to toggle ⬇️"
        )
        new_kb = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton(text=f"Toggle Join Channels: {'ON ✅' if JOIN_CHANNELS_ENABLED else 'OFF ❌'}",
                                      callback_data="toggle_joinchannels")],
                [InlineKeyboardButton("Close ❌", callback_data="close_settings")]
            ]
        )

        try:
            await query.message.edit_text(new_text, reply_markup=new_kb)
            print("Edited settings message to reflect new state.")
        except Exception as e:
            print("Failed to edit settings message:", e)

        # Inform the admin (also optional show_alert)
        try:
            await query.answer(f"Join Channels {'enabled ✅' if JOIN_CHANNELS_ENABLED else 'disabled 🚫'}")
        except Exception as e:
            print("Second query.answer() failed:", e)

    elif query.data == "close_settings":
        try:
            await query.message.delete()
            print("Settings message deleted by admin.")
        except Exception as e:
            print("Failed to delete settings message:", e)
        try:
            await query.answer("Closed settings menu.")
        except:
            pass
    else:
        # Unknown callback data
        print("Unknown callback_data:", query.data)
        try:
            await query.answer("Unknown action.", show_alert=True)
        except:
            pass


# -------------------------
# /joinchannels command (uses the toggle)
# -------------------------
@Clients.on_message(filters.command("joinchannels") & filters.private)
async def join_channels(client: Client, message: Message):
    global JOIN_CHANNELS_ENABLED

    print(f"/joinchannels called by {message.from_user.id}. JOIN_CHANNELS_ENABLED={JOIN_CHANNELS_ENABLED}")

    if not JOIN_CHANNELS_ENABLED:
        await message.reply_text("⚙️ This feature is currently disabled by the admin.")
        return

    user_id = message.from_user.id
    member_statuses = {}
    keyboard_buttons = []

    for channel_id in [F_SUB1, F_SUB2, F_SUB3]:
        try:
            member = await client.get_chat_member(channel_id, user_id)
            if member.status in [enums.ChatMemberStatus.MEMBER, enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER]:
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

    response = "⚡️ CHECK OUT OUR CHANNELS ⚡️\n\n"
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


# -------------------------
# Run bot
# -------------------------
