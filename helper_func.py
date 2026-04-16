# helper_func.py
import base64
import re
import asyncio

from pyrogram import filters
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import UserNotParticipant, FloodWait, MessageNotModified

from config import (
    FORCE_SUB_CHANNEL_1,
    FORCE_SUB_CHANNEL_2,
    FORCE_SUB_CHANNEL_3,
    FORCE_SUB_CHANNEL_4,
    OWNER_ID
)

from database.database import admins_collection, banned_users


# -------------------------------
# AUTO DELETE
# -------------------------------
async def auto_delete(msg, delay=60):
    await asyncio.sleep(delay)
    try:
        await msg.delete()
    except:
        pass


# -------------------------------
# SAFE EDIT
# -------------------------------
async def safe_edit(message, text, buttons=None):
    try:
        if message.text != text:
            await message.edit_text(
                text=text,
                reply_markup=buttons,
                disable_web_page_preview=True
            )
    except MessageNotModified:
        pass
    except:
        try:
            await message.reply_text(
                text=text,
                reply_markup=buttons,
                disable_web_page_preview=True
            )
        except:
            pass


# -------------------------------
# INPUT HELPER (FIXED)
# -------------------------------
async def get_input(client, message, prompt):
    new_text = f"{prompt}\n\nSend /cancel to stop."

    # ✅ Prevent MESSAGE_NOT_MODIFIED
    try:
        if message.text != new_text:
            await message.edit_text(new_text)
    except MessageNotModified:
        pass

    try:
        msg = await client.listen(message.chat.id, timeout=300)

        if not msg.text:
            m = await msg.reply("❌ Invalid input!")
            asyncio.create_task(auto_delete(m))
            return None

        if msg.text.lower() == "/cancel":
            m = await msg.reply("❌ Cancelled!")
            asyncio.create_task(auto_delete(m))
            return None

        return msg.text

    except asyncio.TimeoutError:
        m = await message.reply("⌛ Timeout!")
        asyncio.create_task(auto_delete(m))
        return None


# -------------------------------
# OWNER / ADMIN CHECK
# -------------------------------
async def is_owner(user_id: int) -> bool:
    return user_id == OWNER_ID


async def is_admin(user_id: int) -> bool:
    if user_id == OWNER_ID:
        return True

    data = await admins_collection.find_one({"_id": user_id})
    return data is not None


# -------------------------------
# FORCE SUB
# -------------------------------
async def is_subscribed(filter, client, update):
    user_id = update.from_user.id

    if await is_admin(user_id):
        return True

    channels = [
        FORCE_SUB_CHANNEL_1,
        FORCE_SUB_CHANNEL_2,
        FORCE_SUB_CHANNEL_3,
        FORCE_SUB_CHANNEL_4
    ]

    for channel in channels:
        if not channel:
            continue

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


subscribed = filters.create(is_subscribed)


# -------------------------------
# BASE64
# -------------------------------
async def encode(string: str) -> str:
    return base64.urlsafe_b64encode(string.encode()).decode().rstrip("=")


async def decode(base64_string: str) -> str:
    base64_string = base64_string.strip("=")
    padded = base64_string + "=" * (-len(base64_string) % 4)
    return base64.urlsafe_b64decode(padded.encode()).decode()


# -------------------------------
# GET MESSAGES
# -------------------------------
async def get_messages(client, message_ids):
    messages = []
    total = 0

    while total != len(message_ids):
        batch = message_ids[total:total + 200]

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
        total += len(batch)

    return messages


# -------------------------------
# MESSAGE ID EXTRACTOR
# -------------------------------
async def get_message_id(client, message):
    if message.forward_from_chat:
        if message.forward_from_chat.id == client.db_channel.id:
            return message.forward_from_message_id
        return 0

    if message.forward_sender_name:
        return 0

    if message.text:
        pattern = r"https://t.me/(?:c/)?(.*)/(\\d+)"
        match = re.match(pattern, message.text)

        if not match:
            return 0

        chat = match.group(1)
        msg_id = int(match.group(2))

        if chat.isdigit():
            if f"-100{chat}" == str(client.db_channel.id):
                return msg_id
        else:
            if chat == client.db_channel.username:
                return msg_id

    return 0
