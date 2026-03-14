# callback_handler.py
import asyncio
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from bot import Bot
from config import *
from Script import *
from database.database import add_admin, remove_admin, admin_list, ban_user, unban_user, banned_users_list, is_admin

# -------------------------------
# Helper function: listen with /cancel
# -------------------------------
async def listen_with_cancel(client: Bot, chat_id: int, timeout: int = 300):
    try:
        msg = await client.listen(chat_id=chat_id, timeout=timeout)
        if msg.text.lower() == "/cancel":
            return None
        return msg
    except asyncio.TimeoutError:
        return None

# -------------------------------
# Callback handler
# -------------------------------
@Bot.on_callback_query()
async def cb_handler(client: Bot, query: CallbackQuery):
    data = query.data
    user_id = query.from_user.id

    try:
        await query.answer()
    except:
        pass

    # Check admin dynamically
    is_admin_user = user_id == OWNER_ID or user_id in ADMINS or await is_admin(user_id)

    # -------------------------------
    # HELP PANEL
    # -------------------------------
    if data == "help":
        buttons = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🧑‍💻 Contact Owner", user_id=OWNER_ID),
                InlineKeyboardButton("💬 Commands", callback_data="commands")
            ],
            [
                InlineKeyboardButton("⚓ Home", callback_data="start"),
                InlineKeyboardButton("⚡ Close", callback_data="close")
            ]
        ])
        await query.message.edit_text(
            HELP_TXT.format(first=query.from_user.first_name),
            disable_web_page_preview=True,
            reply_markup=buttons
        )

    # -------------------------------
    # ABOUT PANEL
    # -------------------------------
    elif data == "about":
        buttons = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("📜 Disclaimer", callback_data="disclaimer"),
                InlineKeyboardButton("🔐 Source Code", url="https://github.com/TitanXBots/FileStore-Bot")
            ],
            [
                InlineKeyboardButton("⚓ Home", callback_data="start"),
                InlineKeyboardButton("⚡ Close", callback_data="close")
            ]
        ])
        await query.message.edit_text(
            ABOUT_TXT.format(first=query.from_user.first_name),
            disable_web_page_preview=True,
            reply_markup=buttons
        )

    # -------------------------------
    # START PANEL
    # -------------------------------
    elif data == "start":
        buttons = [
            [InlineKeyboardButton("🧠 Help", callback_data="help"),
             InlineKeyboardButton("🔰 About", callback_data="about")]
        ]
        if is_admin_user:
            buttons.append([InlineKeyboardButton("⚙️ Settings", callback_data="settings")])
        await query.message.edit_text(
            START_MSG.format(first=query.from_user.first_name),
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    # -------------------------------
    # SETTINGS PANEL
    # -------------------------------
    elif data == "settings":
        if not is_admin_user:
            return await query.answer("Admins only.", show_alert=True)

        buttons = [
            [InlineKeyboardButton("🧑‍💼 Admin Menu", callback_data="admin_menu")],
            [InlineKeyboardButton("🚫 Ban Menu", callback_data="ban_menu")],
            [InlineKeyboardButton("⬅ Back", callback_data="start")]
        ]
        await query.message.edit_text(
            "⚙️ **Bot Settings Panel**",
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    # -------------------------------
    # ADMIN MENU
    # -------------------------------
    elif data == "admin_menu":
        if not is_admin_user:
            return await query.answer("Admins only.", show_alert=True)

        buttons = [
            [
                InlineKeyboardButton("➕ Add Admin", callback_data="add_admin"),
                InlineKeyboardButton("➖ Remove Admin", callback_data="remove_admin")
            ],
            [InlineKeyboardButton("📋 Admin List", callback_data="admin_list")],
            [InlineKeyboardButton("⬅ Back", callback_data="settings")]
        ]
        await query.message.edit_text(
            "🧑‍💼 **Admin Control Panel**",
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    # -------------------------------
    # BAN MENU
    # -------------------------------
    elif data == "ban_menu":
        if not is_admin_user:
            return await query.answer("Admins only.", show_alert=True)

        buttons = [
            [InlineKeyboardButton("🚫 Ban User", callback_data="ban_user"),
             InlineKeyboardButton("✅ Unban User", callback_data="unban_user")],
            [InlineKeyboardButton("📋 Banned List", callback_data="banned_list")],
            [InlineKeyboardButton("⬅ Back", callback_data="settings")]
        ]
        await query.message.edit_text("🚫 **Ban Control Panel**", reply_markup=InlineKeyboardMarkup(buttons))

    # -------------------------------
    # ADMIN & BAN ACTIONS
    # -------------------------------
    elif data in ["add_admin", "remove_admin", "ban_user", "unban_user", "admin_list", "banned_list"]:
        if not is_admin_user:
            return await query.answer("Admins only.", show_alert=True)

    # -------------------------------
    # ADD / REMOVE ADMIN
    # -------------------------------
    if data in ["add_admin", "remove_admin"]:
        action = "Add" if data == "add_admin" else "Remove"
        buttons = [[InlineKeyboardButton("⬅ Back", callback_data="admin_menu")]]
        await query.message.edit_text(
            f"Send the **User ID** to {action} as admin.\nType /cancel to abort.",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        msg = await listen_with_cancel(client, query.message.chat.id, timeout=120)
        if not msg:
            return await query.message.reply_text("❌ Action cancelled!", reply_markup=InlineKeyboardMarkup(buttons))
        if not msg.text.isdigit():
            return await msg.reply_text("❌ Invalid User ID", reply_markup=InlineKeyboardMarkup(buttons))
        target_id = int(msg.text)
        if data == "add_admin":
            await add_admin(target_id)
            await msg.reply_text(f"✅ User `{target_id}` added as admin.", reply_markup=InlineKeyboardMarkup(buttons))
        else:
            await remove_admin(target_id)
            await msg.reply_text(f"✅ User `{target_id}` removed from admin.", reply_markup=InlineKeyboardMarkup(buttons))

    # -------------------------------
    # BAN / UNBAN USERS
    # -------------------------------
    elif data == "ban_user":
        buttons = [[InlineKeyboardButton("⬅ Back", callback_data="ban_menu")]]
        await query.message.edit_text(
            "<b>Send User ID to ban with optional reason:\nExample: 123456789 spam\nOr type /cancel to abort.</b>",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        msg = await listen_with_cancel(client, query.message.chat.id, timeout=300)
        if not msg:
            return await query.message.reply_text("❌ Action cancelled!", reply_markup=InlineKeyboardMarkup(buttons))
        parts = msg.text.split(maxsplit=1)
        if not parts[0].isdigit():
            return await msg.reply_text("❌ Invalid User ID", reply_markup=InlineKeyboardMarkup(buttons))
        uid = int(parts[0])
        reason = parts[1] if len(parts) > 1 else "No reason"
        await ban_user(uid, reason)
        await msg.reply_text(f"✅ User `{uid}` banned.\nReason: {reason}", reply_markup=InlineKeyboardMarkup(buttons))

    elif data == "unban_user":
        buttons = [[InlineKeyboardButton("⬅ Back", callback_data="ban_menu")]]
        await query.message.edit_text(
            "<b>Send User ID to unban.\nOr type /cancel to abort.</b>",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        msg = await listen_with_cancel(client, query.message.chat.id, timeout=300)
        if not msg:
            return await query.message.reply_text("❌ Action cancelled!", reply_markup=InlineKeyboardMarkup(buttons))
        if not msg.text.isdigit():
            return await msg.reply_text("❌ Invalid User ID", reply_markup=InlineKeyboardMarkup(buttons))
        uid = int(msg.text)
        await unban_user(uid)
        await msg.reply_text(f"✅ User `{uid}` unbanned.", reply_markup=InlineKeyboardMarkup(buttons))

    # -------------------------------
    # ADMIN LIST
    # -------------------------------
    elif data == "admin_list":
        admins_db = await admin_list()
        text = "🧑‍💼 **Admins**\n\n" + "\n".join([f"`{uid}`" for uid in admins_db])
        await query.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅ Back", callback_data="admin_menu")]])
        )

    # -------------------------------
    # BANNED LIST
    # -------------------------------
    elif data == "banned_list":
        users = await banned_users_list()
        text = "🚫 **Banned Users**\n\n"
        if users:
            for user in users:
                uid = user["_id"]
                reason = user.get("reason", "No reason")
                try:
                    user_obj = await client.get_users(uid)
                    name = user_obj.mention
                except:
                    name = f"`{uid}`"
                text += f"• {name} — {reason}\n"
        else:
            text += "No banned users."
        await query.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅ Back", callback_data="ban_menu")]])
        )

    # -------------------------------
    # COMMANDS PANEL
    # -------------------------------
    elif data == "commands":
        await query.message.edit_text(
            COMMANDS_TXT,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back to Help", callback_data="help")],
                [InlineKeyboardButton("⚓ Home", callback_data="start"),
                 InlineKeyboardButton("⚡ Close", callback_data="close")]
            ])
        )

    # -------------------------------
    # DISCLAIMER
    # -------------------------------
    elif data == "disclaimer":
        await query.message.edit_text(
            DISCLAIMER_TXT,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔰 About", callback_data="about")],
                [InlineKeyboardButton("⚓ Home", callback_data="start"),
                 InlineKeyboardButton("⚡ Close", callback_data="close")]
            ])
        )

    # -------------------------------
    # CLOSE
    # -------------------------------
    elif data == "close":
        await query.message.delete()
