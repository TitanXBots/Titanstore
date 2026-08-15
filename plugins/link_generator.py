from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyromod.exceptions import ListenerTimeout
from helper_func import encode, get_message_id
from database.database import is_admin, get_global_db_channel

@Client.on_message(filters.command(["genlink", "batch"]) & filters.private)
async def link_generator(client: Client, message: Message):
    user_id = message.from_user.id
    if not await is_admin(user_id):
        return await message.reply_text("⚠️ ᴀᴄᴄᴇꜱꜱ ᴅᴇɴɪᴇᴅ! ᴀᴅᴍɪɴꜱ ᴏɴʟʏ.")

    db_chat_id = await get_global_db_channel()
    cmd = message.command[0]

    if cmd == "genlink":
        try:
            r_msg = await client.ask(message.chat.id, "<b>ꜰᴏʀᴡᴀʀᴅ ᴍᴇꜱꜱᴀɢᴇ ꜰʀᴏᴍ ʏᴏᴜʀ ᴅʙ ᴄʜᴀɴɴᴇʟ (ᴏʀ ꜱᴇɴᴅ ʟɪɴᴋ):</b>\n\n/cancel - ᴄᴀɴᴄᴇʟ.", timeout=60)
        except ListenerTimeout:
            return await message.reply_text("⌛ <b>ᴛɪᴍᴇᴏᴜᴛ! ᴘʀᴏᴄᴇꜱꜱ ᴄᴀɴᴄᴇʟʟᴇᴅ.</b>")
            
        if not r_msg: return
        text_content = r_msg.text or r_msg.caption or ""
        try: await r_msg.delete()
        except: pass

        if text_content.lower() == "/cancel":
            return await message.reply_text("❌ <b>ᴘʀᴏᴄᴇꜱꜱ ᴄᴀɴᴄᴇʟʟᴇᴅ!</b>")

        msg_id = await get_message_id(client, r_msg, db_chat_id)
        if not msg_id:
            return await message.reply_text("❌ <b>ɪɴᴠᴀʟɪᴅ ᴍᴇꜱꜱᴀɢᴇ!</b> ᴍᴜꜱᴛ ʙᴇ ꜰᴏʀᴡᴀʀᴅᴇᴅ ꜰʀᴏᴍ ᴛʜᴇ ᴄᴏʀʀᴇᴄᴛ ᴅʙ ᴄʜᴀɴɴᴇʟ.")
        
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
        await message.reply_text(text, reply_markup=markup, disable_web_page_preview=True)

    elif cmd == "batch":
        try:
            first_msg = await client.ask(message.chat.id, "<b>ꜰᴏʀᴡᴀʀᴅ ᴛʜᴇ *ꜰɪʀꜱᴛ* ᴍᴇꜱꜱᴀɢᴇ ꜰʀᴏᴍ ᴛʜᴇ ᴅʙ ᴄʜᴀɴɴᴇʟ:</b>\n\n/cancel - ᴄᴀɴᴄᴇʟ.", timeout=60)
            if not first_msg: return
            first_text = first_msg.text or first_msg.caption or ""
            try: await first_msg.delete()
            except: pass

            if first_text.lower() == "/cancel":
                return await message.reply_text("❌ <b>ᴘʀᴏᴄᴇꜱꜱ ᴄᴀɴᴄᴇʟʟᴇᴅ!</b>")

            first_id = await get_message_id(client, first_msg, db_chat_id)
            
            second_msg = await client.ask(message.chat.id, "<b>ꜰᴏʀᴡᴀʀᴅ ᴛʜᴇ *ʟᴀꜱᴛ* ᴍᴇꜱꜱᴀɢᴇ ꜰʀᴏᴍ ᴛʜᴇ ᴅʙ ᴄʜᴀɴɴᴇʟ:</b>\n\n/cancel - ᴄᴀɴᴄᴇʟ.", timeout=60)
            if not second_msg: return
            second_text = second_msg.text or second_msg.caption or ""
            try: await second_msg.delete()
            except: pass

            if second_text.lower() == "/cancel":
                return await message.reply_text("❌ <b>ᴘʀᴏᴄᴇꜱꜱ ᴄᴀɴᴄᴇʟʟᴇᴅ!</b>")

            last_id = await get_message_id(client, second_msg, db_chat_id)
            
            if not first_id or not last_id:
                return await message.reply_text("❌ <b>ɪɴᴠᴀʟɪᴅ ᴍᴇꜱꜱᴀɢᴇꜱ!</b>")
                
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
            await message.reply_text(text, reply_markup=markup, disable_web_page_preview=True)
        except ListenerTimeout:
            await message.reply_text("⌛ <b>ᴛɪᴍᴇᴏᴜᴛ! ᴘʀᴏᴄᴇꜱꜱ ᴄᴀɴᴄᴇʟʟᴇᴅ.</b>")
        except Exception as e:
            await message.reply_text(f"❌ <b>ᴇʀʀᴏʀ:</b> {e}")
            
