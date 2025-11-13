#TitanXBots - permissions.py
from config import OWNER_ID
from database.database import is_admin

def owner_only(func):
    """Allow only the bot owner to run this command."""
    async def wrapper(client, message):
        if message.from_user.id != OWNER_ID:
            return await message.reply_text("🚫 Only the bot owner can use this command.")
        return await func(client, message)
    return wrapper


def admin_only(func):
    """Allow only admins or owner to run this command."""
    async def wrapper(client, message):
        if not (await is_admin(message.from_user.id) or message.from_user.id == OWNER_ID):
            return await message.reply_text("🚫 You don't have permission to use this command.")
        return await func(client, message)
    return wrapper
