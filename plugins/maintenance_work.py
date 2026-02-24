from pyrogram import Client, filters
from pyrogram.types import *
from pymongo import MongoClient
from config import DB_URI, DB_NAME, ADMINS

client = MongoClient(DB_URI)
db = client[DB_NAME]
collection = db["TelegramFiles"]

async def checkmsg(msg: str) -> bool:
    if msg == 'on':
        return True
    elif msg == 'off':
        return False
    else:
        return None

# Command to show the maintenance buttons
@Client.on_message(filters.command("maintenance") & filters.user(ADMINS))
async def maintenance_buttons(client: Client, message: Message):
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Maintenance ON", callback_data="maintenance_on"),
                InlineKeyboardButton("Maintenance OFF", callback_data="maintenance_off")
            ]
        ]
    )
    await message.reply_text("Select Maintenance Mode:", reply_markup=keyboard)

# Callback handler for buttons
@Client.on_callback_query(filters.user(ADMINS))
async def maintenance_callback(client: Client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    data = callback_query.data

    if data == "maintenance_on":
        check_msg = collection.find_one({"admin_id": user_id})
        if check_msg:
            if check_msg["maintenance"] == "on":
                await callback_query.answer("ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ ᴍᴏᴅᴇ ɪꜱ ᴀʟʀᴇᴀᴅʏ ᴏɴ.", show_alert=True)
            else:
                collection.update_one({"admin_id": user_id}, {"$set": {"maintenance": "on"}})
                await callback_query.answer("ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ ᴍᴏᴅᴇ ᴛᴜʀɴᴇᴅ ᴏɴ.", show_alert=True)
        else:
            collection.insert_one({"admin_id": user_id, "maintenance": "on"})
            await callback_query.answer("ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ ᴍᴏᴅᴇ ᴛᴜʀɴᴇᴅ ᴏɴ (ɴᴇᴡ ᴇɴᴛʀʏ).", show_alert=True)

    elif data == "maintenance_off":
        check_msg = collection.find_one({"admin_id": user_id})
        if check_msg:
            if check_msg["maintenance"] == "off":
                await callback_query.answer("ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ ᴍᴏᴅᴇ ɪꜱ ᴀʟʀᴇᴀᴅʏ ᴏꜰꜰ.", show_alert=True)
            else:
                collection.update_one({"admin_id": user_id}, {"$set": {"maintenance": "off"}})
                await callback_query.answer("ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ ᴍᴏᴅᴇ ᴛᴜʀɴᴇᴅ ᴏꜰꜰ.", show_alert=True)
        else:
            collection.insert_one({"admin_id": user_id, "maintenance": "off"})
            await callback_query.answer("ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ ᴍᴏᴅᴇ ᴛᴜʀɴᴇᴅ ᴏꜰꜰ (ɴᴇᴡ ᴇɴᴛʀʏ).", show_alert=True)

    # Optionally, edit the original message to show current status
    status = collection.find_one({"admin_id": user_id})["maintenance"]
    await callback_query.message.edit_text(
        f"Maintenance mode is now: **{status.upper()}**",
        reply_markup=callback_query.message.reply_markup
    )

