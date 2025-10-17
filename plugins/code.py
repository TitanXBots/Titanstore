from pyrogram import Client, filters, enums
from pyrogram.types import *
from pyrogram.errors import *
import os

F_SUB1 = int(os.environ.get('F_SUB1', '-1001593340575'))
F_SUB2 = int(os.environ.get('F_SUB2', '-1001917804203'))
F_SUB3 = int(os.environ.get('F_SUB3', '-1002109163181'))

JOIN_CHANNELS_ENABLED = True  # Global flag to control channel joining

ADMIN_ID = int(os.environ.get("ADMIN_ID", "5356695781")) #Get admin id or default to 0

@Client.on_message(filters.command("settings") & filters.private)
async def settings(client: Client, message: Message):
    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Join Channels", callback_data="joinchannels")],
        ]
    )
    await message.reply_text("Click the button to check channels!", reply_markup=keyboard)

@Client.on_callback_query(filters.regex("joinchannels"))
async def join_channels_callback(client: Client, callback_query: CallbackQuery):
    await join_channels(client, callback_query.message)
    await callback_query.answer()

@Client.on_message(filters.command("joinchannels") & filters.private)
async def join_channels(client: Client, message: Message):
    global JOIN_CHANNELS_ENABLED
    if not JOIN_CHANNELS_ENABLED:
        await message.reply_text("Channel joining is currently disabled.")
        return

    user_id = message.from_user.id

    member_statuses = {}
    keyboard_buttons = []

    for channel_id in [F_SUB1, F_SUB2, F_SUB3]:
        try:
            member = await client.get_chat_member(channel_id, user_id)
            if member.status in [enums.ChatMemberStatus.MEMBER, enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER]:
                member_statuses[channel_id] = "✅"
        except UserNotParticipant:
            try:
                # Get the invite link for the channel
                invite_link = await client.export_chat_invite_link(channel_id)

                channel = await client.get_chat(channel_id)
                channel_title = channel.title

                keyboard_button = InlineKeyboardButton(
                    text=f"{channel_title}",
                    url=invite_link
                )
                keyboard_buttons.append(keyboard_button)
                member_statuses[channel_id] = "❌"
            except Exception as e:
                print(f"Error getting invite link for {channel_id}: {e}")
                member_statuses[channel_id] = "⚠️ Error" #Indicate an error

    response = "⚡️ 𝗖𝗵𝗲𝗰𝗸𝗼𝘂𝘁 𝗢𝘂𝗿 𝗖𝗵𝗮𝗻𝗻𝗲𝗹𝘀 ⚡️\n\n"
    for channel_id in [F_SUB1, F_SUB2, F_SUB3]:
        try:
            channel_title = (await client.get_chat(channel_id)).title
            response += f"{channel_title} {member_statuses[channel_id]}\n"
        except Exception as e:
            print(f"Error getting channel title for {channel_id}: {e}")
            response += f"Channel {channel_id} - Error\n"

    response += """
 𝖩𝗈𝗂𝗇 @sd_bots 𝖥𝗈𝗋 𝖬𝗈𝗋𝖾"""

    if keyboard_buttons:
        keyboard = InlineKeyboardMarkup(
            [[button] for button in keyboard_buttons]
        )
        await message.reply_text(response, reply_markup=keyboard)
    else:

        await message.reply_text(response)

@Client.on_message(filters.command("admin") & filters.private & filters.user(ADMIN_ID))
async def admin_panel(client: Client, message: Message):
    reply_markup = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("✅ Join On", callback_data="joinchannelon"),
                InlineKeyboardButton("❌ Join Off", callback_data="joinchanneloff")
            ],
        ]
    )
    await message.reply_text("Admin Panel:", reply_markup=reply_markup)

@Client.on_callback_query(filters.regex("joinchannelon"))
async def joinchannelon_callback(client: Client, callback_query: CallbackQuery):
    global JOIN_CHANNELS_ENABLED
    JOIN_CHANNELS_ENABLED = True
    await callback_query.answer("Channel joining enabled.")
    await callback_query.message.edit_reply_markup(None) #remove inline keyboard

@Client.on_callback_query(filters.regex("joinchanneloff"))
async def joinchanneloff_callback(client: Client, callback_query: CallbackQuery):
    global JOIN_CHANNEL_DISABLED
    JOIN_CHANNEL_DISABLED = True
    await callback_query.answer("channel joining disabled.")
    await callback_query.message.edit_reply_markup(None)
