from pyrogram import filters
from bot import Bot
from database.database import Seishiro
from config import OWNER_ID


@Bot.on_message(filters.command("addadmin") & filters.user(OWNER_ID))
async def add_admin_command(client, message):

    try:
        admin_id = int(message.command[1])
    except:
        await message.reply_text("Usage:\n/addadmin user_id")
        return

    await Seishiro.add_admin(admin_id)

    await message.reply_text(f"✅ Admin added successfully:\n`{admin_id}`")
