from bot import Bot
from config import *
from Script import *

from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors import MessageNotModified

from database.database import (
    is_admin, add_admin, remove_admin,
    get_admins, ban_user, unban_user,
    get_banned_users
)

import asyncio

# -------------------------------
# ACTIVE INPUT TRACKER
# -------------------------------
active_inputs = {}

# -------------------------------
# SAFE EDIT
# -------------------------------
async def safe_edit(message, text, buttons):
    try:
        await message.edit_text(
            text,
            reply_markup=buttons,
            disable_web_page_preview=True
        )
    except MessageNotModified:
        pass
    except:
        await message.reply_text(
            text,
            reply_markup=buttons,
            disable_web_page_preview=True
        )

# -------------------------------
# INPUT SYSTEM (CANCEL + BACK)
# -------------------------------
async def get_input(client, query, prompt, back_callback):

    user_id = query.from_user.id
    chat_id = query.message.chat.id

    active_inputs[user_id] = True

    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("❌ Cancel", callback_data="cancel_input"),
            InlineKeyboardButton("🔙 Back", callback_data=back_callback)
        ]
    ])

    await query.message.edit_text(prompt, reply_markup=buttons)

    while active_inputs.get(user_id):
        try:
            msg = await client.listen(chat_id, timeout=300)

            if not active_inputs.get(user_id):
                return None

            if msg.text:
                active_inputs.pop(user_id, None)
                return msg.text

        except asyncio.TimeoutError:
            active_inputs.pop(user_id, None)
            await query.message.reply("⌛ Timeout")
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
    # CANCEL INPUT
    # -------------------------------
    if data == "cancel_input":
        if active_inputs.get(user_id):
            active_inputs.pop(user_id, None)

            return await safe_edit(
                query.message,
                "❌ Process Cancelled",
                InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 Back", callback_data="settings")]
                ])
            )
        else:
            return await query.answer("Nothing to cancel", show_alert=True)

    # -------------------------------
    # START
    # -------------------------------
    elif data == "start":
        buttons = [[
            InlineKeyboardButton("🧠 Help", callback_data="help"),
            InlineKeyboardButton("🔰 About", callback_data="about")
        ]]
        if admin_status:
            buttons.append([
                InlineKeyboardButton("⚙️ Settings", callback_data="settings")
            ])

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
                [
                    InlineKeyboardButton("📜 Commands", callback_data="commands"),
                    InlineKeyboardButton("ℹ️ About", callback_data="about")
                ],
                [
                    InlineKeyboardButton("🏠 Home", callback_data="start"),
                    InlineKeyboardButton("❌ Close", callback_data="close")
                ]
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
                [InlineKeyboardButton("🏠 Home", callback_data="start")]
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
                [
                    InlineKeyboardButton("🔙 Back", callback_data="help"),
                    InlineKeyboardButton("🏠 Home", callback_data="start")
                ]
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
                [InlineKeyboardButton("🔙 Back", callback_data="about")],
                [InlineKeyboardButton("🏠 Home", callback_data="start")]
            ])
        )

    # -------------------------------
    # SETTINGS
    # -------------------------------
    elif data == "settings":
        if not admin_status:
            return await query.answer("Admins only!", show_alert=True)

        await safe_edit(
            query.message,
            "⚙️ Admin Panel",
            InlineKeyboardMarkup([
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
        await safe_edit(
            query.message,
            "👨‍💻 Admin Menu",
            InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("➕ Add Admin", callback_data="add_admin"),
                    InlineKeyboardButton("➖ Remove Admin", callback_data="remove_admin")
                ],
                [InlineKeyboardButton("📋 Admin List", callback_data="admin_list")],
                [InlineKeyboardButton("🔙 Back", callback_data="settings")]
            ])
        )

    # ADD ADMIN
    elif data == "add_admin":
        text = await get_input(client, query, "Send User ID to add admin", "admin_menu")
        if not text or not text.isdigit():
            return
        await add_admin(int(text))
        await safe_edit(query.message, "✅ Admin Added",
            InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="admin_menu")]]))

    # REMOVE ADMIN
    elif data == "remove_admin":
        text = await get_input(client, query, "Send User ID to remove admin", "admin_menu")
        if not text or not text.isdigit():
            return
        await remove_admin(int(text))
        await safe_edit(query.message, "✅ Admin Removed",
            InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="admin_menu")]]))

    # ADMIN LIST
    elif data == "admin_list":
        admins = await get_admins()
        text = "👨‍💻 Admins:\n\n" + "\n".join(map(str, admins)) if admins else "No admins found"
        await safe_edit(query.message, text,
            InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="admin_menu")]]))

    # -------------------------------
    # BAN MENU
    # -------------------------------
    elif data == "ban_menu":
        await safe_edit(
            query.message,
            "🚫 Ban Menu",
            InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("🔨 Ban User", callback_data="ban_user"),
                    InlineKeyboardButton("♻️ Unban User", callback_data="unban_user")
                ],
                [InlineKeyboardButton("📋 Banned List", callback_data="banned_list")],
                [InlineKeyboardButton("🔙 Back", callback_data="settings")]
            ])
        )

    # BAN USER
    elif data == "ban_user":
        text = await get_input(client, query, "Send user_id reason", "ban_menu")
        if not text:
            return
        parts = text.split(maxsplit=1)
        if not parts[0].isdigit():
            return await query.message.reply("Invalid ID")
        uid = int(parts[0])
        reason = parts[1] if len(parts) > 1 else "No reason"
        await ban_user(uid, reason)
        await safe_edit(query.message, "🚫 User Banned",
            InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="ban_menu")]]))

    # UNBAN USER
    elif data == "unban_user":
        text = await get_input(client, query, "Send user_id", "ban_menu")
        if not text or not text.isdigit():
            return
        await unban_user(int(text))
        await safe_edit(query.message, "♻️ User Unbanned",
            InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="ban_menu")]]))

    # BANNED LIST
    elif data == "banned_list":
        users = await get_banned_users()
        if not users:
            text = "No banned users"
        else:
            text = "🚫 Banned Users:\n\n"
            for u in users:
                text += f"{u['_id']} - {u.get('reason','')}\n"

        await safe_edit(query.message, text,
            InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="ban_menu")]]))

    # CLOSE
    elif data == "close":
        await query.message.delete()
