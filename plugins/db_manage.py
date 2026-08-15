import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyromod.exceptions import ListenerTimeout
from helper_func import safe_edit
from database.database import is_admin, db

@Client.on_message(filters.command("delall") & filters.private)
async def delete_all_files(client: Client, message: Message):
    user_id = message.from_user.id
    if not await is_admin(user_id):
        return await message.reply_text("⚠️ <b>ᴀᴄᴄᴇꜱꜱ ᴅᴇɴɪᴇᴅ:</b> ᴀᴅᴍɪɴꜱ ᴏɴʟʏ!")

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ ʏᴇꜱ, ᴅᴇʟᴇᴛᴇ ᴀʟʟ", callback_data="confirm_delall"),
            InlineKeyboardButton("❌ ᴄᴀɴᴄᴇʟ", callback_data="cancel_delall")
        ]
    ])
    
    await message.reply_text(
        "⚠️ <b>ᴡᴀʀɴɪɴɢ:</b> ʏᴏᴜ ᴀʀᴇ ᴀʙᴏᴜᴛ ᴛᴏ ᴅᴇʟᴇᴛᴇ <b>ᴀʟʟ ꜰɪʟᴇꜱ</b> ꜰʀᴏᴍ ᴛʜᴇ ᴅᴀᴛᴀʙᴀꜱᴇ!\n\n"
        "ᴛʜɪꜱ ᴀᴄᴛɪᴏɴ ᴄᴀɴɴᴏᴛ ʙᴇ ᴜɴᴅᴏɴᴇ. ᴀʀᴇ ʏᴏᴜ ꜱᴜʀᴇ?",
        reply_markup=keyboard
    )

@Client.on_callback_query(filters.regex(r"^(confirm|cancel)_delall$"))
async def confirm_delall_cb(client: Client, query):
    if not await is_admin(query.from_user.id):
        return await query.answer("⚠️ ᴀᴄᴄᴇꜱꜱ ᴅᴇɴɪᴇᴅ!", show_alert=True)
        
    data = query.data
    if data == "cancel_delall":
        return await safe_edit(query.message, "❌ <b>ᴏᴘᴇʀᴀᴛɪᴏɴ ᴄᴀɴᴄᴇʟʟᴇᴅ.</b> ɴᴏ ꜰɪʟᴇꜱ ᴡᴇʀᴇ ᴅᴇʟᴇᴛᴇᴅ.")
        
    try:
        await db.media.drop()
        await safe_edit(query.message, "✅ <b>ꜱᴜᴄᴄᴇꜱꜱ!</b> ᴀʟʟ ꜰɪʟᴇꜱ ʜᴀᴠᴇ ʙᴇᴇɴ ᴅᴇʟᴇᴛᴇᴅ ꜰʀᴏᴍ ᴛʜᴇ ᴅᴀᴛᴀʙᴀꜱᴇ.")
    except Exception as e:
        await safe_edit(query.message, f"❌ <b>ᴇʀʀᴏʀ ᴅᴇʟᴇᴛɪɴɢ ꜰɪʟᴇꜱ:</b> {e}")

@Client.on_message(filters.command("delfile") & filters.private)
async def delete_specific_file(client: Client, message: Message):
    user_id = message.from_user.id
    if not await is_admin(user_id):
        return await message.reply_text("⚠️ <b>ᴀᴄᴄᴇꜱꜱ ᴅᴇɴɪᴇᴅ:</b> ᴀᴅᴍɪɴꜱ ᴏɴʟʏ!")

    try:
        ask_msg = await client.ask(
            message.chat.id, 
            "🗑 <b>ᴅᴇʟᴇᴛᴇ ꜱᴘᴇᴄɪꜰɪᴄ ꜰɪʟᴇ</b>\n\n"
            "ꜱᴇɴᴅ ᴛʜᴇ ꜰɪʟᴇ ɪᴅ ᴏʀ ᴍᴇꜱꜱᴀɢᴇ ɪᴅ ᴛᴏ ᴅᴇʟᴇᴛᴇ ɪᴛ ꜰʀᴏᴍ ᴛʜᴇ ᴅᴀᴛᴀʙᴀꜱᴇ.\n\n"
            "/cancel - ᴄᴀɴᴄᴇʟ.", 
            timeout=60
        )
    except ListenerTimeout:
        return await message.reply_text("⌛ <b>ᴛɪᴍᴇᴏᴜᴛ! ᴘʀᴏᴄᴇꜱꜱ ᴄᴀɴᴄᴇʟʟᴇᴅ.</b>")

    text = ask_msg.text or ""
    try: await ask_msg.delete()
    except: pass

    if not text or text.lower() == "/cancel":
        return await message.reply_text("❌ <b>ᴘʀᴏᴄᴇꜱꜱ ᴄᴀɴᴄᴇʟʟᴇᴅ!</b>")

    try:
        result = await db.media.delete_one({"file_id": text})
        
        if result.deleted_count > 0:
            await message.reply_text(f"✅ <b>ꜱᴜᴄᴄᴇꜱꜱ!</b> ꜰɪʟᴇ ᴡɪᴛʜ ɪᴅ <code>{text}</code> ʜᴀꜱ ʙᴇᴇɴ ᴅᴇʟᴇᴛᴇᴅ.")
        else:
            await message.reply_text(f"❌ <b>ɴᴏᴛ ꜰᴏᴜɴᴅ!</b> ɴᴏ ꜰɪʟᴇ ᴡɪᴛʜ ɪᴅ <code>{text}</code> ᴡᴀꜱ ꜰᴏᴜɴᴅ ɪɴ ᴛʜᴇ ᴅᴀᴛᴀʙᴀꜱᴇ.")
    except Exception as e:
        await message.reply_text(f"❌ <b>ᴇʀʀᴏʀ:</b> {e}")
        
