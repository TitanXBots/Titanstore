import math
from pyrogram import Client, filters
from pyrogram.types import Message
from helper_func import encode, get_message_id
from database.database import is_admin, get_global_db_channel, get_tenant_config

@Client.on_message(filters.command(["genlink", "batch"]) & filters.private)
async def link_generator(client: Client, message: Message):
    user_id = message.from_user.id
    if not await is_admin(user_id):
        # Allow tenants if they are premium
        tenant = await get_tenant_config(user_id)
        if not tenant:
            return await message.reply_text("⚠️ ᴀᴄᴄᴇꜱꜱ ᴅᴇɴɪᴇᴅ! ᴀᴅᴍɪɴꜱ ᴏʀ ᴘʀᴇᴍɪᴜᴍ ᴛᴇɴᴀɴᴛꜱ ᴏɴʟʏ.")

    db_chat_id = get_global_db_channel()
    if user_id != client.owner_id if hasattr(client, 'owner_id') else True:
        tenant = await get_tenant_config(user_id)
        if tenant:
            db_chat_id = tenant["db_channel"]

    cmd = message.command[0]

    if cmd == "genlink":
        r_msg = await client.ask(message.chat.id, "<b>ꜰᴏʀᴡᴀʀᴅ ᴍᴇꜱꜱᴀɢᴇ ꜰʀᴏᴍ ʏᴏᴜʀ ᴅʙ ᴄʜᴀɴɴᴇʟ (ᴏʀ ꜱᴇɴᴅ ʟɪɴᴋ):</b>", timeout=60)
        if not r_msg: return
        msg_id = await get_message_id(client, r_msg, db_chat_id)
        if not msg_id:
            return await message.reply_text("❌ <b>ɪɴᴠᴀʟɪᴅ ᴍᴇꜱꜱᴀɢᴇ!</b> ᴍᴜꜱᴛ ʙᴇ ꜰᴏʀᴡᴀʀᴅᴇᴅ ꜰʀᴏᴍ ᴛʜᴇ ᴄᴏʀʀᴇᴄᴛ ᴅʙ ᴄʜᴀɴɴᴇʟ.")
        
        owner_prefix = f"_{user_id}_" if user_id != client.owner_id else ""
        base64_string = await encode(f"get{owner_prefix}-{msg_id * abs(db_chat_id)}")
        link = f"https://t.me/{client.username}?start={base64_string}"
        await message.reply_text(f"✅ <b>ʜᴇʀᴇ ɪꜱ ʏᴏᴜʀ ʟɪɴᴋ:</b>\n\n<code>{link}</code>")

    elif cmd == "batch":
        try:
            first_msg = await client.ask(message.chat.id, "<b>ꜰᴏʀᴡᴀʀᴅ ᴛʜᴇ *ꜰɪʀꜱᴛ* ᴍᴇꜱꜱᴀɢᴇ ꜰʀᴏᴍ ᴛʜᴇ ᴅʙ ᴄʜᴀɴɴᴇʟ:</b>", timeout=60)
            first_id = await get_message_id(client, first_msg, db_chat_id)
            
            second_msg = await client.ask(message.chat.id, "<b>ꜰᴏʀᴡᴀʀᴅ ᴛʜᴇ *ʟᴀꜱᴛ* ᴍᴇꜱꜱᴀɢᴇ ꜰʀᴏᴍ ᴛʜᴇ ᴅʙ ᴄʜᴀɴɴᴇʟ:</b>", timeout=60)
            last_id = await get_message_id(client, second_msg, db_chat_id)
            
            if not first_id or not last_id:
                return await message.reply_text("❌ <b>ɪɴᴠᴀʟɪᴅ ᴍᴇꜱꜱᴀɢᴇꜱ!</b>")
                
            owner_prefix = f"_{user_id}_" if user_id != client.owner_id else ""
            string = f"batch{owner_prefix}-{first_id * abs(db_chat_id)}-{last_id * abs(db_chat_id)}"
            base64_string = await encode(string)
            link = f"https://t.me/{client.username}?start={base64_string}"
            await message.reply_text(f"✅ <b>ʜᴇʀᴇ ɪꜱ ʏᴏᴜʀ ʙᴀᴛᴄʜ ʟɪɴᴋ:</b>\n\n<code>{link}</code>")
        except Exception as e:
            await message.reply_text(f"❌ <b>ᴇʀʀᴏʀ:</b> {e}")
            
