from pyrogram import Client, filters
from pyrogram.types import Message

from database.database import maintenance_collection, is_admin


def convertmsg(msg: str) -> str:
    words = msg.lower().split()
    return " ".join(words[1:]) if len(words) > 1 else ""


def checkmsg(msg: str):
    if msg == "on":
        return True
    elif msg == "off":
        return False
    return None


@Client.on_message(filters.command("maintenance"))
async def maintenance(client: Client, message: Message):

    user_id = message.from_user.id

    if not await is_admin(user_id):
        return

    if len(message.text.split()) < 2:
        return await message.reply_text(
            "Correct usage:\n/maintenance on OR /maintenance off"
        )

    msg = convertmsg(message.text)
    status = checkmsg(msg)

    if status is None:
        return await message.reply_text("Invalid argument. Use on/off only.")

    data = await maintenance_collection.find_one({"admin_id": user_id})

    if status is True:
        if data and data.get("maintenance") == "on":
            return await message.reply_text("⚠️ Already ON")

        await maintenance_collection.update_one(
            {"admin_id": user_id},
            {"$set": {"maintenance": "on"}},
            upsert=True
        )
        return await message.reply_text("✅ Maintenance ON")

    else:
        if data and data.get("maintenance") == "off":
            return await message.reply_text("⚠️ Already OFF")

        await maintenance_collection.update_one(
            {"admin_id": user_id},
            {"$set": {"maintenance": "off"}},
            upsert=True
        )
        return await message.reply_text("❌ Maintenance OFF")
