from bot import Bot
from config import *
from Script import *
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors import MessageNotModified
from database.database import (
    admins_collection,
    banned_users,
    is_admin,
    get_setting,
    set_setting
)
import asyncio

# -------------------------------
# AUTO DELETE
# -------------------------------
async def auto_delete(msg, delay=60):
    await asyncio.sleep(delay)
    try:
        await msg.delete()
    except:
        pass

# -------------------------------
# SAFE EDIT
# -------------------------------
async def safe_edit(message, text, buttons=None):
    try:
        await message.edit_text(
            text=text,
            reply_markup=buttons,
            disable_web_page_preview=True
        )
    except MessageNotModified:
        pass
    except:
        try:
            await message.reply_text(
                text=text,
                reply_markup=buttons,
                disable_web_page_preview=True
            )
        except:
            pass

# -------------------------------
# INPUT HELPER (Pyrogram listen)
# -------------------------------
async def get_input(client, message, prompt):
    await message.edit_text(f"{prompt}\n\nSend /cancel to stop.")

    try:
        msg = await client.listen(message.chat.id, timeout=300)

        if not msg.text:
            return None

        if msg.text.lower() == "/cancel":
            return None

        return msg.text

    except Exception:
        return None

# -------------------------------
# CALLBACK HANDLER
# -------------------------------
@Bot.on_callback_query()
async def cb_handler(client: Bot, query: CallbackQuery):

    await query.answer()

    if not query.message:
        return

    data = query.data
    user_id = query.from_user.id
    admin_status = await is_admin(user_id)

    # -------------------------------
    # START
    # -------------------------------
    if data == "start":
        buttons = [
            [InlineKeyboardButton("🧠 Help", callback_data="help"),
             InlineKeyboardButton("🔰 About", callback_data="about")]
        ]

        if admin_status:
            buttons.append([InlineKeyboardButton("⚙️ Settings", callback_data="settings")])

        await safe_edit(
            query.message,
            START_MSG.format(first=query.from_user.first_name),
            InlineKeyboardMarkup(buttons)
        )

    # -------------------------------
    # HELP
    # -------------------------------
    elif data == "help":
        await safe_edit(
            query.message,
            HELP_TXT.format(first=query.from_user.first_name),
            InlineKeyboardMarkup([
                [InlineKeyboardButton("💬 Commands", callback_data="commands")],
                [InlineKeyboardButton("⚓ Home", callback_data="start"),
                 InlineKeyboardButton("⚡ Close", callback_data="close")]
            ])
        )

    # -------------------------------
    # COMMANDS
    # -------------------------------
    elif data == "commands":
        await safe_edit(
            query.message,
            COMMANDS_TXT,
            InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back", callback_data="help")],
                [InlineKeyboardButton("⚓ Home", callback_data="start"),
                 InlineKeyboardButton("⚡ Close", callback_data="close")]
            ])
        )

    # -------------------------------
    # ABOUT
    # -------------------------------
    elif data == "about":
        await safe_edit(
            query.message,
            ABOUT_TXT.format(first=query.from_user.first_name),
            InlineKeyboardMarkup([
                [InlineKeyboardButton("📜 Disclaimer", callback_data="disclaimer")],
                [InlineKeyboardButton("⚓ Home", callback_data="start"),
                 InlineKeyboardButton("⚡ Close", callback_data="close")]
            ])
        )

    # -------------------------------
    # DISCLAIMER
    # -------------------------------
    elif data == "disclaimer":
        await safe_edit(
            query.message,
            DISCLAIMER_TXT,
            InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back", callback_data="about")]
            ])
        )

    # -------------------------------
    # SETTINGS (MAIN PANEL)
    # -------------------------------
    elif data == "settings":

        if not admin_status:
            return await query.answer("Admins only!", show_alert=True)

        status = get_setting("join_channels", True)

        await safe_edit(
            query.message,
            "⚙️ Admin Settings Panel",
            InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        f"Join Channels: {'🟢 ON' if status else '🔴 OFF'}",
                        callback_data="toggle_join"
                    )
                ],
                [
                    InlineKeyboardButton("👨‍💻 Admin Menu", callback_data="admin_menu"),
                    InlineKeyboardButton("🚫 Ban Menu", callback_data="ban_menu")
                ],
                [InlineKeyboardButton("🔙 Back", callback_data="start")]
            ])
        )

    # -------------------------------
    # TOGGLE JOIN CHANNELS
    # -------------------------------
    elif data == "toggle_join":

        if not admin_status:
            return await query.answer("Admins only!", show_alert=True)

        current = get_setting("join_channels", True)
        set_setting("join_channels", not current)

        await query.answer("Updated!", show_alert=True)

        status = get_setting("join_channels", True)

        await safe_edit(
            query.message,
            "⚙️ Admin Settings Panel",
            InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        f"Join Channels: {'🟢 ON' if status else '🔴 OFF'}",
                        callback_data="toggle_join"
                    )
                ],
                [
                    InlineKeyboardButton("👨‍💻 Admin Menu", callback_data="admin_menu"),
                    InlineKeyboardButton("🚫 Ban Menu", callback_data="ban_menu")
                ],
                [InlineKeyboardButton("🔙 Back", callback_data="start")]
            ])
        )

    # -------------------------------
    # ADMIN MENU
    # -------------------------------
    elif data == "admin_menu":

        if not admin_status:
            return await query.answer("Admins only!", show_alert=True)

        await safe_edit(
            query.message,
            "👨‍💻 Admin Panel",
            InlineKeyboardMarkup([
                [InlineKeyboardButton("➕ Add Admin", callback_data="add_admin"),
                 InlineKeyboardButton("➖ Remove Admin", callback_data="remove_admin")],
                [InlineKeyboardButton("📜 Admin List", callback_data="admin_list")],
                [InlineKeyboardButton("🔙 Back", callback_data="settings")]
            ])
        )

    # -------------------------------
    # BAN MENU
    # -------------------------------
    elif data == "ban_menu":

        if not admin_status:
            return await query.answer("Admins only!", show_alert=True)

        await safe_edit(
            query.message,
            "🚫 Ban Panel",
            InlineKeyboardMarkup([
                [InlineKeyboardButton("🚫 Ban User", callback_data="ban_user"),
                 InlineKeyboardButton("✅ Unban User", callback_data="unban_user")],
                [InlineKeyboardButton("📋 Banned List", callback_data="banned_list")],
                [InlineKeyboardButton("🔙 Back", callback_data="settings")]
            ])
        )

    # -------------------------------
    # BAN USER
    # -------------------------------
    elif data == "ban_user":

        if not admin_status:
            return await query.answer("Admins only!", show_alert=True)

        text = await get_input(client, query.message, "Send user_id [reason]")
        if not text:
            return

        parts = text.split(maxsplit=1)
        uid = int(parts[0])
        reason = parts[1] if len(parts) > 1 else "No reason"

        banned_users.update_one(
            {"_id": uid},
            {"$set": {"is_banned": True, "reason": reason}},
            upsert=True
        )

        await query.message.reply(f"User {uid} banned.")

    # -------------------------------
    # UNBAN USER
    # -------------------------------
    elif data == "unban_user":

        if not admin_status:
            return await query.answer("Admins only!", show_alert=True)

        text = await get_input(client, query.message, "Send user_id")
        if not text or not text.isdigit():
            return

        uid = int(text)

        banned_users.update_one(
            {"_id": uid},
            {"$set": {"is_banned": False, "reason": ""}}
        )

        await query.message.reply(f"User {uid} unbanned.")

    # -------------------------------
    # BANNED LIST
    # -------------------------------
    elif data == "banned_list":

        if not admin_status:
            return await query.answer("Admins only!", show_alert=True)

        banned = list(banned_users.find({"is_banned": True}))

        text = "\n".join(
            [f"{u['_id']} - {u.get('reason', '')}" for u in banned]
        ) or "No banned users"

        await safe_edit(
            query.message,
            f"🚫 Banned Users:\n\n{text}",
            InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back", callback_data="ban_menu")]
            ])
        )

    # -------------------------------
    # ADD ADMIN
    # -------------------------------
    elif data == "add_admin":

        if not admin_status:
            return await query.answer("Admins only!", show_alert=True)

        text = await get_input(client, query.message, "Send user_id")
        if not text or not text.isdigit():
            return

        uid = int(text)

        admins_collection.update_one(
            {"_id": uid},
            {"$set": {"is_admin": True}},
            upsert=True
        )

        await query.message.reply("Admin added.")

    # -------------------------------
    # REMOVE ADMIN
    # -------------------------------
    elif data == "remove_admin":

        if not admin_status:
            return await query.answer("Admins only!", show_alert=True)

        text = await get_input(client, query.message, "Send user_id")
        if not text or not text.isdigit():
            return

        uid = int(text)

        admins_collection.delete_one({"_id": uid})

        await query.message.reply("Admin removed.")

    # -------------------------------
    # ADMIN LIST
    # -------------------------------
    elif data == "admin_list":

        if not admin_status:
            return await query.answer("Admins only!", show_alert=True)

        admins = list(admins_collection.find({}))

        text = "\n".join([str(a["_id"]) for a in admins]) or "No admins"

        await safe_edit(
            query.message,
            f"👨‍💻 Admins:\n\n{text}",
            InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back", callback_data="admin_menu")]
            ])
        )

    # -------------------------------
    # CLOSE
    # -------------------------------
    elif data == "close":
        try:
            await query.message.delete()
        except:
            pass
