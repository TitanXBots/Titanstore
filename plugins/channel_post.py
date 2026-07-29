import urllib.parse
from pyrogram import filters, Client
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from config import CHANNEL_ID, USER_REPLY_TEXT
from helper_func import encode

IGNORE_CMDS = [
    'start','users','broadcast','batch','genlink','stats','joinchannels','pypi',
    'restart','settings','joinchannelon','joinchanneloff','admin','autodelete',
    'autodeleteon','autodeleteoff','maintenance','ban','unban','bannedlist',
    'addadmin','removeadmin','adminlist', 'about', 'help'
]

@Client.on_message(filters.private & filters.incoming & ~filters.command(IGNORE_CMDS))
async def private_message_handler(client: Client, message: Message):
    try: 
        await message.reply_text(USER_REPLY_TEXT, quote=True)
    except: 
        pass

@Client.on_message(filters.channel & filters.incoming & filters.chat(CHANNEL_ID))
async def new_post(client: Client, message: Message):
    converted_id = message.id * abs(client.db_channel.id)
    string = f"get-{converted_id}"
    base64_string = await encode(string)
    link = f"https://t.me/{client.username}?start={base64_string}"

    share_url = urllib.parse.quote(link)
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔁 ꜱʜᴀʀᴇ ᴜʀʟ", url=f"https://telegram.me/share/url?url={share_url}")
        ]
    ])
    try: 
        await message.edit_reply_markup(keyboard)
    except: 
        pass
        
