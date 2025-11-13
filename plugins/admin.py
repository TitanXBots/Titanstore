#TitanXBots - Admin Commands
from pyrogram import Client, filters
from config import OWNER_ID
from database import add_admin, remove_admin, list_admins, is_admin
from permissions import owner_only, admin_only  # ✅ Centralized permissions

# -------------------------------
# Owner-only Commands
# -------------------------------

@Client.on_message(filters.command("addadmin") & filters.private)
@owner_only
async def add_admin_cmd(client, message):
    """Add a user as admin (Owner only)."""
    if len(message.command) < 2:
        return await message.reply_text("Usage: `/addadmin user_id`", quote=True)

    try:
        user_id = int(message.command[1])
        await add_admin(user_id)
        await message.reply_text(f"✅ User `{user_id}` has been added as admin.")
    except ValueError:
        await message.reply_text("⚠️ Invalid user ID format.")


@Client.on_message(filters.command("removeadmin") & filters.private)
@owner_only
async def remove_admin_cmd(client, message):
    """Remove a user from the admin list (Owner only)."""
    if len(message.command) < 2:
        return await message.reply_text("Usage: `/removeadmin user_id`", quote=True)

    try:
        user_id = int(message.command[1])
        await remove_admin(user_id)
        await message.reply_text(f"❌ User `{user_id}` has been removed from admin list.")
    except ValueError:
        await message.reply_text("⚠️ Invalid user ID format.")


# -------------------------------
# Admin + Owner Commands
# -------------------------------

@Client.on_message(filters.command("adminlist") & filters.private)
@admin_only
async def admin_list_cmd(client, message):
    """View all admins (Accessible by Admins + Owner)."""
    admins = await list_admins()
    if not admins:
        return await message.reply_text("📭 No admins found in the database.")
    
    text = "<b>👑 Current Admins:</b>\n" + "\n".join([f"• <code>{x}</code>" for x in admins])
    await message.reply_text(text)
