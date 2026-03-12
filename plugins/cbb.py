import asyncio
from pyrogram import filters
from bot import Bot
from config import *
from Script import COMMANDS_TXT, DISCLAIMER_TXT
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from database.database import ban_user, unban_user, banned_users_list
from pyrogram.errors import PeerIdInvalid, MessageNotModified
from pyromod import listen

# Track cancel state per admin
cancel_states = {}

@Bot.on_callback_query()
async def cb_handler(client: Bot, query: CallbackQuery):

    data = query.data
    user_id = query.from_user.id

    try:
        await query.answer()
    except:
        pass

    is_admin_user = user_id == OWNER_ID or user_id in ADMINS

    async def safe_edit(text, buttons):
        try:
            await query.message.edit_text(
                text,
                disable_web_page_preview=True,
                reply_markup=InlineKeyboardMarkup(buttons)
            )
        except MessageNotModified:
            pass

# -------------------------------
# HELP
# -------------------------------

    if data == "help":

        await safe_edit(
            HELP_TXT.format(first=query.from_user.first_name),
            [
                [
                    InlineKeyboardButton("🧑‍💻 Contact Owner", user_id=OWNER_ID),
                    InlineKeyboardButton("💬 Commands", callback_data="commands")
                ],
                [
                    InlineKeyboardButton("⚓ Home", callback_data="start"),
                    InlineKeyboardButton("⚡ Close", callback_data="close")
                ]
            ]
        )

# -------------------------------
# ABOUT
# -------------------------------

    elif data == "about":

        await safe_edit(
            ABOUT_TXT.format(first=query.from_user.first_name),
            [
                [
                    InlineKeyboardButton("📜 Disclaimer", callback_data="disclaimer"),
                    InlineKeyboardButton(
                        "🔐 Source Code",
                        url="https://github.com/TitanXBots/FileStore-Bot"
                    )
                ],
                [
                    InlineKeyboardButton("⚓ Home", callback_data="start"),
                    InlineKeyboardButton("⚡ Close", callback_data="close")
                ]
            ]
        )

# -------------------------------
# START
# -------------------------------

    elif data == "start":

        await safe_edit(
            START_MSG.format(first=query.from_user.first_name),
            [
                [
                    InlineKeyboardButton("🧠 Help", callback_data="help"),
                    InlineKeyboardButton("🔰 About", callback_data="about")
                ],
                [
                    InlineKeyboardButton("⚙️ Settings", callback_data="settings")
                ],
                [
                    InlineKeyboardButton("🤖 Update Channel", url="https://t.me/TitanXBots"),
                    InlineKeyboardButton("🔍 Support Group", url="https://t.me/TitanMattersSupport")
                ]
            ]
        )

# -------------------------------
# SETTINGS
# -------------------------------

    elif data == "settings":

        if not is_admin_user:
            return await query.answer("Admins only.", show_alert=True)

        await safe_edit(
            "⚙️ **Bot Settings Panel**",
            [
                [InlineKeyboardButton("🚫 Ban Menu", callback_data="ban_menu")],
                [InlineKeyboardButton("⚓ Home", callback_data="start")]
            ]
        )

# -------------------------------
# BAN MENU
# -------------------------------

    elif data == "ban_menu":

        if not is_admin_user:
            return await query.answer("Admins only.", show_alert=True)

        await safe_edit(
            "🚫 **Ban Control Panel**",
            [
                [
                    InlineKeyboardButton("🚫 Ban User", callback_data="ban_user"),
                    InlineKeyboardButton("✅ Unban User", callback_data="unban_user")
                ],
                [
                    InlineKeyboardButton("📋 Banned List", callback_data="banned_list")
                ],
                [
                    InlineKeyboardButton("⬅ Back", callback_data="settings")
                ]
            ]
        )

# -------------------------------
# BAN USER
# -------------------------------

    elif data == "ban_user":

        if not is_admin_user:
            return await query.answer("Admins only.", show_alert=True)

        cancel_states[user_id] = False

        await safe_edit(
            "Send **User ID and reason**\n\nExample:\n`123456789 spam`",
            [[InlineKeyboardButton("❌ Cancel", callback_data="cancel_process")]]
        )

        while True:

            msg = await client.listen(
                chat_id=query.message.chat.id,
                filters=filters.user(user_id)
            )

            if cancel_states.get(user_id):
                cancel_states[user_id] = False
                return await msg.reply_text("❌ Ban process cancelled.")

            parts = msg.text.split(maxsplit=1)

            if not parts[0].isdigit():
                await msg.reply_text("❌ Invalid user ID")
                continue

            uid = int(parts[0])
            reason = parts[1] if len(parts) > 1 else "No reason"

            await ban_user(uid, reason)

            await msg.reply_text(
                f"✅ User `{uid}` banned\nReason: {reason}"
            )
            break

# -------------------------------
# UNBAN USER
# -------------------------------

    elif data == "unban_user":

        if not is_admin_user:
            return await query.answer("Admins only.", show_alert=True)

        cancel_states[user_id] = False

        await safe_edit(
            "Send **User ID** to unban",
            [[InlineKeyboardButton("❌ Cancel", callback_data="cancel_process")]]
        )

        while True:

            msg = await client.listen(
                chat_id=query.message.chat.id,
                filters=filters.user(user_id)
            )

            if cancel_states.get(user_id):
                cancel_states[user_id] = False
                return await msg.reply_text("❌ Unban process cancelled.")

            if not msg.text.isdigit():
                await msg.reply_text("❌ Invalid user ID")
                continue

            uid = int(msg.text)

            await unban_user(uid)

            await msg.reply_text(f"✅ User `{uid}` unbanned")
            break

# -------------------------------
# CANCEL BUTTON
# -------------------------------

    elif data == "cancel_process":

        cancel_states[user_id] = True

        await safe_edit(
            "❌ Process cancelled.",
            [[InlineKeyboardButton("⚓ Home", callback_data="start")]]
        )

# -------------------------------
# BANNED LIST
# -------------------------------

    elif data == "banned_list":

        if not is_admin_user:
            return await query.answer("Admins only.", show_alert=True)

        users = await banned_users_list()

        text = "🚫 **Banned Users**\n\n"

        if not users:
            text += "No banned users."

        else:
            for user in users:

                uid = user["_id"]
                reason = user.get("reason", "No reason")

                try:
                    user_obj = await client.get_users(uid)
                    name = user_obj.mention
                except PeerIdInvalid:
                    name = f"`{uid}`"

                text += f"• {name} — {reason}\n"

        await safe_edit(
            text,
            [
                [
                    InlineKeyboardButton("⬅ Back", callback_data="ban_menu"),
                    InlineKeyboardButton("⚡ Close", callback_data="close")
                ]
            ]
        )

# -------------------------------
# COMMANDS
# -------------------------------

    elif data == "commands":

        await safe_edit(
            COMMANDS_TXT,
            [
                [InlineKeyboardButton("🔙 Back to Help", callback_data="help")],
                [
                    InlineKeyboardButton("⚓ Home", callback_data="start"),
                    InlineKeyboardButton("⚡ Close", callback_data="close")
                ]
            ]
        )

# -------------------------------
# DISCLAIMER
# -------------------------------

    elif data == "disclaimer":

        await safe_edit(
            DISCLAIMER_TXT,
            [
                [InlineKeyboardButton("🔰 About", callback_data="about")],
                [
                    InlineKeyboardButton("⚓ Home", callback_data="start"),
                    InlineKeyboardButton("⚡ Close", callback_data="close")
                ]
            ]
        )

# -------------------------------
# CLOSE
# -------------------------------

    elif data == "close":

        try:
            await query.message.delete()
        except:
            pass
