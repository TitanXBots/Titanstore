from pyrogram import Client, filters
from pyrogram.types import Message

from database.database import collection  # OR telegram_files collection
from database.database import is_admin


# -------------------------------
# HELPERS
# -------------------------------
def convertmsg(msg: str) -> str:
    words = msg.lower().split()
    return " ".join(words[1:]) if len(words) > 1 else ""


def checkmsg(msg: str):
    if msg == "on":
        return True
    elif msg == "off":
        return False
    return None


# -------------------------------
# MAINTENANCE COMMAND
# -------------------------------
@Client.on_message(filters.command("maintenance"))
async def maintenance(client: Client, message: Message):

    user_id = message.from_user.id

    # ADMIN CHECK (MOTOR)
    if not await is_admin(user_id):
        return

    # VALIDATION
    if len(message.text.split()) < 2:
        return await message.reply_text(
            "Correct usage:\n/maintenance on OR /maintenance off"
        )

    msg = convertmsg(message.text)
    status = checkmsg(msg)

    if status is None:
        return await message.reply_text("Invalid argument. Use on/off only.")

    # -------------------------------
    # DB FETCH (MOTOR FIXED)
    # -------------------------------
    data = await collection.find_one({"admin_id": user_id})

    # -------------------------------
    # TURN ON
    # -------------------------------
    if status is True:

        if data:
            if data.get("maintenance") == "on":
                return await message.reply_text("⚠️ Already ON")
            else:
                await collection.update_one(
                    {"admin_id": user_id},
                    {"$set": {"maintenance": "on"}}
                )
                return await message.reply_text("✅ Maintenance ON")

        else:
            await collection.insert_one(
                {"admin_id": user_id, "maintenance": "on"}
            )
            return await message.reply_text("✅ Maintenance ON (new entry)")

    # -------------------------------
    # TURN OFF
    # -------------------------------
    else:

        if data:
            if data.get("maintenance") == "off":
                return await message.reply_text("⚠️ Already OFF")
            else:
                await collection.update_one(
                    {"admin_id": user_id},
                    {"$set": {"maintenance": "off"}}
                )
                return await message.reply_text("❌ Maintenance OFF")

        else:
            await collection.insert_one(
                {"admin_id": user_id, "maintenance": "off"}
            )
            return await message.reply_text("❌ Maintenance OFF (new entry)")
