from pyrogram import Client, filters
from pyrogram.types import Message
from config import ADMINS
from database.database import ban_user, unban_user, is_banned, get_ban_reason

# Check every message if user is banned
@Client.on_message(filters.private)
async def check_banned_user(client, message: Message):
    user_id = message.from_user.id
    if await is_banned(user_id):
        reason = await get_ban_reason(user_id)
        await message.reply_text(
            f"🚫 You are banned from using this bot.\n\n**Reason:** {reason}"
        )
        return
    # Continue your bot's normal flow here
    await message.reply_text("✅ You are allowed to use the bot!")

# --- Admin command: Ban user ---
@Client.on_message(filters.command("ban") & filters.user(ADMINS))
async def ban_command(client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("Usage: `/ban user_id [reason]`", quote=True)
    
    try:
        user_id = int(message.command[1])
        reason = " ".join(message.command[2:]) or "No reason provided"
        await ban_user(user_id, reason)
        await message.reply_text(
            f"🚫 User `{user_id}` has been **banned**.\n**Reason:** {reason}"
        )
        try:
            await client.send_message(
                user_id,
                f"⚠️ You have been **banned** from using this bot.\n**Reason:** {reason}"
            )
        except Exception:
            pass
    except Exception as e:
        await message.reply_text(f"❌ Error: {e}")

# --- Admin command: Unban user ---
@Client.on_message(filters.command("unban") & filters.user(ADMINS))
async def unban_command(client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("Usage: `/unban user_id`", quote=True)
    
    try:
        user_id = int(message.command[1])
        await unban_user(user_id)
        await message.reply_text(f"✅ User `{user_id}` has been **unbanned**.")
        try:
            await client.send_message(
                user_id,
                "✅ You have been **unbanned**. You can now use the bot again!"
            )
        except Exception:
            pass
    except Exception as e:
        await message.reply_text(f"❌ Error: {e}")
