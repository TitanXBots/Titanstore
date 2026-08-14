import asyncio
import time
from pyrogram import Client, filters
from pyrogram.types import Message
from database.database import get_all_users, is_admin

@Client.on_message(filters.command("broadcast") & filters.private)
async def broadcast_handler(client: Client, message: Message):
    if not await is_admin(message.from_user.id):
        return await message.reply_text("⚠️ ᴀᴄᴄᴇꜱꜱ ᴅᴇɴɪᴇᴅ!")
        
    if not message.reply_to_message:
        return await message.reply_text("<b>ᴘʟᴇᴀꜱᴇ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇꜱꜱᴀɢᴇ ᴛᴏ ʙʀᴏᴀᴅᴄᴀꜱᴛ.</b>")
        
    users = await get_all_users()
    broadcast_msg = message.reply_to_message
    
    status_msg = await message.reply_text("<b>📢 ʙʀᴏᴀᴅᴄᴀꜱᴛ ɪɴ ᴘʀᴏɢʀᴇꜱꜱ...</b>")
    start_time = time.time()
    
    success, failed, total = 0, 0, len(users)
    
    for user_id in users:
        try:
            await broadcast_msg.copy(chat_id=user_id)
            success += 1
        except Exception:
            failed += 1
        await asyncio.sleep(0.1)
        
    elapsed = time.time() - start_time
    await status_msg.edit_text(
        f"<b>📢 ʙʀᴏᴀᴅᴄᴀꜱᴛ ᴄᴏᴍᴘʟᴇᴛᴇᴅ!</b>\n\n"
        f"👥 <b>ᴛᴏᴛᴀʟ:</b> <code>{total}</code>\n"
        f"✅ <b>ꜱᴜᴄᴄᴇꜱꜱ:</b> <code>{success}</code>\n"
        f"❌ <b>ꜰᴀɪʟᴇᴅ:</b> <code>{failed}</code>\n"
        f"⏱ <b>ᴛɪᴍᴇ:</b> <code>{int(elapsed)}s</code>"
    )
    
