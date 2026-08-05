import urllib.parse
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyromod.exceptions import ListenerTimeout

from helper_func import encode, get_message_id
from database.database import is_premium, get_tenant_config
from config import CHANNEL_ID

@Client.on_message(filters.private & filters.command('batch'))
async def batch(client: Client, message: Message):
    user_id = message.from_user.id
    if not await is_premium(user_id): 
        return await message.reply_text("⚠️ <b>ᴀᴄᴄᴇꜱꜱ ᴅᴇɴɪᴇᴅ:</b> ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴀɴᴅ ᴘʀᴇᴍɪᴜᴍ ᴍᴇᴍʙᴇʀꜱ ᴄᴀɴ ɢᴇɴᴇʀᴀᴛᴇ ʙᴀᴛᴄʜ ʟɪɴᴋꜱ.")

    tenant = await get_tenant_config(user_id)
    expected_db_channel = tenant["db_channel"] if tenant else CHANNEL_ID
    owner_id = user_id if tenant else 0

    while True:
        try:
            first_message = await client.ask(chat_id=user_id, text="ꜰᴏʀᴡᴀʀᴅ ꜰɪʀꜱᴛ ᴍᴇꜱꜱᴀɢᴇ ꜰʀᴏᴍ ᴅʙ ᴄʜᴀɴɴᴇʟ\nᴏʀ ꜱᴇɴᴅ ᴅʙ ᴘᴏꜱᴛ ʟɪɴᴋ", filters=(filters.forwarded | filters.text), timeout=60)
        except ListenerTimeout: return
        f_msg_id = await get_message_id(client, first_message, expected_db_channel)
        if f_msg_id: break
        await first_message.reply_text("❌ ɪɴᴠᴀʟɪᴅ ᴍᴇꜱꜱᴀɢᴇ (ɴᴏᴛ ꜰʀᴏᴍ ʏᴏᴜʀ ᴀᴘᴘʀᴏᴠᴇᴅ ᴅʙ ᴄʜᴀɴɴᴇʟ)")

    while True:
        try:
            second_message = await client.ask(chat_id=user_id, text="ꜰᴏʀᴡᴀʀᴅ ʟᴀꜱᴛ ᴍᴇꜱꜱᴀɢᴇ ꜰʀᴏᴍ ᴅʙ ᴄʜᴀɴɴᴇʟ\nᴏʀ ꜱᴇɴᴅ ᴅʙ ᴘᴏꜱᴛ ʟɪɴᴋ", filters=(filters.forwarded | filters.text), timeout=60)
        except ListenerTimeout: return
        s_msg_id = await get_message_id(client, second_message, expected_db_channel)
        if s_msg_id: break
        await second_message.reply_text("❌ ɪɴᴠᴀʟɪᴅ ᴍᴇꜱꜱᴀɢᴇ (ɴᴏᴛ ꜰʀᴏᴍ ʏᴏᴜʀ ᴀᴘᴘʀᴏᴠᴇᴅ ᴅʙ ᴄʜᴀɴɴᴇʟ)")

    if f_msg_id > s_msg_id:
        f_msg_id, s_msg_id = s_msg_id, f_msg_id

    # Smart Payload Calculation
    string = f"get-{owner_id}-{f_msg_id * abs(expected_db_channel)}-{s_msg_id * abs(expected_db_channel)}"
    base64_string = await encode(string)
    link = f"https://t.me/{client.username}?start={base64_string}"
    
    share_url = urllib.parse.quote(link)
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔁 ꜱʜᴀʀᴇ ᴜʀʟ", url=f"https://telegram.me/share/url?url={share_url}")]])
    await second_message.reply_text(f"<b>ʜᴇʀᴇ ɪꜱ ʏᴏᴜʀ ʙᴀᴛᴄʜ ʟɪɴᴋ:</b>\n\n{link}", reply_markup=keyboard)

@Client.on_message(filters.private & filters.command('genlink'))
async def link_generator(client: Client, message: Message):
    user_id = message.from_user.id
    if not await is_premium(user_id): 
        return await message.reply_text("⚠️ <b>ᴀᴄᴄᴇꜱꜱ ᴅᴇɴɪᴇᴅ:</b> ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴀɴᴅ ᴘʀᴇᴍɪᴜᴍ ᴍᴇᴍʙᴇʀꜱ ᴄᴀɴ ɢᴇɴᴇʀᴀᴛᴇ ʟɪɴᴋꜱ.")

    tenant = await get_tenant_config(user_id)
    expected_db_channel = tenant["db_channel"] if tenant else CHANNEL_ID
    owner_id = user_id if tenant else 0

    while True:
        try:
            channel_message = await client.ask(chat_id=user_id, text="ꜰᴏʀᴡᴀʀᴅ ᴍᴇꜱꜱᴀɢᴇ ꜰʀᴏᴍ ᴅʙ ᴄʜᴀɴɴᴇʟ\nᴏʀ ꜱᴇɴᴅ ᴅʙ ᴘᴏꜱᴛ ʟɪɴᴋ", filters=(filters.forwarded | filters.text), timeout=60)
        except ListenerTimeout: return
        msg_id = await get_message_id(client, channel_message, expected_db_channel)
        if msg_id: break
        await channel_message.reply_text("❌ ɪɴᴠᴀʟɪᴅ ᴍᴇꜱꜱᴀɢᴇ (ɴᴏᴛ ꜰʀᴏᴍ ʏᴏᴜʀ ᴀᴘᴘʀᴏᴠᴇᴅ ᴅʙ ᴄʜᴀɴɴᴇʟ)")

    # Smart Payload Calculation
    base64_string = await encode(f"get-{owner_id}-{msg_id * abs(expected_db_channel)}")
    link = f"https://t.me/{client.username}?start={base64_string}"
    
    share_url = urllib.parse.quote(link)
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔁 ꜱʜᴀʀᴇ ᴜʀʟ", url=f"https://telegram.me/share/url?url={share_url}")]])
    await channel_message.reply_text(f"<b>ʜᴇʀᴇ ɪꜱ ʏᴏᴜʀ ʟɪɴᴋ:</b>\n\n{link}", reply_markup=keyboard)
    
