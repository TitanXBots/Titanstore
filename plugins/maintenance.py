from pyrogram import Client, filters
from pyrogram.types import Message
from database.database import maintenance_collection, is_admin

@Client.on_message(filters.command("maintenance") & filters.private)
async def maintenance_toggle_command(client: Client, message: Message):
    if not await is_admin(message.from_user.id): return await message.reply_text("⚠️ ᴀᴄᴄᴇꜱꜱ ᴅᴇɴɪᴇᴅ: ᴀᴅᴍɪɴꜱ ᴏɴʟʏ!")

    if len(message.command) != 2:
        return await message.reply_text("<b>Usage:</b>\n`/maintenance on`\n`/maintenance off`")
    arg = message.command[1].lower()
    if arg not in ("on", "off"):
        return await message.reply_text("❌ ɪɴᴠᴀʟɪᴅ ᴀʀɢᴜᴍᴇɴᴛ. ᴜꜱᴇ ᴏɴʟʏ `on` or `off`.")

    await maintenance_collection.update_one({"_id": "maintenance"}, {"$set": {"maintenance": arg}}, upsert=True)
    if arg == "on": await message.reply_text("✅ ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ ᴍᴏᴅᴇ ᴇɴᴀʙʟᴇᴅ. ᴛʜᴇ ʙᴏᴛ ɪꜱ ᴄᴜʀʀᴇɴᴛʟʏ ᴜɴᴅᴇʀ ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ. ᴜꜱᴇʀꜱ ᴄᴀɴɴᴏᴛ ᴜꜱᴇ ᴛʜᴇ ʙᴏᴛ ᴀᴛ ᴛʜɪꜱ ᴛɪᴍᴇ.")
    else: await message.reply_text("⚙️ ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ ᴍᴏᴅᴇ ʜᴀꜱ ʙᴇᴇɴ ᴅɪꜱᴀʙʟᴇᴅ. ᴛʜᴇ ʙᴏᴛ ɪꜱ ɴᴏᴡ ᴀᴠᴀɪʟᴀʙʟᴇ ᴛᴏ ᴀʟʟ ᴜꜱᴇʀꜱ.")
        
