import base64
import re
import asyncio
from pyrogram import filters
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import UserNotParticipant, FloodWait, MessageNotModified
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from config import START_PIC
from database.database import is_admin, is_owner, get_force_sub_status, get_global_fs_channels

async def delayed_delete(message, delay=7):
    await asyncio.sleep(delay)
    try: await message.delete()
    except: pass

async def send_cancel_notification(client, query, reply_markup):
    try:
        cancel_msg = await query.message.reply_photo(
            photo=START_PIC,
            caption="❌ <b>ᴘʀᴏᴄᴇꜱꜱ ᴄᴀɴᴄᴇʟʟᴇᴅ!</b>\n\nThe current operation has been successfully aborted.",
            reply_markup=reply_markup
        )
        asyncio.create_task(delayed_delete(cancel_msg, delay=7))
    except Exception:
        pass

async def safe_edit(message, text, buttons=None):
    try:
        if message.photo or message.video or message.document:
            if message.caption != text: await message.edit_caption(caption=text, reply_markup=buttons)
        else:
            if message.text != text: await message.edit_text(text=text, reply_markup=buttons, disable_web_page_preview=True)
    except MessageNotModified: pass
    except Exception:
        try: await message.reply_text(text=text, reply_markup=buttons, disable_web_page_preview=True)
        except: pass

async def subscribed(client, message, custom_channels=None) -> bool:
    if not message.from_user: return True
    if not await get_force_sub_status(): return True

    user_id = message.from_user.id
    if await is_admin(user_id) or await is_owner(user_id): return True
    
    channels_to_check = custom_channels if custom_channels is not None else await get_global_fs_channels()
    
    for channel in channels_to_check:
        if not channel or str(channel) in ["0", "-100"]: continue
        try:
            chat_id = int(channel) if str(channel).startswith("-100") or str(channel).isdigit() else channel
            member = await client.get_chat_member(chat_id, user_id)
            if member.status not in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.MEMBER]: return False
        except UserNotParticipant: return False
        except FloodWait as e:
            await asyncio.sleep(e.value)
            try:
                member = await client.get_chat_member(chat_id, user_id)
                if member.status not in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.MEMBER]: return False
            except: return False
        except Exception: continue
    return True

async def encode(string: str) -> str:
    return base64.urlsafe_b64encode(string.encode()).decode().rstrip("=")

async def decode(base64_string: str) -> str:
    base64_string = base64_string.strip("=")
    padded = base64_string + "=" * (-len(base64_string) % 4)
    return base64.urlsafe_b64decode(padded.encode()).decode()

async def get_messages(client, message_ids, db_channel_id):
    messages, total = [], 0
    while total != len(message_ids):
        batch = message_ids[total:total + 200]
        try: msgs = await client.get_messages(chat_id=db_channel_id, message_ids=batch)
        except FloodWait as e:
            await asyncio.sleep(e.value)
            msgs = await client.get_messages(chat_id=db_channel_id, message_ids=batch)
        except: msgs = []
        messages.extend(msgs)
        total += len(batch)
    return messages

async def get_message_id(client, message, expected_channel_id):
    if message.forward_from_chat:
        return message.forward_from_message_id if message.forward_from_chat.id == expected_channel_id else 0
    if message.forward_sender_name: return 0
    text = message.text or message.caption or ""
    if text:
        match = re.search(r"https://t.me/(?:c/)?([^/]+)/(\d+)", text)
        if match:
            chat, msg_id = match.group(1), int(match.group(2))
            if chat in [str(expected_channel_id), str(expected_channel_id).replace("-100", "")]: return msg_id
    return 0

def get_readable_time(seconds: int) -> str:
    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    res = []
    if days: res.append(f"{days}d")
    if hours: res.append(f"{hours}h")
    if minutes: res.append(f"{minutes}m")
    if seconds or not res: res.append(f"{seconds}s")
    return " ".join(res)

async def get_user_input(client, message_or_query, text, reply_markup, timeout=60):
    chat_id = message_or_query.message.chat.id if isinstance(message_or_query, CallbackQuery) else message_or_query.chat.id
    user_id = message_or_query.from_user.id
    
    msg_to_edit = message_or_query.message if isinstance(message_or_query, CallbackQuery) else message_or_query
    await safe_edit(msg_to_edit, text, reply_markup)
    
    loop = asyncio.get_running_loop()
    future = loop.create_future()
    
    @client.on_message(filters.chat(chat_id) & filters.user(user_id), group=-1)
    async def message_handler(c, m):
        if not future.done():
            future.set_result(("message", m))
        m.stop_propagation()

    @client.on_callback_query(filters.user(user_id), group=-1)
    async def callback_handler(c, q):
        if not future.done():
            future.set_result(("callback", q))

    client.add_handler(message_handler, group=-1)
    client.add_handler(callback_handler, group=-1)

    try:
        result_type, result_obj = await asyncio.wait_for(future, timeout=timeout)
        return result_type, result_obj
    except asyncio.TimeoutError:
        return "timeout", None
    finally:
        try: client.remove_handler(message_handler, group=-1)
        except: pass
        try: client.remove_handler(callback_handler, group=-1)
        except: pass
            
