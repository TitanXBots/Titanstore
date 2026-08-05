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
    get_auto_delete_time, get_tenant_config, get_file_again_status, get_force_sub_status,
    get_global_db_channel, get_global_fs_channels
)

logging.basicConfig(level=logging.INFO)

async def handle_file_delivery(client, user_id, message_or_query, payload):
    try:
        argument = (await decode(payload)).split("-")
        owner_id = 0
        
        if len(argument) >= 3: owner_id = int(argument[1])
        
        db_chat_id = await get_global_db_channel()
        fs_channels = await get_global_fs_channels()
        
        if owner_id != 0:
            tenant = await get_tenant_config(owner_id)
            if tenant:
                db_chat_id = tenant["db_channel"]
                fs_channels = tenant["fs_channels"]

        if len(argument) == 2: 
            ids = range(int(argument[1]) // abs(db_chat_id), (int(argument[1]) // abs(db_chat_id)) + 1)
        elif len(argument) == 3: 
            ids = [int(argument[2]) // abs(db_chat_id)]
        elif len(argument) == 4: 
            ids = range(int(argument[2]) // abs(db_chat_id), (int(argument[3]) // abs(db_chat_id)) + 1)
        else: return
    except Exception: return

    if await get_force_sub_status() and not await subscribed(client, message_or_query, fs_channels):
        buttons = []
        row = []
        for i, channel in enumerate(fs_channels, start=1):
            if not channel or str(channel) in ["0", "-100"]: continue
            try:
                link = client.invitelinks.get(str(channel))
                if not link:
                    chat = await client.get_chat(channel)
                    link = chat.invite_link or await client.export_chat_invite_link(channel)
                    client.invitelinks[str(channel)] = link
                row.append(InlineKeyboardButton(f"ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ {i}", url=link))
                if len(row) == 2:
                    buttons.append(row)
                    row = []
            except Exception as e:
                logging.error(f"Failed to generate FS link for {channel}: {e}")
        if row: buttons.append(row)
        
        refresh_payload = payload if len(payload) <= 50 else ""
        buttons.append([InlineKeyboardButton("🔄 ʀᴇꜰʀᴇꜱʜ", callback_data=f"refresh_{refresh_payload}")])
        
        first_name = message_or_query.from_user.first_name or "User"
        
        if isinstance(message_or_query, CallbackQuery):
            return await message_or_query.message.reply_photo(photo=FORCE_PIC, caption=FORCE_MSG.format(first=first_name), reply_markup=InlineKeyboardMarkup(buttons))
        return await message_or_query.reply_photo(photo=FORCE_PIC, caption=FORCE_MSG.format(first=first_name), reply_markup=InlineKeyboardMarkup(buttons))

    temp = await client.send_message(user_id, "⏳ ᴘʀᴏᴄᴇꜱꜱɪɴɢ...")
    messages = await get_messages(client, ids, db_chat_id)
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


@Client.on_message(filters.command("start") & filters.private)
async def start_command(client: Client, message: Message):
    user_id = message.from_user.id
    text = message.text
    first_name = message.from_user.first_name or "User"
    username = message.from_user.username or ""

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
        payload = text.split(" ", 1)[1]
        return await handle_file_delivery(client, user_id, message, payload)

    if await get_force_sub_status() and not await subscribed(client, message):
        fs_channels = await get_global_fs_channels()
        buttons = []
        row = []
        for i, channel in enumerate(fs_channels, start=1):
            if not channel or str(channel) in ["0", "-100"]: continue
            try:
                link = client.invitelinks.get(str(channel))
                if not link:
                    chat = await client.get_chat(channel)
                    link = chat.invite_link or await client.export_chat_invite_link(channel)
                    client.invitelinks[str(channel)] = link
                row.append(InlineKeyboardButton(f"ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ {i}", url=link))
                if len(row) == 2:
                    buttons.append(row)
                    row = []
            except Exception as e:
                logging.error(f"Failed to generate FS link for {channel}: {e}")
        if row: buttons.append(row)
        buttons.append([InlineKeyboardButton("🔄 ʀᴇꜰʀᴇꜱʜ", callback_data="refresh_")])
        return await message.reply_photo(photo=FORCE_PIC, caption=FORCE_MSG.format(first=first_name), reply_markup=InlineKeyboardMarkup(buttons))

    btn = [[InlineKeyboardButton("🧠 ʜᴇʟᴘ", callback_data="help"), InlineKeyboardButton("🔰 ᴀʙᴏᴜᴛ", callback_data="about")]]
    if await is_admin(user_id): btn.append([InlineKeyboardButton("⚙️ ꜱᴇᴛᴛɪɴɢꜱ", callback_data="settings")])
    await message.reply_photo(photo=START_PIC, caption=START_MSG.format(first=first_name), reply_markup=InlineKeyboardMarkup(btn))


@Client.on_callback_query(filters.regex(r"^refresh_"))
async def refresh_cb(client: Client, query: CallbackQuery):
    user_id = query.from_user.id
    first_name = query.from_user.first_name or "User"
    payload = query.data.split("_", 1)[1]
    
    if payload:
        await query.message.delete()
        return await handle_file_delivery(client, user_id, query, payload)
        
    if await get_force_sub_status() and not await subscribed(client, query):
        return await query.answer("❌ ʏᴏᴜ ʜᴀᴠᴇɴ'ᴛ ᴊᴏɪɴᴇᴅ ᴀʟʟ ᴄʜᴀɴɴᴇʟꜱ ʏᴇᴛ!", show_alert=True)
        
    await query.answer("✅ ʏᴏᴜ ʜᴀᴠᴇ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ᴊᴏɪɴᴇᴅ!", show_alert=True)
    await query.message.delete()
    
    btn = [[InlineKeyboardButton("🧠 ʜᴇʟᴘ", callback_data="help"), InlineKeyboardButton("🔰 ᴀʙᴏᴜᴛ", callback_data="about")]]
    if await is_admin(user_id): btn.append([InlineKeyboardButton("⚙️ ꜱᴇᴛᴛɪɴɢꜱ", callback_data="settings")])
    await client.send_photo(chat_id=user_id, photo=START_PIC, caption=START_MSG.format(first=first_name), reply_markup=InlineKeyboardMarkup(btn))

async def delete_files(messages, client, main_message, payload, timer):
    await asyncio.sleep(timer)
    for msg in messages:
        try: await client.delete_messages(chat_id=msg.chat.id, message_ids=msg.id)
        except: pass
        
    show_button = await get_file_again_status()
    
    try: 
        text_content = "✅ <b>ʏᴏᴜʀ ꜰɪʟᴇ ʜᴀꜱ ʙᴇᴇɴ ᴅᴇʟᴇᴛᴇᴅ.</b>"
        markup = None
        
        if show_button:
            text_content += "\n👇 ᴄʟɪᴄᴋ ʙᴇʟᴏᴡ ᴛᴏ ɢᴇᴛ ɪᴛ ᴀɢᴀɪɴ."
            markup = InlineKeyboardMarkup([[InlineKeyboardButton("♻️ ɢᴇᴛ ꜰɪʟᴇ ᴀɢᴀɪɴ", url=f"https://t.me/{client.username}?start={payload}")]])
            
        await main_message.edit_text(text=text_content, reply_markup=markup)
    except: pass
        
