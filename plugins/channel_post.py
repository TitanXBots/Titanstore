from pyrogram import Client, filters
from pyrogram.types import Message
from database.database import get_global_db_channel, db

@Client.on_message(filters.channel & ~filters.forwarded)
async def channel_post_handler(client: Client, message: Message):
    db_chat_id = await get_global_db_channel()
    
    if message.chat.id != db_chat_id:
        return

    # Automatically indexes incoming media files from your database channel silently without log spam
    if message.media:
        media = getattr(message, message.media.value)
        file_id = getattr(media, "file_id", None)
        file_unique_id = getattr(media, "file_unique_id", None)
        file_name = getattr(media, "file_name", "Media")
        
        if file_id:
            await db.media.update_one(
                {"message_id": message.id},
                {
                    "$set": {
                        "file_id": file_id,
                        "file_unique_id": file_unique_id,
                        "file_name": file_name,
                        "message_id": message.id,
                        "chat_id": message.chat.id
                    }
                },
                upsert=True
            )
            
