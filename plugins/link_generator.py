from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyromod.exceptions import ListenerTimeout
from helper_func import encode, get_message_id
from database.database import is_admin, get_global_db_channel

@Client.on_message(filters.command(["genlink", "batch"]) & filters.private)
async def link_generator(client: Client, message: Message):
    user_id = message.from_user.id
    if not await is_admin(user_id):
        return await message.reply_text("⚠️ <b>ᴀᴄᴄᴇꜱꜱ ᴅᴇɴɪᴇᴅ!</b> ᴀᴅᴍɪɴꜱ ᴏɴʟʏ.")

    db_chat_id = await get_global_db_channel()
    cmd = message.command[0]

    if cmd == "genlink":
        prompt_msg = await message.reply_text("<b>ꜰᴏʀᴡᴀʀᴅ ᴍᴇꜱꜱᴀɢᴇ ꜰʀᴏᴍ ʏᴏᴜʀ ᴅʙ ᴄʜᴀɴɴᴇʟ (ᴏʀ ꜱᴇɴᴅ ʟɪɴᴋ):</b>\n\n/cancel - ᴄᴀɴᴄᴇʟ.")
        try:
            r_msg = await client.listen(chat_id=message.chat.id, filters=filters.private & filters.user(user_id), timeout=60)
        except ListenerTimeout:
            await prompt_msg.delete()
            return await message.reply_text("⌛ <b>ᴛɪᴍᴇᴏᴜᴛ! ᴘʀᴏᴄᴇꜱꜱ ᴄᴀɴᴄᴇʟʟᴇᴅ.</b>")
            
        if not r_msg:
            await prompt_msg.delete()
            return
            
        text_content = r_msg.text or r_msg.caption or ""
        
        if text_content.lower() == "/cancel":
            await prompt_msg.delete()
            return await r_msg.reply_text("❌ <b>ᴘʀᴏᴄᴇꜱꜱ ᴄᴀɴᴄᴇʟʟᴇᴅ!</b>")

        msg_id = await get_message_id(client, r_msg, db_chat_id)
        
        # Delete the bot's prompt message after getting the input (without deleting the user's message)
        try:
            await prompt_msg.delete()
        except:
            pass

        if not msg_id:
            return await r_msg.reply_text("❌ <b>ɪɴᴠᴀʟɪᴅ ᴍᴇꜱꜱᴀɢᴇ!</b> ᴍᴜꜱᴛ ʙᴇ ꜰᴏʀᴡᴀʀᴅᴇᴅ ꜰʀᴏᴍ ᴛʜᴇ ᴄᴏʀʀᴇᴄᴛ ᴅʙ ᴄʜᴀɴɴᴇʟ.")
        
        base64_string = await encode(f"get-{msg_id * abs(db_chat_id)}")
        link = f"https://t.me/{client.username}?start={base64_string}"
        
        text = (
            "🎉 ʏᴏᴜʀ ꜱʜᴀʀᴇᴀʙʟᴇ ꜰɪʟᴇ ʟɪɴᴋ ɪꜱ ʀᴇᴀᴅʏ!\n"
            "🔗 ᴄʟɪᴄᴋ ᴛʜᴇ ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ ᴛᴏ ꜱʜᴀʀᴇ ɪᴛ.\n\n"
            "ᴛʜᴀɴᴋ ʏᴏᴜ ꜰᴏʀ ʙᴇɪɴɢ ᴘᴀʀᴛ ᴏꜰ ᴛɪᴛᴀɴᴄɪɴᴇᴘʟᴇx! 🚀"
        )
        markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 Share URL ↗", url=f"https://t.me/share/url?url={link}")],
            [InlineKeyboardButton("🔗 Open Link ↗", url=link)]
        ])
        await r_msg.reply_text(text, reply_markup=markup, disable_web_page_preview=True)

    elif cmd == "batch":
        prompt1 = await message.reply_text("<b>ꜰᴏʀᴡᴀʀᴅ ᴛʜᴇ *ꜰɪʀꜱᴛ* ᴍᴇꜱꜱᴀɢᴇ ꜰʀᴏᴍ ᴛʜᴇ ᴅʙ ᴄʜᴀɴɴᴇʟ:</b>\n\n/cancel - ᴄᴀɴᴄᴇʟ.")
        try:
            first_msg = await client.listen(chat_id=message.chat.id, filters=filters.private & filters.user(user_id), timeout=60)
        except ListenerTimeout:
            await prompt1.delete()
            return await message.reply_text("⌛ <b>ᴛɪᴍᴇᴏᴜᴛ! ᴘʀᴏᴄᴇꜱꜱ ᴄᴀɴᴄᴇʟʟᴇᴅ.</b>")
        
        try: await prompt1.delete()
        except: pass

        if not first_msg: return
        first_text = first_msg.text or first_msg.caption or ""
        if first_text.lower() == "/cancel":
            return await first_msg.reply_text("❌ <b>ᴘʀᴏᴄᴇꜱꜱ ᴄᴀɴᴄᴇʟʟᴇᴅ!</b>")

        first_id = await get_message_id(client, first_msg, db_chat_id)
        
        prompt2 = await message.reply_text("<b>ꜰᴏʀᴡᴀʀᴅ ᴛʜᴇ *ʟᴀꜱᴛ* ᴍᴇꜱꜱᴀɢᴇ ꜰʀᴏᴍ ᴛʜᴇ ᴅʙ ᴄʜᴀɴɴᴇʟ:</b>\n\n/cancel - ᴄᴀɴᴄᴇʟ.")
        try:
            second_msg = await client.listen(chat_id=message.chat.id, filters=filters.private & filters.user(user_id), timeout=60)
        except ListenerTimeout:
            await prompt2.delete()
            return await message.reply_text("⌛ <b>ᴛɪᴍᴇᴏᴜᴛ! ᴘʀᴏᴄᴇꜱꜱ ᴄᴀɴᴄᴇʟʟᴇᴅ.</b>")
        
        try: await prompt2.delete()
        except: pass

        if not second_msg: return
        second_text = second_msg.text or second_msg.caption or ""
        if second_text.lower() == "/cancel":
            return await second_msg.reply_text("❌ <b>ᴘʀᴏᴄᴇꜱꜱ ᴄᴀɴᴄᴇʟʟᴇᴅ!</b>")

        last_id = await get_message_id(client, second_msg, db_chat_id)
        
        if not first_id or not last_id:
            return await second_msg.reply_text("❌ <b>ɪɴᴠᴀʟɪᴅ ᴍᴇꜱꜱᴀɢᴇꜱ!</b>")
            
        string = f"batch-{first_id * abs(db_chat_id)}-{last_id * abs(db_chat_id)}"
        base64_string = await encode(string)
        link = f"https://t.me/{client.username}?start={base64_string}"
        
        text = (
            "🎉 ʏᴏᴜʀ ʙᴀᴛᴄʜ ꜱʜᴀʀᴇᴀʙʟᴇ ʟɪɴᴋ ɪꜱ ʀᴇᴀᴅʏ!\n"
            "🔗 ᴄʟɪᴄᴋ ᴛʜᴇ ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ ᴛᴏ ꜱʜᴀʀᴇ ɪᴛ.\n\n"
            "ᴛʜᴀɴᴋ ʏᴏᴜ ꜰᴏʀ ʙᴇɪɴɢ ᴘᴀʀᴛ ᴏꜰ ᴛɪᴛᴀɴᴄɪɴᴇᴘʟᴇx! 🚀"
        )
        markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 Share URL ↗", url=f"https://t.me/share/url?url={link}")],
            [InlineKeyboardButton("🔗 Open Link ↗", url=link)]
        ])
        await second_msg.reply_text(text, reply_markup=markup, disable_web_page_preview=True)
        
