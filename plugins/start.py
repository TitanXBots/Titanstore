import asyncio
import logging
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors import FloodWait

from config import FORCE_PIC, FORCE_MSG, LOG_CHANNEL_ID, START_PIC, START_MSG, REFERRAL_POINTS
from helper_func import subscribed, decode, get_messages, get_readable_time
from database.database import (
    is_user_present, add_user, is_user_banned, get_ban_reason, 
    is_maintenance, get_auto_delete_status, get_protect_status,
    get_auto_delete_time, get_file_again_status, get_force_sub_status,
    get_global_db_channel, get_global_fs_channels, get_premium_status,
    get_user_approved_channels, add_referral_points, is_admin
)

logging.basicConfig(level=logging.INFO)

async def delete_files(messages, client, main_message, payload, timer):
    await asyncio.sleep(timer)
    for msg in messages:
        try: await client.delete_messages(chat_id=msg.chat.id, message_ids=msg.id)
        except: pass
    if await get_file_again_status():
        try:
            markup = InlineKeyboardMarkup([[InlineKeyboardButton("♻️ ɢᴇᴛ ꜰɪʟᴇ ᴀɢᴀɪɴ", url=f"https://t.me/{client.username}?start={payload}")]])
            await main_message.edit_text("✅ <b>ʏᴏᴜʀ ꜰɪʟᴇ ʜᴀꜱ ʙᴇᴇɴ ᴅᴇʟᴇᴛᴇᴅ.</b>\n👇 ᴄʟɪᴄᴋ ʙᴇʟᴏᴡ ᴛᴏ ɢᴇᴛ ɪᴛ ᴀɢᴀɪɴ.", reply_markup=markup)
        except: pass

async def handle_file_delivery(client, user_id, message_or_query, payload):
    try:
        argument = (await decode(payload)).split("-")
        cmd = argument[0]
        owner_id = None
        
        if cmd == "get":
            msg_val = int(argument[1])
            if len(argument) == 3: owner_id = int(argument[2])
        elif cmd == "batch":
            first_val = int(argument[1])
            last_val = int(argument[2])
            if len(argument) == 4: owner_id = int(argument[3])
        else: return
        
        db_chat_id = await get_global_db_channel()
        fs_channels = await get_global_fs_channels()

        if owner_id and await get_premium_status(owner_id):
            u_db = await get_user_approved_channels(owner_id, "db")
            u_fs = await get_user_approved_channels(owner_id, "fs")
            if u_db: db_chat_id = u_db[0]
            if u_fs: fs_channels = u_fs

        if not db_chat_id: return

        if cmd == "get":
            ids = [msg_val // abs(db_chat_id)]
        elif cmd == "batch":
            ids = range(first_val // abs(db_chat_id), (last_val // abs(db_chat_id)) + 1)
            
    except Exception as e:
        logging.error(f"Payload error: {e}")
        return

    # Check Force Sub
    if await get_force_sub_status() and not await subscribed(client, message_or_query, fs_channels):
        buttons, row = [], []
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
            except Exception as e: logging.error(f"FS Link Gen Error: {e}")
        if row: buttons.append(row)
        buttons.append([InlineKeyboardButton("🔄 ʀᴇꜰʀᴇꜱʜ", callback_data=f"refresh_{payload}")])
        
        first_name = message_or_query.from_user.first_name or "User"
        try:
            if isinstance(message_or_query, CallbackQuery):
                return await message_or_query.message.reply_photo(photo=FORCE_PIC, caption=FORCE_MSG.format(first=first_name), reply_markup=InlineKeyboardMarkup(buttons))
            return await message_or_query.reply_photo(photo=FORCE_PIC, caption=FORCE_MSG.format(first=first_name), reply_markup=InlineKeyboardMarkup(buttons))
        except Exception:
            # Fallback if image fails
            if isinstance(message_or_query, CallbackQuery):
                return await message_or_query.message.reply_text(text=FORCE_MSG.format(first=first_name), reply_markup=InlineKeyboardMarkup(buttons))
            return await message_or_query.reply_text(text=FORCE_MSG.format(first=first_name), reply_markup=InlineKeyboardMarkup(buttons))

    temp = await client.send_message(user_id, "⏳ ᴘʀᴏᴄᴇꜱꜱɪɴɢ...")
    messages = await get_messages(client, ids, db_chat_id)
    await temp.delete()

    copied_msgs, is_protected = [], await get_protect_status()
    
    for msg in messages:
        if msg.empty: continue 
        try:
            copied = await msg.copy(chat_id=user_id, caption=msg.caption.html if msg.caption else "", parse_mode=ParseMode.HTML, protect_content=is_protected)
            copied_msgs.append(copied)
        except FloodWait as e:
            await asyncio.sleep(e.value)
            copied = await msg.copy(chat_id=user_id, caption=msg.caption.html if msg.caption else "", parse_mode=ParseMode.HTML, protect_content=is_protected)
            copied_msgs.append(copied)
        except Exception: pass

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
    raw_text = message.text or message.caption or ""
    first_name = message.from_user.first_name or "User"
    username = message.from_user.username or ""

    try:
        if await is_user_banned(user_id):
            return await message.reply_text(f"🚫 ʏᴏᴜ ᴀʀᴇ ʙᴀɴɴᴇᴅ.\nʀᴇᴀꜱᴏɴ: {await get_ban_reason(user_id)}")

        payload = raw_text.split(" ", 1)[1] if len(raw_text.split()) > 1 else None

        # REFERRAL SYSTEM HANDLING
        if payload and payload.startswith("ref_"):
            try:
                referrer_id = int(payload.split("_")[1])
                if referrer_id != user_id and not await is_user_present(user_id):
                    await add_referral_points(referrer_id, REFERRAL_POINTS)
                    try: await client.send_message(referrer_id, f"🎉 **New Referral!** Someone joined using your link. You received {REFERRAL_POINTS} points!")
                    except: pass
            except Exception: pass
            payload = None 

        if not await is_user_present(user_id):
            await add_user(user_id, first_name, username)
            try: await client.send_message(LOG_CHANNEL_ID, f"#New_User\n\n≈ ɪᴅ:- <code>{user_id}</code>\n≈ ɴᴀᴍᴇ:- {first_name}")
            except: pass

        if await is_maintenance(user_id):
            return await message.reply_text("🛠 ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ ᴍᴏᴅᴇ ᴏɴ. ɴᴏʀᴍᴀʟ ᴏᴘᴇʀᴀᴛɪᴏɴꜱ ᴀʀᴇ ᴛᴇᴍᴘᴏʀᴀʀɪʟʏ ᴘᴀᴜꜱᴇᴅ.")

        if payload:
            return await handle_file_delivery(client, user_id, message, payload)

        # Dynamic UI - Normal users see 'My Account', Admins see 'Settings'
        btn = [
            [InlineKeyboardButton("👑 ᴍʏ ᴀᴄᴄᴏᴜɴᴛ", callback_data="my_account")],
            [InlineKeyboardButton("🧠 ʜᴇʟᴘ", callback_data="help"), InlineKeyboardButton("🔰 ᴀʙᴏᴜᴛ", callback_data="about")]
        ]
        if await is_admin(user_id):
            btn.append([InlineKeyboardButton("⚙️ ᴀᴅᴍɪɴ ꜱᴇᴛᴛɪɴɢꜱ", callback_data="settings")])

        # TRY SENDING WITH PHOTO FIRST, FALLBACK TO TEXT IF PHOTO FAILS
        try:
            await message.reply_photo(photo=START_PIC, caption=START_MSG.format(first=first_name), reply_markup=InlineKeyboardMarkup(btn))
        except Exception as e:
            logging.error(f"Image delivery failed: {e}")
            await message.reply_text(text=START_MSG.format(first=first_name), reply_markup=InlineKeyboardMarkup(btn))
            
    except Exception as e:
        logging.error(f"Start command crashed: {e}")


@Client.on_callback_query(filters.regex(r"^refresh_"))
async def refresh_cb(client: Client, query: CallbackQuery):
    try: await query.answer()
    except: pass
    payload = query.data.split("_", 1)[1]
    await query.message.delete()
    if payload:
        return await handle_file_delivery(client, query.from_user.id, query, payload)
    await start_command(client, query.message)
    
