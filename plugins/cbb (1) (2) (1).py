from bot import Bot
from config import *
from Script import *
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors import MessageNotModified
import asyncio
from database.database import *
# -------------------------------
# SAFE MESSAGE EDIT
# -------------------------------
async def safe_edit(message, text, buttons):
    try:
        await message.edit_text(
            text=text,
            disable_web_page_preview=True,
            reply_markup=buttons
        )
    except MessageNotModified:
        pass

# -------------------------------
# ADMIN CHECK
# -------------------------------
async def is_admin(user_id: int) -> bool:
    return user_id == OWNER_ID or admins_collection.find_one({"_id": user_id}) is not None

# -------------------------------
# CALLBACK HANDLER
# -------------------------------
@Bot.on_callback_query()
async def cb_handler(client: Bot, query: CallbackQuery):
    data = query.data
    user_id = query.from_user.id
    admin_status = await is_admin(user_id)

    # -------------------------------
    # HELP
    # -------------------------------
    if data == "help":
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("🧑‍💻 Contact Owner", user_id=OWNER_ID),
             InlineKeyboardButton("💬 Commands", callback_data="commands")],
            [InlineKeyboardButton("🏠 Home", callback_data="start"),
             InlineKeyboardButton("❌ Close", callback_data="close")]
        ])
        await safe_edit(query.message, HELP_TXT.format(first=query.from_user.first_name), buttons)

    # -------------------------------
    # COMMANDS
    # -------------------------------
    elif data == "commands":
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back", callback_data="help")],
            [InlineKeyboardButton("🏠 Home", callback_data="start"),
             InlineKeyboardButton("❌ Close", callback_data="close")]
        ])
        await safe_edit(query.message, COMMANDS_TXT, buttons)

    # -------------------------------
    # DISCLAIMER
    # -------------------------------
    elif data == "disclaimer":
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back", callback_data="about")],
            [InlineKeyboardButton("🏠 Home", callback_data="start"),
             InlineKeyboardButton("❌ Close", callback_data="close")]
        ])
        await safe_edit(query.message, DISCLAIMER_TXT, buttons)

    # -------------------------------
    # ABOUT
    # -------------------------------
    elif data == "about":
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("📜 Disclaimer", callback_data="disclaimer"),
             InlineKeyboardButton("🔐 Source", url="https://github.com/TitanXBots/FileStore-Bot")],
            [InlineKeyboardButton("🏠 Home", callback_data="start"),
             InlineKeyboardButton("❌ Close", callback_data="close")]
        ])
        await safe_edit(query.message, ABOUT_TXT.format(first=query.from_user.first_name), buttons)

    # -------------------------------
    # START
    # -------------------------------
    elif data == "start":
        buttons = [[InlineKeyboardButton("🧠 Help", callback_data="help"),
                    InlineKeyboardButton("📗 About", callback_data="about")]]
        if admin_status:
            buttons.append([InlineKeyboardButton("⚙️ Settings", callback_data="settings")])
        await safe_edit(query.message, START_MSG.format(first=query.from_user.first_name), InlineKeyboardMarkup(buttons))

    # -------------------------------
    # SETTINGS
    # -------------------------------
    elif data == "settings":
        if not admin_status:
            await query.answer("⚠️ Only admins allowed.", show_alert=True)
            return
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("👨‍💻 Admin Menu", callback_data="admin_menu"),
             InlineKeyboardButton("🚫 Ban Menu", callback_data="ban_menu")],
            [InlineKeyboardButton("🔙 Back", callback_data="start")]
        ])
        await safe_edit(query.message, "⚙️ **Admin Settings Panel**", buttons)

    # -------------------------------
    # ADMIN MENU
    # -------------------------------
    elif data == "admin_menu":
        if not admin_status:
            await query.answer("⚠️ Only admins allowed.", show_alert=True)
            return
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("➕ Add Admin", callback_data="add_admin"),
             InlineKeyboardButton("➖ Remove Admin", callback_data="remove_admin")],
            [InlineKeyboardButton("📜 Admin List", callback_data="admin_list")],
            [InlineKeyboardButton("🔙 Back", callback_data="settings")]
        ])
        await safe_edit(query.message, "👨‍💻 **Admin Management Panel**", buttons)

    # -------------------------------
    # BAN MENU
    # -------------------------------
    elif data == "ban_menu":
        if not admin_status:
            await query.answer("⚠️ Only admins allowed.", show_alert=True)
            return
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("🚫 Ban User", callback_data="ban_user"),
             InlineKeyboardButton("✅ Unban User", callback_data="unban_user")],
            [InlineKeyboardButton("📋 Banned List", callback_data="banned_list")],
            [InlineKeyboardButton("🔙 Back", callback_data="settings")]
        ])
        await safe_edit(query.message, "🚫 **Ban Management Panel**", buttons)

    # -------------------------------
    # BAN USER
    # -------------------------------
    elif data == "ban_user":
        if not admin_status:
            await query.answer("⚠️ Only admins allowed.", show_alert=True)
            return
        await query.message.edit_text(
            "🚫 Send the **User ID** to ban.\nYou can add a reason:\n<code>user_id reason</code>\nOr send /cancel to stop."
        )
        try:
            msg = await client.listen(chat_id=query.message.chat.id, timeout=300)
            if msg.text == "/cancel":
                await msg.reply("❌ Ban canceled!")
                return
            parts = msg.text.split(maxsplit=1)
            if not parts[0].isdigit():
                await msg.reply("⚠️ Invalid User ID!")
                return
            ban_user_id = int(parts[0])
            reason = parts[1] if len(parts) > 1 else "No reason provided"
            await bans_collection.update_one(
                {"_id": ban_user_id},
                {"$set": {"is_banned": True, "reason": reason}},
                upsert=True
            )
            await msg.reply(f"✅ User `{ban_user_id}` banned.\nReason: {reason}")
        except asyncio.TimeoutError:
            await query.message.reply("⌛ Timeout! Ban canceled.")

    # -------------------------------
    # UNBAN USER
    # -------------------------------
    elif data == "unban_user":
        if not admin_status:
            await query.answer("⚠️ Only admins allowed.", show_alert=True)
            return
        await query.message.edit_text("✅ Send the **User ID** to unban.\nOr send /cancel to stop.")
        try:
            msg = await client.listen(chat_id=query.message.chat.id, timeout=300)
            if msg.text == "/cancel":
                await msg.reply("❌ Unban canceled!")
                return
            if not msg.text.isdigit():
                await msg.reply("⚠️ Invalid User ID!")
                return
            unban_user_id = int(msg.text)
            await bans_collection.update_one(
                {"_id": unban_user_id},
                {"$set": {"is_banned": False, "reason": ""}}
            )
            await msg.reply(f"✅ User `{unban_user_id}` unbanned.")
        except asyncio.TimeoutError:
            await query.message.reply("⌛ Timeout! Unban canceled.")

    # -------------------------------
    # BANNED LIST
    # -------------------------------
    elif data == "banned_list":
        if not admin_status:
            await query.answer("⚠️ Only admins allowed.", show_alert=True)
            return
        banned_users = bans_collection.find({"is_banned": True})
        lines = [f"• {user['_id']} - {user.get('reason','No reason')}" async for user in banned_users]
        text = "🚫 Banned Users:\n" + "\n".join(lines) if lines else "No users banned."
        await query.message.edit_text(text)

    # -------------------------------
    # ADD ADMIN
    # -------------------------------
    elif data == "add_admin":
        if not admin_status:
            await query.answer("⚠️ Only admins allowed.", show_alert=True)
            return
        await query.message.edit_text("➕ Send the **User ID** to add as admin.\nOr send /cancel to stop.")
        try:
            msg = await client.listen(chat_id=query.message.chat.id, timeout=300)
            if msg.text == "/cancel":
                await msg.reply("❌ Add Admin canceled!")
                return
            if not msg.text.isdigit():
                await msg.reply("⚠️ Invalid User ID!")
                return
            new_admin_id = int(msg.text)
            admins_collection.update_one({"_id": new_admin_id}, {"$set": {"is_admin": True}}, upsert=True)
            await msg.reply(f"✅ User `{new_admin_id}` added as admin.")
        except asyncio.TimeoutError:
            await query.message.reply("⌛ Timeout! Add Admin canceled.")

    # -------------------------------
    # REMOVE ADMIN
    # -------------------------------
    elif data == "remove_admin":
        if not admin_status:
            await query.answer("⚠️ Only admins allowed.", show_alert=True)
            return
        await query.message.edit_text("➖ Send the **User ID** to remove from admin.\nOr send /cancel to stop.")
        try:
            msg = await client.listen(chat_id=query.message.chat.id, timeout=300)
            if msg.text == "/cancel":
                await msg.reply("❌ Remove Admin canceled!")
                return
            if not msg.text.isdigit():
                await msg.reply("⚠️ Invalid User ID!")
                return
            remove_admin_id = int(msg.text)
            admins_collection.delete_one({"_id": remove_admin_id})
            await msg.reply(f"✅ User `{remove_admin_id}` removed from admin.")
        except asyncio.TimeoutError:
            await query.message.reply("⌛ Timeout! Remove Admin canceled.")

    # -------------------------------
    # ADMIN LIST
    # -------------------------------
    elif data == "admin_list":
        if not admin_status:
            await query.answer("⚠️ Only admins allowed.", show_alert=True)
            return
        admins = admins_collection.find({})
        lines = [f"• {admin['_id']}" async for admin in admins]
        text = "👨‍💻 Admin List:\n" + "\n".join(lines) if lines else "No admins found."
        await query.message.edit_text(text)

    # -------------------------------
    # CLOSE
    # -------------------------------
    elif data == "close":
        await query.message.delete()
        try:
            await query.message.reply_to_message.delete()
        except:
            pass
