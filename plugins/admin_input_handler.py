from bot import Bot
from pyrogram import filters
from database.database import add_admin, remove_admin, ban_user, unban_user
from plugins.callback_handler import admin_state


@Bot.on_message(filters.private & filters.text)
async def admin_input_handler(client, message):

    user_id = message.from_user.id

    if user_id not in admin_state:
        return

    action = admin_state[user_id]
    text = message.text.strip()

    if action == "add_admin":

        if not text.isdigit():
            return await message.reply_text("❌ Send valid user ID")

        await add_admin(int(text))
        await message.reply_text(f"✅ `{text}` added as admin")

    elif action == "remove_admin":

        if not text.isdigit():
            return await message.reply_text("❌ Send valid user ID")

        await remove_admin(int(text))
        await message.reply_text(f"❌ `{text}` removed from admin")

    elif action == "ban_user":

        parts = text.split(maxsplit=1)

        if not parts[0].isdigit():
            return await message.reply_text("❌ Invalid user ID")

        uid = int(parts[0])
        reason = parts[1] if len(parts) > 1 else "No reason"

        await ban_user(uid, reason)

        await message.reply_text(f"🚫 `{uid}` banned\nReason: {reason}")

    elif action == "unban_user":

        if not text.isdigit():
            return await message.reply_text("❌ Invalid user ID")

        await unban_user(int(text))

        await message.reply_text(f"✅ `{text}` unbanned")

    admin_state.pop(user_id, None)
