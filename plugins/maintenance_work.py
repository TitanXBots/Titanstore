from pyrogram import Client, filters
from pyrogram.types import Message
from pymongo import MongoClient
from config import DB_URI, DB_NAME
from database.database import * # <- dynamic admin check from your DB

client = MongoClient(DB_URI)
db = client[DB_NAME]
collection = db["TelegramFiles"]


async def convertmsg(msg: str) -> str:
    words = msg.lower().split()
    if len(words) > 1:
        return " ".join(words[1:])
    else:
        return ""


async def checkmsg(msg: str) -> bool:
    if msg == 'on':
        return True
    elif msg == 'off':
        return False
    else:
        return None


@Client.on_message(filters.command("maintenance"))
async def maintenance(client: Client, message: Message):
    user_id = message.from_user.id
    if not await is_admin(user_id):  # <-- dynamic admin check
        return  # Ignore non-admins

    if not message.text.split()[1:]:
        await message.reply_text("Correct the command format. Usage: /maintenance [on/off]")
        return

    msg = await convertmsg(message.text)
    status = await checkmsg(msg)

    check_msg = collection.find_one({"admin_id": user_id})

    if status is True:
        if check_msg:
            if check_msg.get("maintenance") == "on":
                await message.reply_text("ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ ᴍᴏᴅᴇ ɪꜱ ᴀʟʀᴇᴀᴅʏ ᴏɴ.")
            else:
                collection.update_one({"admin_id": user_id}, {"$set": {"maintenance": "on"}})
                await message.reply_text("ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ ᴍᴏᴅᴇ ᴛᴜʀɴᴇᴅ ᴏɴ.")
        else:
            collection.insert_one({"admin_id": user_id, "maintenance": "on"})
            await message.reply_text("ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ ᴍᴏᴅᴇ ᴛᴜʀɴᴇᴅ ᴏɴ (ɴᴇᴡ ᴇɴᴛʀʏ).")

    elif status is False:
        if check_msg:
            if check_msg.get("maintenance") == "off":
                await message.reply_text("ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ ᴍᴏᴅᴇ ɪꜱ ᴀʟʀᴇᴀᴅʏ ᴏꜰꜰ.")
            else:
                collection.update_one({"admin_id": user_id}, {"$set": {"maintenance": "off"}})
                await message.reply_text("ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ ᴍᴏᴅᴇ ᴛᴜʀɴᴇᴅ ᴏꜰꜰ.")
        else:
            collection.insert_one({"admin_id": user_id, "maintenance": "off"})
            await message.reply_text("ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ ᴍᴏᴅᴇ ᴛᴜʀɴᴇᴅ ᴏꜰꜰ (ɴᴇᴡ ᴇɴᴛʀʏ).")

    else:
        await message.reply_text("Invalid argument. Use /maintenance [on/off].")
