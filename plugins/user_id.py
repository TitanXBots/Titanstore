# plugins/id.py
from pyrogram import filters, enums
from pyrogram.types import Message
from pyrogram import Client  # Import the Client class
#from bot import Bot #No Need to import bot here since it get initialed during start

@Client.on_message(filters.command("id") & filters.private)
async def showid(client:Client, message: Message):  #Explicit typing with client : Client
    chat_type = message.chat.type

    if chat_type == enums.ChatType.PRIVATE:
        user_id = message.chat.id
        await message.reply_text(
            f"Your User ID Is : {user_id}",
            quote=True
        )

# Jishu Developer
# Don't Remove Credit 🥺
# Telegram Channel @Madflix_Bots
# Backup Channel @JishuBotz
# Developer @JishuDeveloper
