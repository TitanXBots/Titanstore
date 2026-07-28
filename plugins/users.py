from pyrogram import Client, filters
from pyrogram.types import Message
from database.database import is_admin, get_all_users

@Client.on_message(filters.command("users") & filters.private)
async def check_users_command(client: Client, message: Message):
    if not await is_admin(message.from_user.id):
        return await message.reply_text("⚠️ ᴀᴄᴄᴇꜱꜱ ᴅᴇɴɪᴇᴅ: ᴀᴅᴍɪɴꜱ ᴏɴʟʏ!")
        
    loading_msg = await message.reply_text("⏳ ꜰᴇᴛᴄʜɪɴɢ ᴜꜱᴇʀ ᴅᴀᴛᴀ...")
    users = await get_all_users()
    
    await loading_msg.edit_text(
        f"📊 **ʙᴏᴛ ꜱᴛᴀᴛɪꜱᴛɪᴄꜱ**\n\n"
        f"👥 **ᴛᴏᴛᴀʟ ʀᴇɢɪꜱᴛᴇʀᴇᴅ ᴜꜱᴇʀꜱ:** `{len(users)}`"
    )
