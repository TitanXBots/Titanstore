import asyncio
from pyrogram import filters, Client
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait

from bot import Bot
from config import CHANNEL_ID, DISABLE_CHANNEL_BUTTON, USER_REPLY_TEXT
from helper_func import encode
from database.database import is_admin

# -------------------------------
# PRIVATE MESSAGE HANDLER (ADMINS ONLY)
# -------------------------------
@Bot.on_message(filters.private & ~filters.command([
    'start','users','broadcast','batch','genlink','stats','joinchannels','pypi',
    'restart','settings','joinchannelon','joinchanneloff','admin','autodelete',
    'autodeleteon','autodeleteoff','maintenance','ban','unban','bannedlist',
    'addadmin','removeadmin','adminlist', 'maintenance'
]))
async def channel_post(client: Bot, message: Message):
    user_id = message.from_user.id
    
    # Strictly forward to direct fallback handler if sender is not an authenticated administrator
    if not await is_admin(user_id):
        return

    reply_text = await message.reply_text("Please Wait...!", quote=True)

    # ---------------- COPY TO DB CHANNEL ----------------
    try:
        post_message = await message.copy(
            chat_id=client.db_channel.id,
            disable_notification=True
        )
    except FloodWait as e:
        await asyncio.sleep(e.value)
        post_message = await message.copy(
            chat_id=client.db_channel.id,
            disable_notification=True
        )
    except Exception as e:
        return await reply_text.edit_text(f"Something went wrong: {e}")

    # ---------------- LINK GENERATION ----------------
    converted_id = post_message.id * abs(client.db_channel.id)
    string = f"get-{converted_id}"
    base64_string = await encode(string)
    link = f"https://t.me/{client.username}?start={base64_string}"

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔁 Share URL", url=f"https://telegram.me/share/url?url={link}")]
    ])

    await reply_text.edit_text(
        f"<b>Here is your link</b>\n\n{link}",
        reply_markup=keyboard,
        disable_web_page_preview=True
    )

    # ---------------- ADD BUTTON TO MESSAGE ----------------
    if not DISABLE_CHANNEL_BUTTON:
        try:
            await post_message.edit_reply_markup(keyboard)
        except:
            pass


# -------------------------------
# CHANNEL AUTO BUTTON SYSTEM
# -------------------------------
@Bot.on_message(filters.channel & filters.incoming & filters.chat(CHANNEL_ID))
async def new_post(client: Bot, message: Message):
    if DISABLE_CHANNEL_BUTTON:
        return

    converted_id = message.id * abs(client.db_channel.id)
    string = f"get-{converted_id}"
    base64_string = await encode(string)
    link = f"https://t.me/{client.username}?start={base64_string}"

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔁 Share URL", url=f"https://telegram.me/share/url?url={link}")]
    ])

    try:
        await message.edit_reply_markup(keyboard)
    except:
        pass


# -------------------------------
# NON-ADMIN USER DIRECT REPLY FALLBACK
# -------------------------------
@Bot.on_message(filters.private & filters.incoming & ~filters.command([
    'start','users','broadcast','batch','genlink','stats','joinchannels','pypi',
    'restart','settings','joinchannelon','joinchanneloff','admin','autodelete',
    'autodeleteon','autodeleteoff','maintenance','ban','unban','bannedlist',
    'addadmin','removeadmin','adminlist', 'maintenance'
]))
async def user_direct_reply(client: Bot, message: Message):
    user_id = message.from_user.id
    
    # If user is admin, ignore this fallback (handled seamlessly above)
    if await is_admin(user_id):
        return
        
    # Catch non-admins sending text, links or documents and warn them
    try:
        await message.reply_text(USER_REPLY_TEXT, quote=True)
    except:
        pass
        
