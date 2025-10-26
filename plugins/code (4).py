from pyrogram import Client, filters, enums
from pyrogram.types import *
from pyrogram.errors import *
import os
from pyrogram.handlers import CallbackQueryHandler

# --- Environment variables for channel IDs ---
F_SUB1 = int(os.environ.get('F_SUB1', '-1001593340575'))
F_SUB2 = int(os.environ.get('F_SUB2', '-1001917804203'))
F_SUB3 = int(os.environ.get('F_SUB3', '-1002109163181'))

# --- Admin user ID (replace with the actual admin user ID) ---
ADMIN_IDS = int(os.environ.get("ADMIN_IDS", "5356695781"))

# --- Variable to control the join channels feature ---
JOIN_CHANNELS_ENABLED = True  # Default ON

# ==========================================================
#                  ADMIN ON / OFF COMMANDS
# ==========================================================
@Client.on_message(filters.command("settings") & filters.private)
async def settings(client: Client, message: Message):
    user_id = message.from_user.id
    if user_id not in ADMIN_IDS:
        await message.reply_text("You are not authorized to use this command.")
        return

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Join Channels ON", callback_data="joinchannel_on"),
                InlineKeyboardButton("Join Channels OFF", callback_data="joinchannel_off"),
            ],
            [InlineKeyboardButton("Close", callback_data="close_data")],
        ]
    )
    await message.reply_text("Settings Panel:", reply_markup=keyboard)


@Client.on_callback_query(filters.regex("joinchannel_on"))
async def joinchannel_on(client: Client, query: CallbackQuery):
    global JOIN_CHANNELS_ENABLED
    JOIN_CHANNELS_ENABLED = True
    await query.answer("Join Channels requirement is now ON.")
    await query.message.edit_reply_markup(None)

@Client.on_callback_query(filters.regex("joinchannel_off"))
async def joinchannel_off(client: Client, query: CallbackQuery):
    global JOIN_CHANNELS_ENABLED
    JOIN_CHANNELS_ENABLED = False
    await query.answer("Join Channels requirement is now OFF.")
    await query.message.edit_reply_markup(None)


@Client.on_callback_query(filters.regex("close_data"))
async def close_data(client: Client, query: CallbackQuery):
    await query.message.delete()


@Client.on_message(filters.command("joinchannels") & filters.private)
async def join_channels(client: Client, message: Message):
    global JOIN_CHANNELS_ENABLED
    user_id = message.from_user.id

    if JOIN_CHANNELS_ENABLED:
      member_statuses = {}
      keyboard_buttons = []

      for channel_id in [F_SUB1, F_SUB2, F_SUB3]:
          try:
              member = await client.get_chat_member(channel_id, user_id)
              if member.status == enums.ChatMemberStatus.MEMBER or member.status == enums.ChatMemberStatus.ADMINISTRATOR or member.status == enums.ChatMemberStatus.OWNER:
                  member_statuses[channel_id] = "✅"
              else:
                  # User is not a member, continue to the next block
                  raise UserNotParticipant

          except UserNotParticipant:
              # Get the invite link for the channel
              try:
                  invite_link = await client.export_chat_invite_link(channel_id)
              except Exception as e:
                  print(f"Failed to get invite link for channel {channel_id}: {e}")
                  invite_link = None

              if invite_link:
                  try:
                      channel = await client.get_chat(channel_id)
                      channel_title = channel.title
                  except Exception as e:
                      print(f"Failed to get channel title for {channel_id}: {e}")
                      channel_title = "Unknown Channel"

                  keyboard_button = InlineKeyboardButton(
                      text=f"{channel_title}",
                      url=invite_link
                  )
                  keyboard_buttons.append(keyboard_button)
                  member_statuses[channel_id] = "❌"
              else:
                  member_statuses[channel_id] = "❌ (Error getting link)"


      response = "⚡️ Mandatory Channels ⚡️\n\n"
      for channel_id in [F_SUB1, F_SUB2, F_SUB3]:
          try:
              channel_title = (await client.get_chat(channel_id)).title
          except Exception as e:
              print(f"Failed to get channel title for {channel_id}: {e}")
              channel_title = "Unknown Channel"

          response += f"{channel_title} {member_statuses[channel_id]}\n"

      response += """
 Check @sd_bots For More"""

      if keyboard_buttons:
          keyboard = InlineKeyboardMarkup(
              [[button] for button in keyboard_buttons]
          )
          await message.reply_text(response, reply_markup=keyboard)
      else:

          await message.reply_text(response)

    else:
        await message.reply_text("Join channel requirement is currently turned off.")



# ==========================================================
print("✅ Bot Started!")
