
from pyrogram import Client, filters, enums
from pyrogram.types import *
from pyrogram.errors import *
import os
import logging  # Import the logging module

# Configure logging
logging.basicConfig(
    format='[%(asctime)s - %(levelname)s] - %(name)s - %(message)s',
    level=logging.INFO  # Adjust level as needed (DEBUG, INFO, WARNING, ERROR)
)

logger = logging.getLogger(__name__)

F_SUB1 = os.environ.get('F_SUB1', '-2109163181')  # Read as strings first
F_SUB2 = os.environ.get('F_SUB2', '-1917804203')
F_SUB3 = os.environ.get('F_SUB3', '-1593340575')

ADMIN_USER_IDS = list(map(int, os.environ.get("ADMINS", "5356695781").split(",")))

# Store the state of the command (on/off)
COMMAND_ENABLED = True

def admin_filter(func):
    async def wrapper(client: Client, update):
        user_id = update.from_user.id
        if user_id in ADMIN_USER_IDS:
            return await func(client, update)
        else:
            await update.answer("You are not authorized to perform this action.", show_alert=True)
            return
    return wrapper


@Client.on_message(filters.command("joinchannels") & filters.private)
async def join_channels(client: Client, message: Message):
    global COMMAND_ENABLED

    if not COMMAND_ENABLED:
        await message.reply_text("This command is currently disabled.")
        return

    user_id = message.from_user.id

    member_statuses = {}
    keyboard_buttons = []

    channel_ids = [F_SUB1, F_SUB2, F_SUB3]

    for channel_id_str in channel_ids:
        if not channel_id_str:  # Skip empty channel IDs
            continue

        try:
            channel_id = int(channel_id_str) # Convert to integer inside the loop

            try:
                member = await client.get_chat_member(channel_id, user_id)
                if member.status in [enums.ChatMemberStatus.MEMBER, enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER]:
                    member_statuses[channel_id] = "✅"
            except UserNotParticipant:
                # Get the invite link for the channel
                try:
                    invite_link = await client.export_chat_invite_link(channel_id)
                except Exception as e:
                    logger.error(f"Error getting invite link for {channel_id}: {e}")
                    invite_link = None

                if invite_link:
                    try:
                        channel = await client.get_chat(channel_id)
                        channel_title = channel.title
                        keyboard_button = InlineKeyboardButton(
                            text=f"{channel_title}",
                            url=invite_link
                        )
                        keyboard_buttons.append(keyboard_button)
                        member_statuses[channel_id] = "❌"
                    except Exception as e:
                         logger.error(f"Error getting channel title for {channel_id}: {e}")
                         member_statuses[channel_id] = "⚠️ Error getting channel info"
                else:
                    member_statuses[channel_id] = "⚠️ Invite link unavailable"

            except Exception as e:  # Catch-all for other errors during get_chat_member
                logger.error(f"Error getting member status for {channel_id}: {e}")
                member_statuses[channel_id] = f"⚠️ Error: {e}"

        except ValueError:
            logger.warning(f"Invalid channel ID format: {channel_id_str}.  Must be an integer.")
            continue # skip to the next ID

    response = "⚡️ 𝗖𝗵𝗲𝗰𝗸𝗼𝘂𝘁 𝗢𝘂𝗿 𝗖𝗵𝗮𝗻𝗻𝗲𝗹𝘀 ⚡️\n\n"
    for channel_id_str in channel_ids:  # Iterate over strings again for consistent key access
        if not channel_id_str:
            continue

        try:
            channel_id = int(channel_id_str) # Convert to int inside the loop
            try:
                channel_title = (await client.get_chat(channel_id)).title
                response += f"{channel_title} {member_statuses[channel_id]}\n"
            except KeyError:
                logger.warning(f"No member status found for channel {channel_id}.  Possibly skipped due to previous error.")
                response += f"Channel ID: {channel_id} - Status unavailable (check logs)\n" # helpful debug
            except Exception as e:
                logger.error(f"Error getting channel title for {channel_id}: {e}")
                response += f"Channel ID: {channel_id} - Error: {e}\n"


        except ValueError:
            # Should not happen again, but handle it just in case
            logger.warning(f"Invalid channel ID format (again): {channel_id_str}")
            continue # skip to next id

    response += """
𝖩𝗈𝗂𝗇 @sd_bots 𝖥𝗈𝗋 𝖬𝗈𝗋𝖾"""

    reply_markup = None
    if keyboard_buttons:
        keyboard = InlineKeyboardMarkup(
            [[button] for button in keyboard_buttons]
        )
        reply_markup = keyboard

    # Add on/off buttons -  Only show admins the on/off buttons
    if message.from_user.id in ADMIN_USER_IDS:
        on_off_keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("Turn OFF", callback_data="turn_off_command"),
                InlineKeyboardButton("Turn ON", callback_data="turn_on_command"),
            ]
        ])

        if reply_markup:
            # If there are channel join buttons, add the on/off buttons below them
            if isinstance(reply_markup, InlineKeyboardMarkup):
                reply_markup.inline_keyboard.extend(on_off_keyboard.inline_keyboard)
            else:
                reply_markup = on_off_keyboard # if there's any error just send on/off buttons
        else:
            reply_markup = on_off_keyboard  # Only on/off buttons

    await message.reply_text(response, reply_markup=reply_markup)


@Client.on_callback_query(filters.regex("turn_on_command"))
@admin_filter
async def turn_on(client: Client, callback_query: CallbackQuery):
    global COMMAND_ENABLED
    COMMAND_ENABLED = True
    await callback_query.answer("Join Channels command is now ON.")
    await callback_query.message.edit_reply_markup(None) #remove inline keyboard

@Client.on_callback_query(filters.regex("turn_off_command"))
@admin_filter
async def turn_off(client: Client, callback_query: CallbackQuery):
    global COMMAND_ENABLED
    COMMAND_ENABLED = False
    await callback_query.answer("Join Channels command is now OFF.")
    await callback_query.message.edit_reply_markup(None) #remove inline keyboard
