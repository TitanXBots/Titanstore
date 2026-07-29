import urllib.parse
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyromod.exceptions import ListenerTimeout

from helper_func import encode, get_message_id
from database.database import is_premium

@Client.on_message(filters.private & filters.command('batch'))
async def batch(client: Client, message: Message):
    if not await is_premium(message.from_user.id): 
        return await message.reply_text("⚠️ <b>ᴀᴄᴄᴇꜱꜱ ᴅᴇɴɪᴇᴅ:</b> ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴀɴᴅ ᴘʀᴇᴍɪᴜᴍ ᴍᴇᴍʙᴇʀꜱ ᴄᴀɴ ɢᴇɴᴇʀᴀᴛᴇ ʙᴀᴛᴄʜ ʟɪɴᴋꜱ.")

    while True:
        try:
            first_message = await client.ask(chat_id=message.from_user.id, text="ꜰᴏʀᴡᴀʀᴅ ꜰɪʀꜱᴛ ᴍᴇꜱꜱᴀɢᴇ ꜰʀᴏᴍ ᴅʙ ᴄʜᴀɴɴᴇʟ\nᴏʀ ꜱᴇɴᴅ ᴅʙ ᴘᴏꜱᴛ ʟɪɴᴋ", filters=(filters.forwarded | filters.text), timeout=60)
        except ListenerTimeout: return
        f_msg_id = await get_message_id(client, first_message)
        if f_msg_id: break
        await first_message.reply_text("❌ ɪɴᴠᴀʟɪᴅ ᴍᴇꜱꜱᴀɢᴇ (ɴᴏᴛ ꜰʀᴏᴍ ᴅʙ ᴄʜᴀɴɴᴇʟ)")

    while True:
        try:
            second_message = await client.ask(chat_id=message.from_user.id, text="ꜰᴏʀᴡᴀʀᴅ ʟᴀꜱᴛ ᴍᴇꜱꜱᴀɢᴇ ꜰʀᴏᴍ ᴅʙ ᴄʜᴀɴɴᴇʟ\nᴏʀ ꜱᴇɴᴅ ᴅʙ ᴘᴏꜱᴛ ʟɪɴᴋ", filters=(filters.forwarded | filters.text), timeout=60)
        except ListenerTimeout: return
        s_msg_id = await get_message_id(client, second_message)
        if s_msg_id: break
        await second_message.reply_text("❌ ɪɴᴠᴀʟɪᴅ ᴍᴇꜱꜱᴀɢᴇ (ɴᴏᴛ ꜰʀᴏᴍ ᴅʙ ᴄʜᴀɴɴᴇʟ)")

    if f_msg_id > s_msg_id:
        f_msg_id, s_msg_id = s_msg_id, f_msg_id

    string = f"get-{f_msg_id * abs(client.db_channel.id)}-{s_msg_id * abs(client.db_channel.id)}"
    base64_string = await encode(string)
    link = f"https://t.me/{client.username}?start={base64_string}"
    
    share_url = urllib.parse.quote(link)
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔁 ꜱʜᴀʀᴇ ᴜʀʟ", url=f"https://telegram.me/share/url?url={share_url}")
        ]
    ])
    await second_message.reply_text(f"<b>ʜᴇʀᴇ ɪꜱ ʏᴏᴜʀ ʙᴀᴛᴄʜ ʟɪɴᴋ:</b>\n\n{link}", reply_markup=keyboard)

@Client.on_message(filters.private & filters.command('genlink'))
async def link_generator(client: Client, message: Message):
    if not await is_premium(message.from_user.id): 
        return await message.reply_text("⚠️ <b>ᴀᴄᴄᴇꜱꜱ ᴅᴇɴɪᴇᴅ:</b> ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴀɴᴅ ᴘʀᴇᴍɪᴜᴍ ᴍᴇᴍʙᴇʀꜱ ᴄᴀɴ ɢᴇɴᴇʀᴀᴛᴇ ʟɪɴᴋꜱ.")

    while True:
        try:
            channel_message = await client.ask(chat_id=message.from_user.id, text="ꜰᴏʀᴡᴀʀᴅ ᴍᴇꜱꜱᴀɢᴇ ꜰʀᴏᴍ ᴅʙ ᴄʜᴀɴɴᴇʟ\nᴏʀ ꜱᴇɴᴅ ᴅʙ ᴘᴏꜱᴛ ʟɪɴᴋ", filters=(filters.forwarded | filters.text), timeout=60)
        except ListenerTimeout: return
        msg_id = await get_message_id(client, channel_message)
        if msg_id: break
        await channel_message.reply_text("❌ ɪɴᴠᴀʟɪᴅ ᴍᴇꜱꜱᴀɢᴇ (ɴᴏᴛ ꜰʀᴏᴍ ᴅʙ ᴄʜᴀɴɴᴇʟ)")

    base64_string = await encode(f"get-{msg_id * abs(client.db_channel.id)}")
    link = f"https://t.me/{client.username}?start={base64_string}"
    
    share_url = urllib.parse.quote(link)
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔁 ꜱʜᴀʀᴇ ᴜʀʟ", url=f"https://telegram.me/share/url?url={share_url}")
        ]
    ])
    await channel_message.reply_text(f"<b>ʜᴇʀᴇ ɪꜱ ʏᴏᴜʀ ʟɪɴᴋ:</b>\n\n{link}", reply_markup=keyboard)
    
