import base64
import re
import asyncio
import logging
from pyrogram.errors import MessageNotModified, UserNotParticipant, FloodWait
from pyrogram.enums import ChatMemberStatus, ParseMode

# --- UI EDITING ---
async def safe_edit(message, text, reply_markup=None):
    try:
        if message.photo or message.video or message.document or message.animation:
            return await message.edit_caption(caption=text, parse_mode=ParseMode.HTML, reply_markup=reply_markup)
        else:
            return await message.edit_text(text=text, parse_mode=ParseMode.HTML, reply_markup=reply_markup)
    except MessageNotModified:
        pass
    except Exception as e:
        logging.error(f"Safe Edit Error: {e}")

async def send_cancel_msg(client, chat_id):
    try: await client.send_message(chat_id, "❌ **ᴘʀᴏᴄᴇꜱꜱ ᴄᴀɴᴄᴇʟʟᴇᴅ!**")
    except: pass

# --- FORCE SUB CHECKER ---
async def subscribed(client, message_or_query, channels: list) -> bool:
    user_id = message_or_query.from_user.id
    for channel in channels:
        if not channel or str(channel) in ["0", "-100"]: continue
        try:
            member = await client.get_chat_member(chat_id=channel, user_id=user_id)
            if member.status in [ChatMemberStatus.BANNED, ChatMemberStatus.RESTRICTED]: return False
        except UserNotParticipant: return False
        except FloodWait as e:
            await asyncio.sleep(e.value)
            return await subscribed(client, message_or_query, channels)
        except Exception: pass
    return True

# --- ENCODING & DECODING ---
async def encode(string: str) -> str:
    string_bytes = string.encode("ascii")
    base64_bytes = base64.urlsafe_b64encode(string_bytes)
    return base64_bytes.decode("ascii").strip("=")

async def decode(base64_string: str) -> str:
    base64_string = base64_string.strip("-")
    padding = len(base64_string) % 4
    if padding != 0: base64_string += "=" * (4 - padding)
    base64_bytes = base64_string.encode("ascii")
    string_bytes = base64.urlsafe_b64decode(base64_bytes)
    return string_bytes.decode("ascii")

# --- DATABASE MESSAGE RETRIEVAL ---
async def get_messages(client, message_ids, chat_id):
    try:
        messages = await client.get_messages(chat_id=chat_id, message_ids=list(message_ids))
        return messages if isinstance(messages, list) else [messages]
    except FloodWait as e:
        await asyncio.sleep(e.value)
        return await get_messages(client, message_ids, chat_id)
    except Exception: return []

async def get_message_id(client, message, chat_id: int) -> int:
    if message.forward_from_chat and message.forward_from_chat.id == chat_id:
        return message.forward_from_message_id
    elif message.text:
        match = re.search(r"https://t.me/(?:c/)?(.*)/(\d+)", message.text)
        if match: return int(match.group(2))
    return 0

# --- TIME FORMATTING ---
def get_readable_time(seconds: int) -> str:
    count = 0
    readable_time = ""
    time_list = []
    time_suffix_list = ["s", "m", "h", "days"]
    while count < 4:
        count += 1
        remainder, result = divmod(seconds, 60) if count < 3 else divmod(seconds, 24)
        if seconds == 0 and remainder == 0: break
        time_list.append(int(result))
        seconds = int(remainder)
    for x in range(len(time_list)):
        time_list[x] = str(time_list[x]) + time_suffix_list[x]
    if len(time_list) == 4:
        readable_time += time_list.pop() + ", "
    time_list.reverse()
    readable_time += " ".join(time_list)
    return readable_time
    
