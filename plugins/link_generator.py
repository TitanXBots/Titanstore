import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from helper_func import encode, get_message_id
from database.database import is_admin

@Client.on_message(filters.private & filters.command('batch'))
async def batch(client: Client, message: Message):
    user_id = message.from_user.id
    if not await is_admin(user_id):
        return

    while True:
        try:
            first_message = await client.ask(
                chat_id=user_id,
                text="Forward FIRST message from DB channel\nor send DB post link",
                filters=(filters.forwarded | filters.text),
                timeout=60
            )
        except asyncio.TimeoutError:
            return await message.reply_text("⏳ Request timed out or cancelled.")
        except:
            return

        f_msg_id = await get_message_id(client, first_message)
        if f_msg_id:
            break
        await first_message.reply_text("❌ Invalid message (not from DB channel)")

    while True:
        try:
            second_message = await client.ask(
                chat_id=user_id,
                text="Forward LAST message from DB channel\nor send DB post link",
                filters=(filters.forwarded | filters.text),
                timeout=60
            )
        except asyncio.TimeoutError:
            return await message.reply_text("⏳ Request timed out or cancelled.")
        except:
            return

        s_msg_id = await get_message_id(client, second_message)
        if s_msg_id:
            break
        await second_message.reply_text("❌ Invalid message (not from DB channel)")

    string = f"get-{f_msg_id * abs(client.db_channel.id)}-{s_msg_id * abs(client.db_channel.id)}"
    base64_string = await encode(string)
    link = f"https://t.me/{client.username}?start={base64_string}"

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔁 Share URL", url=f"https://telegram.me/share/url?url={link}")]
    ])

    await second_message.reply_text(
        f"<b>Here is your batch link:</b>\n\n{link}",
        reply_markup=keyboard
    )

@Client.on_message(filters.private & filters.command('genlink'))
async def link_generator(client: Client, message: Message):
    user_id = message.from_user.id
    if not await is_admin(user_id):
        return

    while True:
        try:
            channel_message = await client.ask(
                chat_id=user_id,
                text="Forward message from DB channel\nor send DB post link",
                filters=(filters.forwarded | filters.text),
                timeout=60
            )
        except asyncio.TimeoutError:
            return await message.reply_text("⏳ Request timed out or cancelled.")
        except:
            return

        msg_id = await get_message_id(client, channel_message)
        if msg_id:
            break
        await channel_message.reply_text("❌ Invalid message (not from DB channel)")

    base64_string = await encode(f"get-{msg_id * abs(client.db_channel.id)}")
    link = f"https://t.me/{client.username}?start={base64_string}"

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔁 Share URL", url=f"https://telegram.me/share/url?url={link}")]
    ])

    await channel_message.reply_text(
        f"<b>Here is your link:</b>\n\n{link}",
        reply_markup=keyboard
    )
    
