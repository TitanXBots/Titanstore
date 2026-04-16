import asyncio
from pyrogram import filters, Client
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors import MessageNotModified

from bot import Bot
from config import *
from Script import *

from helper_func import safe_edit, get_input, auto_delete
from database.database import (
    admins_collection,
    banned_users,
    is_admin
)


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

    # ---------------- START ----------------
    if data == "start":
        buttons = [
            [
                InlineKeyboardButton("🧠 Help", callback_data="help"),
                InlineKeyboardButton("🔰 About", callback_data="about")
            ]
        ]

        if admin_status:
            buttons.append([InlineKeyboardButton("⚙️ Settings", callback_data="settings")])

        return await safe_edit(
            query.message,
            START_MSG.format(first=query.from_user.first_name),
            InlineKeyboardMarkup(buttons)
        )

    # ---------------- HELP ----------------
    elif data == "help":
        return await safe_edit(
            query.message,
            HELP_TXT.format(first=query.from_user.first_name),
            InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("🧑‍💻 Contact Owner", url=f"tg://user?id={OWNER_ID}"),
                    InlineKeyboardButton("💬 Commands", callback_data="commands")
                ],
                [
                    InlineKeyboardButton("⚓ Home", callback_data="start"),
                    InlineKeyboardButton("⚡ Close", callback_data="close")
                ]
            ])
        )

    # ---------------- COMMANDS ----------------
    elif data == "commands":
        return await safe_edit(
            query.message,
            COMMANDS_TXT,
            InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back", callback_data="help")],
                [
                    InlineKeyboardButton("⚓ Home", callback_data="start"),
                    InlineKeyboardButton("⚡ Close", callback_data="close")
                ]
            ])
        )

    # ---------------- ABOUT ----------------
    elif data == "about":
        return await safe_edit(
            query.message,
            ABOUT_TXT.format(first=query.from_user.first_name),
            InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("📜 Disclaimer", callback_data="disclaimer"),
                    InlineKeyboardButton("🔐 Source", url="https://github.com/TitanXBots/FileStore-Bot")
                ],
                [
                    InlineKeyboardButton("⚓ Home", callback_data="start"),
                    InlineKeyboardButton("⚡ Close", callback_data="close")
                ]
            ])
        )

    # ---------------- DISCLAIMER ----------------
    elif data == "disclaimer":
        return await safe_edit(
            query.message,
            DISCLAIMER_TXT,
            InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back", callback_data="about")],
                [
                    InlineKeyboardButton("⚓ Home", callback_data="start"),
                    InlineKeyboardButton("⚡ Close", callback_data="close")
                ]
            ])
        )

    # ---------------- SETTINGS ----------------
    elif data == "settings":
        if not admin_status:
            return await query.answer("⚠️ Admins only!", show_alert=True)

        return await safe_edit(
            query.message,
            "⚙️ Admin Settings Panel",
            InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("👨‍💻 Admin Menu", callback_data="admin_menu"),
                    InlineKeyboardButton("🚫 Ban Menu", callback_data="ban_menu")
                ],
                [InlineKeyboardButton("🔙 Back", callback_data="start")]
            ])
        )

    # ---------------- ADMIN MENU ----------------
    elif data == "admin_menu":
        if not admin_status:
            return await query.answer("⚠️ Admins only!", show_alert=True)

        return await safe_edit(
            query.message,
            "👨‍💻 Admin Management",
            InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("➕ Add Admin", callback_data="add_admin"),
                    InlineKeyboardButton("➖ Remove Admin", callback_data="remove_admin")
                ],
                [
                    InlineKeyboardButton("📋 Admin List", callback_data="admin_list")
                ],
                [
                    InlineKeyboardButton("🔙 Back", callback_data="settings")
                ]
            ])
        )

    # ---------------- BAN MENU ----------------
    elif data == "ban_menu":
        if not admin_status:
            return await query.answer("⚠️ Admins only!", show_alert=True)

        return await safe_edit(
            query.message,
            "🚫 Ban Management",
            InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("🚫 Ban User", callback_data="ban_user"),
                    InlineKeyboardButton("✅ Unban User", callback_data="unban_user")
                ],
                [
                    InlineKeyboardButton("📄 Banned List", callback_data="banned_list")
                ],
                [
                    InlineKeyboardButton("🔙 Back", callback_data="settings")
                ]
            ])
        )

    # ---------------- BAN USER ----------------
    elif data == "ban_user":
        if not admin_status:
            return await query.answer("⚠️ Admins only!", show_alert=True)

        text = await get_input(client, query.message, "Send user_id [reason]")
        if not text:
            return

        parts = text.split(maxsplit=1)
        if not parts[0].isdigit():
            return await query.message.reply("❌ Invalid User ID")

        uid = int(parts[0])
        reason = parts[1] if len(parts) > 1 else "No reason"

        await banned_users.update_one(
            {"_id": uid},
            {"$set": {"is_banned": True, "reason": reason}},
            upsert=True
        )

        return await query.message.reply(f"✅ User {uid} banned")

    # ---------------- UNBAN USER ----------------
    elif data == "unban_user":
        if not admin_status:
            return await query.answer("⚠️ Admins only!", show_alert=True)

        text = await get_input(client, query.message, "Send user_id")
        if not text or not text.isdigit():
            return

        uid = int(text)

        await banned_users.update_one(
            {"_id": uid},
            {"$set": {"is_banned": False, "reason": ""}}
        )

        return await query.message.reply(f"✅ User {uid} unbanned")

    # ---------------- BANNED LIST ----------------
    elif data == "banned_list":
        if not admin_status:
            return await query.answer("⚠️ Admins only!", show_alert=True)

        banned = await banned_users.find({"is_banned": True}).to_list(length=None)

        if not banned:
            return await safe_edit(
                query.message,
                "No banned users.",
                InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="ban_menu")]])
            )

        text = "\n".join([f"• {u['_id']} - {u.get('reason','No reason')}" for u in banned])

        return await safe_edit(
            query.message,
            f"🚫 Banned Users:\n\n{text}",
            InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="ban_menu")]])
        )

    # ---------------- ADD ADMIN ----------------
    elif data == "add_admin":
        if not admin_status:
            return await query.answer("⚠️ Admins only!", show_alert=True)

        text = await get_input(client, query.message, "Send user_id")
        if not text or not text.isdigit():
            return

        uid = int(text)

        await admins_collection.update_one(
            {"_id": uid},
            {"$set": {"is_admin": True}},
            upsert=True
        )

        return await query.message.reply(f"✅ Admin added: {uid}")

    # ---------------- REMOVE ADMIN ----------------
    elif data == "remove_admin":
        if not admin_status:
            return await query.answer("⚠️ Admins only!", show_alert=True)

        text = await get_input(client, query.message, "Send user_id")
        if not text or not text.isdigit():
            return

        uid = int(text)

        await admins_collection.delete_one({"_id": uid})

        return await query.message.reply(f"❌ Admin removed: {uid}")

    # ---------------- ADMIN LIST ----------------
    elif data == "admin_list":
        if not admin_status:
            return await query.answer("⚠️ Admins only!", show_alert=True)

        admins = await admins_collection.find({}).to_list(length=None)

        if not admins:
            return await safe_edit(
                query.message,
                "No admins found.",
                InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="admin_menu")]])
            )

        text = "\n".join([f"• {a['_id']}" for a in admins])

        return await safe_edit(
            query.message,
            f"👨‍💻 Admin List:\n\n{text}",
            InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="admin_menu")]])
        )

    # ---------------- CLOSE ----------------
    elif data == "close":
        try:
            await query.message.delete()
        except:
            pass
