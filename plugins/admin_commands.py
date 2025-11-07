from pyrogram import Client, filters
from pyrogram.types import Message
from database.admins import add_admin, remove_admin, get_admins, is_admin

# Optional: Add a default owner (for first use)
OWNER_ID = int(os.environ.get("OWNER_ID", 5356695781))

@Client.on_message(filters.command("addadmin"))
async def add_admin_cmd(client, message: Message):
    sender_id = message.from_user.id
    admins = await get_admins()
    
    if sender_id not in admins and sender_id != OWNER_ID:
        return await message.reply_text("🚫 You are not authorized to add admins.")
    
    if len(message.command) < 2:
        return await message.reply_text("Usage: `/addadmin <user_id>`", quote=True)

    try:
        new_admin_id = int(message.command[1])
        added = await add_admin(new_admin_id)
        if added:
            await message.reply_text(f"✅ `{new_admin_id}` added as admin.")
        else:
            await message.reply_text("⚠️ User is already an admin.")
    except ValueError:
        await message.reply_text("❌ Invalid user ID format.")


@Client.on_message(filters.command("removeadmin"))
async def remove_admin_cmd(client, message: Message):
    sender_id = message.from_user.id
    admins = await get_admins()
    
    if sender_id not in admins and sender_id != OWNER_ID:
        return await message.reply_text("🚫 You are not authorized to remove admins.")
    
    if len(message.command) < 2:
        return await message.reply_text("Usage: `/removeadmin <user_id>`", quote=True)

    try:
        target_id = int(message.command[1])
        await remove_admin(target_id)
        await message.reply_text(f"🚫 `{target_id}` removed from admin list.")
    except ValueError:
        await message.reply_text("❌ Invalid user ID format.")


@Client.on_message(filters.command("adminlist"))
async def admin_list_cmd(client, message: Message):
    admins = await get_admins()
    if not admins:
        await message.reply_text("⚠️ No admins found.")
    else:
        text = "👮 **Admin List:**\n\n" + "\n".join([f"`{uid}`" for uid in admins])
        await message.reply_text(text)
