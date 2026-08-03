import asyncio
import logging
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors import FloodWait

from config import FORCE_PIC, FORCE_MSG, LOG_CHANNEL_ID, START_PIC, START_MSG
from helper_func import subscribed, decode, get_messages, get_readable_time
from database.database import (
    is_user_present, add_user, is_user_banned, get_ban_reason, 
    is_maintenance, is_admin, get_auto_delete_status, get_protect_status,
    get_auto_delete_time
)

logging.basicConfig(level=logging.INFO)

@Client.on_message(filters.command("start") & filters.private)
async def start_command(client: Client, message: Message):
    user_id = message.from_user.id
    text = message.text
    first_name = message.from_user.first_name or "User"
    username = message.from_user.username or ""

    if not await subscribed(client, message):
        buttons = []
        row = []
        for i, key in enumerate(["fs1", "fs2", "fs3", "fs4"], start=1):
            link = client.invitelinks.get(key)
            if link:
                row.append(InlineKeyboardButton(f"ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ {i}", url=link))
                if len(row) == 2:
                    buttons.append(row)
                    row = []
        if row: buttons.append(row)
        
        # Capture the payload (if they are requesting a file) to attach it to the refresh button
        payload = text.split(" ", 1)[1] if len(text.split()) > 1 else ""
        if len(payload) > 50: payload = "" # Safeguard to avoid Telegram button data limits
        
        buttons.append([InlineKeyboardButton("🔄 ʀᴇꜰʀᴇꜱʜ", callback_data=f"refresh_{payload}")])
            
        return await message.reply_photo(
            photo=FORCE_PIC, 
            caption=FORCE_MSG.format(first=first_name), 
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    if await is_user_banned(user_id):
        return await message.reply_text(f"🚫 ʏᴏᴜ ᴀʀᴇ ʙᴀɴɴᴇᴅ.\nʀᴇᴀꜱᴏɴ: {await get_ban_reason(user_id)}")

    if not await is_user_present(user_id):
        await add_user(user_id, first_name, username)
        NEW_USER_TXT = """#New_User {}\n\n≈ ɪᴅ:- <code>{}</code>\n≈ ɴᴀᴍᴇ:- {}"""
        try: await client.send_message(LOG_CHANNEL_ID, NEW_USER_TXT.format(message.from_user.mention, user_id, first_name))
        except: pass

    if await is_maintenance(user_id):
        return await message.reply_text("🛠 ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ ᴍᴏᴅᴇ ᴏɴ. ɴᴏʀᴍᴀʟ ᴏᴘᴇʀᴀᴛɪᴏɴꜱ ᴀʀᴇ ᴛᴇᴍᴘᴏʀᴀʀɪʟʏ ᴘᴀᴜꜱᴇᴅ.")

    if len(text.split()) > 1:
        try:
            argument = (await decode(text.split(" ", 1)[1])).split("-")
            ids = range(int(argument[1]) // abs(client.db_channel.id), (int(argument[2]) // abs(client.db_channel.id)) + 1) if len(argument) == 3 else [int(argument[1]) // abs(client.db_channel.id)]
        except Exception: return

        temp = await message.reply_text("⏳ ᴘʀᴏᴄᴇꜱꜱɪɴɢ...")
        messages = await get_messages(client, ids)
        await temp.delete()

        copied_msgs = []
        is_protected = await get_protect_status()
        
        for msg in messages:
            if msg.empty: continue 
            try:
                copied = await msg.copy(chat_id=user_id, caption=msg.caption.html if msg.caption else "", parse_mode=ParseMode.HTML, protect_content=is_protected)
                copied_msgs.append(copied)
            except FloodWait as e:
                await asyncio.sleep(e.value)
                copied = await msg.copy(chat_id=user_id, caption=msg.caption.html if msg.caption else "", parse_mode=ParseMode.HTML, protect_content=is_protected)
                copied_msgs.append(copied)
            except Exception as e: logging.error(f"Copy error: {e}")

        if not copied_msgs: 
            return await message.reply("❌ <b>ᴇʀʀᴏʀ:</b> ꜰɪʟᴇꜱ ᴜɴᴀᴠᴀɪʟᴀʙʟᴇ ᴏʀ ᴅᴇʟᴇᴛᴇᴅ ꜰʀᴏᴍ ᴛʜᴇ ᴅᴀᴛᴀʙᴀꜱᴇ.")

        if await get_auto_delete_status():
            auto_delete_time = await get_auto_delete_time()
            if auto_delete_time > 0:
                warn = await message.reply(f"<b>❗️ <u>ɪᴍᴘᴏʀᴛᴀɴᴛ</u> ❗️</b>\n\nᴛʜɪꜱ ꜰɪʟᴇ ᴡɪʟʟ ʙᴇ ᴅᴇʟᴇᴛᴇᴅ ɪɴ <b>{get_readable_time(auto_delete_time)}</b>.")
                asyncio.create_task(delete_files(copied_msgs, client, warn, text.split(" ", 1)[1], auto_delete_time))
        return

    btn = [
        [
            InlineKeyboardButton("🧠 ʜᴇʟᴘ", callback_data="help"), 
            InlineKeyboardButton("🔰 ᴀʙᴏᴜᴛ", callback_data="about")
        ]
    ]
    if await is_admin(user_id): 
        btn.append([
            InlineKeyboardButton("⚙️ ꜱᴇᴛᴛɪɴɢꜱ", callback_data="settings")
        ])
        
    await message.reply_photo(
        photo=START_PIC, 
        caption=START_MSG.format(first=first_name), 
        reply_markup=InlineKeyboardMarkup(btn)
    )

@Client.on_callback_query(filters.regex(r"^refresh_"))
async def refresh_cb(client: Client, query: CallbackQuery):
    user_id = query.from_user.id
    first_name = query.from_user.first_name or "User"
    
    if not await subscribed(client, query):
        return await query.answer("❌ ʏᴏᴜ ʜᴀᴠᴇɴ'ᴛ ᴊᴏɪɴᴇᴅ ᴀʟʟ ᴄʜᴀɴɴᴇʟꜱ ʏᴇᴛ!", show_alert=True)
        
    await query.answer("✅ ʏᴏᴜ ʜᴀᴠᴇ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ᴊᴏɪɴᴇᴅ!", show_alert=True)
    
    payload = query.data.split("_", 1)[1]
    
    # User just used /start without requesting a file
    if not payload:
        await query.message.delete()
        btn = [
            [
                InlineKeyboardButton("🧠 ʜᴇʟᴘ", callback_data="help"), 
                InlineKeyboardButton("🔰 ᴀʙᴏᴜᴛ", callback_data="about")
            ]
        ]
        if await is_admin(user_id): 
            btn.append([InlineKeyboardButton("⚙️ ꜱᴇᴛᴛɪɴɢꜱ", callback_data="settings")])
            
        return await client.send_photo(
            chat_id=user_id,
            photo=START_PIC, 
            caption=START_MSG.format(first=first_name), 
            reply_markup=InlineKeyboardMarkup(btn)
        )

    # User successfully joined to get a file, instantly deliver it!
    await query.message.delete()
    temp = await client.send_message(user_id, "⏳ ᴘʀᴏᴄᴇꜱꜱɪɴɢ...")
    
    try:
        argument = (await decode(payload)).split("-")
        ids = range(int(argument[1]) // abs(client.db_channel.id), (int(argument[2]) // abs(client.db_channel.id)) + 1) if len(argument) == 3 else [int(argument[1]) // abs(client.db_channel.id)]
    except Exception: 
        return await temp.delete()

    messages = await get_messages(client, ids)
    await temp.delete()

    copied_msgs = []
    is_protected = await get_protect_status()
    
    for msg in messages:
        if msg.empty: continue 
        try:
            copied = await msg.copy(chat_id=user_id, caption=msg.caption.html if msg.caption else "", parse_mode=ParseMode.HTML, protect_content=is_protected)
            copied_msgs.append(copied)
        except FloodWait as e:
            await asyncio.sleep(e.value)
            copied = await msg.copy(chat_id=user_id, caption=msg.caption.html if msg.caption else "", parse_mode=ParseMode.HTML, protect_content=is_protected)
            copied_msgs.append(copied)
        except Exception as e: logging.error(f"Copy error: {e}")

    if not copied_msgs: 
        return await client.send_message(user_id, "❌ <b>ᴇʀʀᴏʀ:</b> ꜰɪʟᴇꜱ ᴜɴᴀᴠᴀɪʟᴀʙʟᴇ ᴏʀ ᴅᴇʟᴇᴛᴇᴅ ꜰʀᴏᴍ ᴛʜᴇ ᴅᴀᴛᴀʙᴀꜱᴇ.")

    if await get_auto_delete_status():
        auto_delete_time = await get_auto_delete_time()
        if auto_delete_time > 0:
            warn = await client.send_message(user_id, f"<b>❗️ <u>ɪᴍᴘᴏʀᴛᴀɴᴛ</u> ❗️</b>\n\nᴛʜɪꜱ ꜰɪʟᴇ ᴡɪʟʟ ʙᴇ ᴅᴇʟᴇᴛᴇᴅ ɪɴ <b>{get_readable_time(auto_delete_time)}</b>.")
            asyncio.create_task(delete_files(copied_msgs, client, warn, payload, auto_delete_time))


async def delete_files(messages, client, main_message, payload, timer):
    await asyncio.sleep(timer)
    for msg in messages:
        try: await client.delete_messages(chat_id=msg.chat.id, message_ids=msg.id)
        except: pass
    try: 
        await main_message.edit_text(
            text="✅ <b>ʏᴏᴜʀ ꜰɪʟᴇ ʜᴀꜱ ʙᴇᴇɴ ᴅᴇʟᴇᴛᴇᴅ.</b>\n👇 ᴄʟɪᴄᴋ ʙᴇʟᴏᴡ ᴛᴏ ɢᴇᴛ ɪᴛ ᴀɢᴀɪɴ.", 
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("♻️ ɢᴇᴛ ꜰɪʟᴇ ᴀɢᴀɪɴ", url=f"https://t.me/{client.username}?start={payload}")
                ]
            ])
        )
    except: pass
        
