import time
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from database.database import (
    is_admin, get_all_users, get_admins, get_banned_users,
    get_global_fs_channels, get_protect_status, get_maintenance_status,
    get_auto_delete_status, get_force_sub_status, user_data
)
from helper_func import get_readable_time

# Record the exact time the bot starts to calculate uptime
BOT_START_TIME = time.time()

# ==========================================
# 1. ADMIN COMMAND (/adstatus) - Hidden from users
# ==========================================
@Client.on_message(filters.command("adstatus") & filters.private)
async def adstatus_command(client: Client, message: Message):
    # Security Check: Alert non-admins and auto-delete
    if not await is_admin(message.from_user.id):
        warning = await message.reply_text("⚠️ This command is only for Admins.")
        await asyncio.sleep(10)
        try:
            await warning.delete()
            await message.delete()
        except:
            pass
        return

    processing_msg = await message.reply_text("Fetching real-time statistics...")
    start_t = time.time()

    # Fetch Live Database Counts
    total_users = len(await get_all_users())
    total_admins = len(await get_admins())
    total_banned = len(await get_banned_users())
    premium_users = await user_data.count_documents({"is_premium": True})
    fsub_channels = len(await get_global_fs_channels())

    # Fetch Live Settings Statuses
    protect_content = "Enabled" if await get_protect_status() else "Disabled"
    maintenance = "Enabled" if await get_maintenance_status() else "Disabled"
    auto_delete = "Enabled" if await get_auto_delete_status() else "Disabled"
    fsub_mode = "Enabled" if await get_force_sub_status() else "Disabled"

    # Calculate Final Ping and Uptime
    ping = round((time.time() - start_t) * 1000)
    uptime = get_readable_time(int(time.time() - BOT_START_TIME))

    text = (
        f"📊 BOT STATS\n\n"
        f"• Total Users: {total_users}\n"
        f"• Total Admins: {total_admins}\n"
        f"• Total Banned Users: {total_banned}\n"
        f"• Premium Users: {premium_users}\n"
        f"• Total ForceSub Channels: {fsub_channels}\n\n"
        f"⚙️ BOT STATUS\n\n"
        f"• Bot Ping: {ping} ms\n"
        f"• Bot Uptime: {uptime}\n"
        f"• Protect Content: {protect_content}\n"
        f"• Maintenance Mode: {maintenance}\n"
        f"• Auto Delete Mode: {auto_delete}\n"
        f"• Request FSub Mode: {fsub_mode}"
    )

    await processing_msg.edit_text(text)
    
    # 🚀 NEW: Auto-delete the admin stats and user command after 60 seconds
    await asyncio.sleep(60)
    try:
        await processing_msg.delete()
        await message.delete()
    except:
        pass


# ==========================================
# 2. PUBLIC COMMAND (/status) - For everyone
# ==========================================
@Client.on_message(filters.command("status") & filters.private)
async def public_status_command(client: Client, message: Message):
    processing_msg = await message.reply_text("Checking systems...")
    start_t = time.time()

    # Fetch only the Maintenance status for the public menu
    maintenance = "Enabled" if await get_maintenance_status() else "Disabled"

    # Calculate Final Ping and Uptime
    ping = round((time.time() - start_t) * 1000)
    uptime = get_readable_time(int(time.time() - BOT_START_TIME))

    # Format exactly as requested (Kept Bot Status emojis, removed the rest)
    text = (
        f"⚙️ BOT STATUS\n"
        f"Bot Status: Online\n"
        f"Bot Ping: {ping} ms\n"
        f"Bot Uptime: {uptime}\n"
        f"Maintenance Mode: {maintenance}"
    )

    await processing_msg.edit_text(text)
    
    # 🚀 NEW: Auto-delete the public stats and user command after 60 seconds
    await asyncio.sleep(60)
    try:
        await processing_msg.delete()
        await message.delete()
    except:
        pass
        
