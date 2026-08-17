from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyromod.exceptions import ListenerTimeout
from helper_func import encode, get_message_id
from database.database import is_admin, get_global_db_channel, get_premium_status, get_user_approved_channels

@Client.on_message(filters.command(["genlink", "batch"]) & filters.private)
async def link_generator(client: Client, message: Message):
    user_id = message.from_user.id
    is_adm = await is_admin(user_id)
    is_prem = await get_premium_status(user_id)
    
    if not (is_adm or is_prem):
        return await message.reply_text("⚠️ <b>ᴀᴄᴄᴇꜱꜱ ᴅᴇɴɪᴇᴅ!</b> ᴀᴅᴍɪɴꜱ ᴏʀ ᴘʀᴇᴍɪᴜᴍ ᴜꜱᴇʀꜱ ᴏɴʟʏ.")

    if is_prem and not is_adm:
        user_db = await get_user_approved_channels(user_id, "db")
        if not user_db:
            return await message.reply_text("❌ <b>ʏᴏᴜ ᴅᴏ ɴᴏᴛ ʜᴀᴠᴇ ᴀɴ ᴀᴘᴘʀᴏᴠᴇᴅ ᴅʙ ᴄʜᴀɴɴᴇʟ.</b>\nꜱᴇᴛᴜᴘ ᴜꜱɪɴɢ 'ᴍʏ ᴀᴄᴄᴏᴜɴᴛ' ʙᴜᴛᴛᴏɴ ᴏʀ /plan")
        db_chat_id = user_db[0]
    else:
        db_chat_id = await get_global_db_channel()

    cmd = message.command[0]

    if cmd == "genlink":
        prompt_msg = await message.reply_text("<b>ꜰᴏʀᴡᴀʀᴅ ᴍᴇꜱꜱᴀɢᴇ ꜰʀᴏᴍ ʏᴏᴜʀ ᴅʙ ᴄʜᴀɴɴᴇʟ:</b>\n\n/cancel - ᴄᴀɴᴄᴇʟ.")
        try:
            # FIX: Removed filters.user()
            r_msg = await client.listen(chat_id=message.chat.id, timeout=60)
        except ListenerTimeout: 
            return await message.reply_text("⌛ <b>ᴛɪᴍᴇᴏᴜᴛ! ᴘʀᴏᴄᴇꜱꜱ ᴄᴀɴᴄᴇʟʟᴇᴅ.</b>")
            
        if not r_msg: return
        text_content = r_msg.text or r_msg.caption or ""
        if text_content.lower() == "/cancel": return await r_msg.reply_text("❌ <b>ᴘʀᴏᴄᴇꜱꜱ ᴄᴀɴᴄᴇʟʟᴇᴅ!</b>")

        msg_id = await get_message_id(client, r_msg, db_chat_id)
        if not msg_id: return await r_msg.reply_text("❌ <b>ɪɴᴠᴀʟɪᴅ ᴍᴇꜱꜱᴀɢᴇ!</b> ᴍᴜꜱᴛ ʙᴇ ꜰᴏʀᴡᴀʀᴅᴇᴅ ꜰʀᴏᴍ ᴛʜᴇ ᴄᴏʀʀᴇᴄᴛ ᴅʙ ᴄʜᴀɴɴᴇʟ.")
        
        payload_str = f"get-{msg_id * abs(db_chat_id)}"
        if is_prem and not is_adm: payload_str += f"-{user_id}"
        
        link = f"https://t.me/{client.me.username}?start={await encode(payload_str)}"
        
        markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔄 Share URL ↗", url=f"https://t.me/share/url?url={link}")], [InlineKeyboardButton("🔗 Open Link ↗", url=link)]])
        await r_msg.reply_text("🎉 ʏᴏᴜʀ ꜱʜᴀʀᴇᴀʙʟᴇ ꜰɪʟᴇ ʟɪɴᴋ ɪꜱ ʀᴇᴀᴅʏ!\n🔗 ᴄʟɪᴄᴋ ᴛʜᴇ ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ ᴛᴏ ꜱʜᴀʀᴇ ɪᴛ.", reply_markup=markup, disable_web_page_preview=True)

    elif cmd == "batch":
        prompt1 = await message.reply_text("<b>ꜰᴏʀᴡᴀʀᴅ ᴛʜᴇ *ꜰɪʀꜱᴛ* ᴍᴇꜱꜱᴀɢᴇ:</b>\n\n/cancel - ᴄᴀɴᴄᴇʟ.")
        try: 
            # FIX: Removed filters.user()
            first_msg = await client.listen(chat_id=message.chat.id, timeout=60)
        except ListenerTimeout: 
            return await message.reply_text("⌛ <b>ᴛɪᴍᴇᴏᴜᴛ!</b>")
            
        if not first_msg or (first_msg.text or "").lower() == "/cancel": return await message.reply_text("❌ <b>ᴄᴀɴᴄᴇʟʟᴇᴅ!</b>")
        first_id = await get_message_id(client, first_msg, db_chat_id)
        
        prompt2 = await message.reply_text("<b>ꜰᴏʀᴡᴀʀᴅ ᴛʜᴇ *ʟᴀꜱᴛ* ᴍᴇꜱꜱᴀɢᴇ:</b>\n\n/cancel - ᴄᴀɴᴄᴇʟ.")
        try: 
            # FIX: Removed filters.user()
            second_msg = await client.listen(chat_id=message.chat.id, timeout=60)
        except ListenerTimeout: 
            return await message.reply_text("⌛ <b>ᴛɪᴍᴇᴏᴜᴛ!</b>")
            
        if not second_msg or (second_msg.text or "").lower() == "/cancel": return await message.reply_text("❌ <b>ᴄᴀɴᴄᴇʟʟᴇᴅ!</b>")
        last_id = await get_message_id(client, second_msg, db_chat_id)
        
        if not first_id or not last_id: return await second_msg.reply_text("❌ <b>ɪɴᴠᴀʟɪᴅ ᴍᴇꜱꜱᴀɢᴇꜱ!</b>")
            
        payload_str = f"batch-{first_id * abs(db_chat_id)}-{last_id * abs(db_chat_id)}"
        if is_prem and not is_adm: payload_str += f"-{user_id}"
        
        link = f"https://t.me/{client.me.username}?start={await encode(payload_str)}"
        
        markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔄 Share URL ↗", url=f"https://t.me/share/url?url={link}")], [InlineKeyboardButton("🔗 Open Link ↗", url=link)]])
        await second_msg.reply_text("🎉 ʏᴏᴜʀ ʙᴀᴛᴄʜ ꜱʜᴀʀᴇᴀʙʟᴇ ʟɪɴᴋ ɪꜱ ʀᴇᴀᴅʏ!\n🔗 ᴄʟɪᴄᴋ ᴛʜᴇ ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ ᴛᴏ ꜱʜᴀʀᴇ ɪᴛ.", reply_markup=markup, disable_web_page_preview=True)
        
