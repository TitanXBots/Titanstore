import base64
import asyncio
import re

from pyrogram import filters
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import UserNotParticipant, FloodWait, MessageNotModified

from config import FORCE_CHANNELS, OWNER_ID
from database.database import is_admin


# ---------------- AUTO DELETE ----------------
async def auto_delete(msg, delay=60):
    await asyncio.sleep(delay)
    try:
        await msg.delete()
    except:
        pass


# ---------------- SAFE EDIT ----------------
async def safe_edit(message, text, buttons=None):

    try:
        if message.text != text:
            return await message.edit_text(
                text=text,
                reply_markup=buttons,
                disable_web_page_preview=True
            )

    except MessageNotModified:
        return

    except:
        try:
            return await message.reply_text(
                text=text,
                reply_markup=buttons,
                disable_web_page_preview=True
            )
        except:
            return


# ---------------- BASE64 ----------------
async def encode(text: str) -> str:
    return base64.urlsafe_b64encode(text.encode()).decode().rstrip("=")


async def decode(text: str) -> str:
    text = text.strip("=")
    padded = text + "=" * (-len(text) % 4)
    return base64.urlsafe_b64decode(padded.encode()).decode()


# ---------------- SUBSCRIPTION CHECK ----------------
async def check_subscription(client, user_id: int) -> bool:

    if await is_admin(user_id) or user_id == OWNER_ID:
        return True

    for channel in FORCE_CHANNELS:
        try:
            member = await client.get_chat_member(channel, user_id)

            if member.status not in [
                ChatMemberStatus.OWNER,
                ChatMemberStatus.ADMINISTRATOR,
                ChatMemberStatus.MEMBER
            ]:
                return False

        except UserNotParticipant:
            return False

        except:
            return False

    return True


subscribed = filters.create(check_subscription)


# ---------------- MESSAGE FETCH ----------------
async def get_messages(client, message_ids):

    messages = []
    batch_size = 200

    for i in range(0, len(message_ids), batch_size):

        batch = message_ids[i:i + batch_size]

        try:
            msgs = await client.get_messages(
                chat_id=client.db_channel.id,
                message_ids=batch
            )

        except FloodWait as e:
            await asyncio.sleep(e.value)
            msgs = await client.get_messages(
                chat_id=client.db_channel.id,
                message_ids=batch
            )

        except:
            msgs = []

        messages.extend(msgs)

    return messages


# ---------------- MESSAGE ID EXTRACTOR (FIXED) ----------------
async def get_message_id(client, message):

    if message.forward_from_chat:
        if message.forward_from_chat.id == client.db_channel.id:
            return message.forward_from_message_id
        return 0

    if message.text:
        pattern = r"https://t.me/(?:c/)?(\d+|[a-zA-Z0-9_]+)/(\d+)"
        match = re.search(pattern, message.text)

        if match:
            return int(match.group(2))

    return 0


# ---------------- TIME FORMAT ----------------
def get_readable_time(seconds: int) -> str:

    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)

    result = []

    if days:
        result.append(f"{days}d")
    if hours:
        result.append(f"{hours}h")
    if minutes:
        result.append(f"{minutes}m")
    if seconds or not result:
        result.append(f"{seconds}s")

    return " ".join(result)
