import base64
import re
import asyncio
import logging
from pyrogram.errors import MessageNotModified, UserNotParticipant, FloodWait
from pyrogram.enums import ChatMemberStatus

# --------------------------------------------------
# 1. BULLETPROOF UI EDITING
# --------------------------------------------------
async def safe_edit(message, text, reply_markup=None):
    """Safely edits a message, automatically detecting if it's text or media."""
    try:
        if message.media:
            return await message.edit_caption(
                caption=text, 
                reply_markup=reply_markup
            )
        else:
            return await message.edit_text(
                text=text, 
                reply_markup=reply_markup
            )
    except MessageNotModified:
        # Ignore if the user clicks the same button twice
        pass
    except Exception as e:
        logging.error(f"Safe Edit Error: {e}")


async def send_cancel_msg(client, chat_id):
    """Sends a generic cancellation message."""
    try:
        await client.send_message(chat_id, "❌ **ᴘʀᴏᴄᴇꜱꜱ ᴄᴀɴᴄᴇʟʟᴇᴅ!**")
    except Exception:
        pass


# --------------------------------------------------
# 2. FORCE SUBSCRIPTION CHECKER
# --------------------------------------------------
async def subscribed(client, message_or_query, channels: list) -> bool:
    """Checks if a user is subscribed to all required Force Sub channels."""
    user_id = message_or_query.from_user.id
    for channel in channels:
        if not channel or str(channel) in ["0", "-100"]:
            continue
        try:
            member = await client.get_chat_member(chat_id=channel, user_id=user_id)
            # If user is banned/kicked, treat as not subscribed
            if member.status in [ChatMemberStatus.BANNED, ChatMemberStatus.RESTRICTED]:
                return False
        except UserNotParticipant:
            return False
        except FloodWait as e:
            await asyncio.sleep(e.value)
            return await subscribed(client, message_or_query, channels)
        except Exception as e:
            logging.error(f"FS Check Error on channel {channel}: {e}")
            # If bot isn't admin in the FS channel, it might throw an error. 
            # We pass to prevent the bot from breaking completely.
            pass
    return True


# --------------------------------------------------
# 3. ENCODING & DECODING FOR SHAREABLE LINKS
# --------------------------------------------------
async def encode(string: str) -> str:
    """Encodes string to Base64 for secure start links."""
    string_bytes = string.encode("ascii")
    base64_bytes = base64.urlsafe_b64encode(string_bytes)
    base64_string = base64_bytes.decode("ascii").strip("=")
    return base64_string

async def decode(base64_string: str) -> str:
    """Decodes Base64 string back to message/batch data."""
    # Add padding back if necessary
    base64_string = base64_string.strip("-")
    padding = len(base64_string) % 4
    if padding != 0:
        base64_string += "=" * (4 - padding)
        
    base64_bytes = base64_string.encode("ascii")
    string_bytes = base64.urlsafe_b64decode(base64_bytes)
    return string_bytes.decode("ascii")


# --------------------------------------------------
# 4. DATABASE MESSAGE RETRIEVAL
# --------------------------------------------------
async def get_messages(client, message_ids, chat_id):
    """Fetches a list of messages from the Database Channel."""
    try:
        # Pyrogram can fetch a list of IDs directly
        messages = await client.get_messages(chat_id=chat_id, message_ids=list(message_ids))
        # Ensure it returns a list even if it's a single message
        if not isinstance(messages, list):
            messages = [messages]
        return messages
    except FloodWait as e:
        await asyncio.sleep(e.value)
        return await get_messages(client, message_ids, chat_id)
    except Exception as e:
        logging.error(f"Error fetching messages from DB: {e}")
        return []


async def get_message_id(client, message, chat_id: int) -> int:
    """Extracts the specific message ID from a forwarded message or a direct link."""
    # If the user forwarded a message from the DB channel
    if message.forward_from_chat:
        if message.forward_from_chat.id == chat_id:
            return message.forward_from_message_id
            
    # If the user sent a telegram link to the message
    elif message.text:
        pattern = r"https://t.me/(?:c/)?(.*)/(\d+)"
        match = re.search(pattern, message.text)
        if match:
            return int(match.group(2))
            
    return 0


# --------------------------------------------------
# 5. TIME FORMATTING
# --------------------------------------------------
def get_readable_time(seconds: int) -> str:
    """Converts raw seconds into a readable format (e.g., 1d 2h 30m)."""
    count = 0
    readable_time = ""
    time_list = []
    time_suffix_list = ["s", "m", "h", "days"]

    while count < 4:
        count += 1
        remainder, result = divmod(seconds, 60) if count < 3 else divmod(seconds, 24)
        if seconds == 0 and remainder == 0:
            break
        time_list.append(int(result))
        seconds = int(remainder)

    for x in range(len(time_list)):
        time_list[x] = str(time_list[x]) + time_suffix_list[x]

    if len(time_list) == 4:
        readable_time += time_list.pop() + ", "

    time_list.reverse()
    readable_time += " ".join(time_list)
    
    return readable_time
    
