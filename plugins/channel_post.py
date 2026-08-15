from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ParseMode
from config import LOG_CHANNEL_ID
from helper_func import encode
from database.database import get_global_db_channel, is_admin

@Client.on_message(filters.channel & ~filters.forwarded)
async def channel_post_handler(client: Client, message: Message):
    db_chat_id = await get_global_db_channel()
    
    if message.chat.id != db_chat_id:
        return

    if message.media:
        media_type = message.media.value
        msg_id = message.id
        
        base64_string = await encode(f"get-{msg_id * abs(db_chat_id)}")
        link = f"https://t.me/{client.username}?start={base64_string}"
        
        reply_markup = message.reply_markup
        
        text = (
            f"<b>📁 ɴᴇᴡ ꜰɪʟᴇ ᴀᴅᴅᴇᴅ!</b>\n\n"
            f"<b>≈ ꜰɪʟᴇ ɴᴀᴍᴇ:</b> <code>{getattr(message, media_type).file_name if getattr(message, media_type, None) else 'Media'}</code>\n"
            f"<b>≈ ꜱʜᴀʀᴇ ʟɪɴᴋ:</b> <code>{link}</code>"
        )
        
        try:
            await client.send_message(
                LOG_CHANNEL_ID,
                text,
                disable_web_page_preview=True
            )
        except Exception:
            pass
            
