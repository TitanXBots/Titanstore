import urllib.parse
from pyrogram import filters, Client
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from config import USER_REPLY_TEXT
from helper_func import encode
from database.database import is_admin, get_tenant_by_db, get_global_db_channel

IGNORE_CMDS = [
    'start','users','broadcast','batch','genlink','stats','joinchannels','pypi',
    'restart','settings','joinchannelon','joinchanneloff','admin','autodelete',
    'autodeleteon','autodeleteoff','maintenance','ban','unban','bannedlist',
    'addadmin','removeadmin','adminlist', 'about', 'help', 'connect'
]

@Client.on_message(filters.private & filters.incoming & ~filters.command(IGNORE_CMDS))
async def private_message_handler(client: Client, message: Message):
    if not await is_admin(message.from_user.id):
        try: 
            await message.reply_text(USER_REPLY_TEXT, quote=True)
        except: 
            pass

@Client.on_message(filters.channel & filters.incoming)
async def new_post(client: Client, message: Message):
    chat_id = message.chat.id
    owner_id = None
    
    global_db = await get_global_db_channel()
    if chat_id == global_db:
        owner_id = 0
    else:
        tenant = await get_tenant_by_db(chat_id)
        if tenant:
            owner_id = tenant["_id"]
            
    if owner_id is None:
        return

    converted_id = message.id * abs(chat_id)
    string = f"get-{owner_id}-{converted_id}"
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
        
