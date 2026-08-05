from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from config import START_PIC, OWNER_ID
from database.database import is_premium

PLAN_PIC = "https://envs.sh/WeX.jpg" 
QR_PIC = "https://envs.sh/TPh.jpg" 

@Client.on_message(filters.command("plan") & filters.private)
async def plan_command(client: Client, message: Message):
    first_name = message.from_user.first_name or "User"
    caption = (
        f"👋 ʜᴇʏ <b>{first_name}</b>,\n\n"
        f"🎁 <b>ᴘʀᴇᴍɪᴜᴍ ꜰᴇᴀᴛᴜʀᴇ ʙᴇɴᴇꜰɪᴛꜱ:</b>\n\n"
        f"☑️ ɴᴏ ɴᴇᴇᴅ ᴛᴏ ᴏᴘᴇɴ ʟɪɴᴋꜱ\n"
        f"☑️ ɢᴇᴛ ᴅɪʀᴇᴄᴛ ꜰɪʟᴇꜱ\n"
        f"☑️ ᴀᴅ-ꜰʀᴇᴇ ᴇxᴘᴇʀɪᴇɴᴄᴇ\n"
        f"☑️ ʜɪɢʜ-ꜱᴘᴇᴇᴅ ᴅᴏᴡɴʟᴏᴀᴅ ʟɪɴᴋ\n"
        f"☑️ ᴍᴜʟᴛɪ-ᴘʟᴀʏᴇʀ ꜱᴛʀᴇᴀᴍɪɴɢ ʟɪɴᴋꜱ\n"
        f"☑️ ᴜɴʟɪᴍɪᴛᴇᴅ ᴍᴏᴠɪᴇꜱ ᴀɴᴅ ꜱᴇʀɪᴇꜱ\n"
        f"☑️ ꜰᴜʟʟ ᴀᴅᴍɪɴ ꜱᴜᴘᴘᴏʀᴛ\n"
        f"☑️ ʀᴇǫᴜᴇꜱᴛ ᴡɪʟʟ ʙᴇ ᴄᴏᴍᴘʟᴇᴛᴇᴅ ɪɴ 1ʜ [ ɪꜰ ᴀᴠᴀɪʟᴀʙʟᴇ ]\n\n"
        f"🥤 ᴄʜᴇᴄᴋ ʏᴏᴜʀ ᴀᴄᴛɪᴠᴇ ᴘʟᴀɴ: /myplan"
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🎁 ᴏᴛʜᴇʀ ᴘʟᴀɴ / ᴄᴜꜱᴛᴏᴍɪꜱᴇᴅ ᴅᴀʏꜱ", callback_data="custom_plan")],
        [InlineKeyboardButton("« ʙᴀᴄᴋ ᴛᴏ ʜᴏᴍᴇ", callback_data="start")]
    ])
    await message.reply_photo(photo=PLAN_PIC, caption=caption, reply_markup=keyboard)

@Client.on_message(filters.command("myplan") & filters.private)
async def myplan_command(client: Client, message: Message):
    user_id = message.from_user.id
    is_prem = await is_premium(user_id)
    if is_prem:
        text = "💎 <b>ʏᴏᴜ ᴀʀᴇ ᴀ ᴘʀᴇᴍɪᴜᴍ ᴍᴇᴍʙᴇʀ!</b>\n\nʏᴏᴜ ʜᴀᴠᴇ ᴜɴʟɪᴍɪᴛᴇᴅ ᴀᴄᴄᴇꜱꜱ ᴛᴏ ᴘʀᴇᴍɪᴜᴍ ꜰᴇᴀᴛᴜʀᴇꜱ."
    else:
        text = "🆓 <b>ʏᴏᴜ ᴀʀᴇ ᴏɴ ᴛʜᴇ ꜰʀᴇᴇ ᴘʟᴀɴ.</b>\n\nᴜꜱᴇ /plan ᴛᴏ ᴠɪᴇᴡ ᴘʀᴇᴍɪᴜᴍ ʙᴇɴᴇꜰɪᴛꜱ ᴀɴᴅ ᴜᴘɢʀᴀᴅᴇ!"
    await message.reply_text(text)

@Client.on_callback_query(filters.regex("^(buy_plans|custom_plan|plan_home)$"))
async def plans_cb(client: Client, query: CallbackQuery):
    user_id = query.from_user.id
    first_name = query.from_user.first_name or "User"
    data = query.data

    if data in ["buy_plans", "plan_home"]:
        caption = (
            f"👋 ʜᴇʏ <b>{first_name}</b>,\n\n"
            f"🎁 <b>ᴘʀᴇᴍɪᴜᴍ ꜰᴇᴀᴛᴜʀᴇ ʙᴇɴᴇꜰɪᴛꜱ:</b>\n\n"
            f"☑️ ɴᴏ ɴᴇᴇᴅ ᴛᴏ ᴏᴘᴇɴ ʟɪɴᴋꜱ\n"
            f"☑️ ɢᴇᴛ ᴅɪʀᴇᴄᴛ ꜰɪʟᴇꜱ\n"
            f"☑️ ᴀᴅ-ꜰʀᴇᴇ ᴇxᴘᴇʀɪᴇɴᴄᴇ\n"
            f"☑️ ʜɪɢʜ-ꜱᴘᴇᴇᴅ ᴅᴏᴡɴʟᴏᴀᴅ ʟɪɴᴋ\n"
            f"☑️ ᴍᴜʟᴛɪ-ᴘʟᴀʏᴇʀ ꜱᴛʀᴇᴀᴍɪɴɢ ʟɪɴᴋꜱ\n"
            f"☑️ ᴜɴʟɪᴍɪᴛᴇᴅ ᴍᴏᴠɪᴇꜱ ᴀɴᴅ ꜱᴇʀɪᴇꜱ\n"
            f"☑️ ꜰᴜʟʟ ᴀᴅᴍɪɴ ꜱᴜᴘᴘᴏʀᴛ\n"
            f"☑️ ʀᴇǫᴜᴇꜱᴛ ᴡɪʟʟ ʙᴇ ᴄᴏᴍᴘʟᴇᴛᴇᴅ ɪɴ 1ʜ [ ɪꜰ ᴀᴠᴀɪʟᴀʙʟᴇ ]\n\n"
            f"🥤 ᴄʜᴇᴄᴋ ʏᴏᴜʀ ᴀᴄᴛɪᴠᴇ ᴘʟᴀɴ: /myplan"
        )
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🎁 ᴏᴛʜᴇʀ ᴘʟᴀɴ / ᴄᴜꜱᴛᴏᴍɪꜱᴇᴅ ᴅᴀʏꜱ", callback_data="custom_plan")],
            [InlineKeyboardButton("« ʙᴀᴄᴋ ᴛᴏ ʜᴏᴍᴇ", callback_data="start")]
        ])
        try:
            if query.message.photo:
                await query.message.edit_caption(caption=caption, reply_markup=keyboard)
            else:
                await query.message.delete()
                await client.send_photo(chat_id=user_id, photo=PLAN_PIC, caption=caption, reply_markup=keyboard)
        except Exception:
            await client.send_photo(chat_id=user_id, photo=PLAN_PIC, caption=caption, reply_markup=keyboard)

    elif data == "custom_plan":
        caption = (
            f"👋 ʜᴇʏ <b>{first_name}</b>,\n\n"
            f"🎁 <b>ᴏᴛʜᴇʀ ᴘʟᴀɴ</b>\n"
            f"⏰ <b>ᴄᴜꜱᴛᴏᴍɪꜱᴇᴅ ᴅᴀʏꜱ</b>\n"
            f"🪩 <b>ᴀᴄᴄᴏʀᴅɪɴɢ ᴛᴏ ᴅᴀʏꜱ ʏᴏᴜ ᴄʜᴏᴏꜱᴇ</b>\n\n"
            f"🏆 <b>ɪꜰ ʏᴏᴜ ᴡᴀɴᴛ ᴀ ɴᴇᴡ ᴘʟᴀɴ ᴀᴘᴀʀᴛ ꜰʀᴏᴍ ᴛＨᴇ ɢɪᴠᴇɴ ᴘʟᴀɴ, ᴛʜᴇɴ ʏᴏᴜ ᴄᴀɴ ᴛᴀʟᴋ ᴛᴏ ᴏᴜʀ ᴏᴡɴᴇʀ ᴅɪʀᴇᴄᴛʟʏ ʙʏ ᴄʟɪᴄᴋɪɴɢ ᴏɴ ᴛʜᴇ ᴄᴏɴᴛᴀᴄᴛ ʙᴜᴛᴛᴏɴ ɢɪᴠᴇɴ ʙᴇʟᴏᴡ.</b>\n\n"
            f"👩‍💻 <b>ᴄᴏɴᴛᴀᴄᴛ ᴛʜᴇ ᴏᴡɴᴇʀ ᴛᴏ ɢᴇᴛ ʏᴏᴜʀ ᴏᴛʜᴇʀ ᴘʟᴀɴ.</b>\n\n"
            f"➛ ᴜꜱᴇ /plan ᴛᴏ ꜱᴇᴇ ᴀʟʟ ᴏᴜʀ ᴘʟᴀɴꜱ ᴀᴛ ᴏɴᴄᴇ.\n"
            f"➛ ᴄʜᴇᴄᴋ ʏᴏᴜʀ ᴀᴄᴛɪᴠᴇ ᴘʟᴀɴ ʙʏ ᴜꜱɪɴɢ: /myplan"
        )
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📱 ᴄᴏɴᴛᴀᴄᴛ ᴛᴏ ᴏᴡɴᴇʀ", url=f"tg://user?id={OWNER_ID}")],
            [InlineKeyboardButton("• ʙᴀᴄᴋ •", callback_data="buy_plans")]
        ])
        try:
            if query.message.photo:
                await query.message.edit_caption(caption=caption, reply_markup=keyboard)
            else:
                await query.message.delete()
                await client.send_photo(chat_id=user_id, photo=QR_PIC, caption=caption, reply_markup=keyboard)
        except Exception:
            await client.send_photo(chat_id=user_id, photo=QR_PIC, caption=caption, reply_markup=keyboard)
          
