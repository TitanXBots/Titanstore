from bot import Bot
from config import *
from Script import *
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors import MessageNotModified
from database.database import admins_collection, banned_users, is_admin

# -------------------------------
# USER STATE (IMPORTANT)
# -------------------------------
user_states = {}

# -------------------------------
# SAFE MESSAGE EDIT
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
        user_states.pop(user_id, None)

        return await safe_edit(
            query.message,
            "❌ Operation cancelled.",
            InlineKeyboardMarkup([
                [InlineKeyboardButton("⚓ Home", callback_data="start")]
            ])
        )

    # -------------------------------
    # START
    # -------------------------------
    if data == "start":
        buttons = [
            [InlineKeyboardButton("🧠 Help", callback_data="help"),
             InlineKeyboardButton("🔰 About", callback_data="about")]
        ]

        if admin_status:
            buttons.append(
                [InlineKeyboardButton("⚙️ Settings", callback_data="settings")]
            )

        await safe_edit(
            query.message,
            START_MSG.format(first=query.from_user.first_name),
            InlineKeyboardMarkup(buttons)
        )

    # -------------------------------
    # HELP
    # -------------------------------
    elif data == "help":
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("🧑‍💻 Contact Owner", url=f"tg://user?id={OWNER_ID}"),
             InlineKeyboardButton("💬 Commands", callback_data="commands")],
            [InlineKeyboardButton("⚓ Home", callback_data="start"),
             InlineKeyboardButton("⚡ Close", callback_data="close")]
        ])

        await safe_edit(
            query.message,
            HELP_TXT.format(first=query.from_user.first_name),
            buttons
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
                [InlineKeyboardButton("📜 Disclaimer", callback_data="disclaimer"),
                 InlineKeyboardButton("🔐 Source", url="https://github.com/TitanXBots/FileStore-Bot")],
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
                [InlineKeyboardButton("🔙 Back", callback_data="about")],
                [InlineKeyboardButton("⚓ Home", callback_data="start"),
                 InlineKeyboardButton("⚡ Close", callback_data="close")]
            ])
        )

    # -------------------------------
    # SETTINGS
    # -------------------------------
    elif data == "settings":
        if not admin_status:
            return await query.answer("⚠️ Admins only!", show_alert=True)

        await safe_edit(
            query.message,
            "⚙️ Admin Settings Panel",
            InlineKeyboardMarkup([
                [InlineKeyboardButton("👨‍💻 Admin Menu", callback_data="admin_menu"),
                 InlineKeyboardButton("🚫 Ban Menu", callback_data="ban_menu")],
                [InlineKeyboardButton("🔙 Back", callback_data="start")]
            ])
        )

    # -------------------------------
    # ADMIN MENU
    # -------------------------------
    elif data == "admin_menu":
        if not admin_status:
            return await query.answer("⚠️ Admins only!", show_alert=True)

        await safe_edit(
            query.message,
            "👨‍💻 Admin Management Panel",
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
            return await query.answer("⚠️ Admins only!", show_alert=True)

        await safe_edit(
            query.message,
            "🚫 Ban Management Panel",
            InlineKeyboardMarkup([
                [InlineKeyboardButton("🚫 Ban User", callback_data="ban_user"),
                 InlineKeyboardButton("✅ Unban User", callback_data="unban_user")],
                [InlineKeyboardButton("📋 Banned List", callback_data="banned_list")],
                [InlineKeyboardButton("🔙 Back", callback_data="settings")]
            ])
        )

    # -------------------------------
    # STATE SETTERS
    # -------------------------------
    elif data == "ban_user":
        user_states[user_id] = "ban_user"

        return await safe_edit(
            query.message,
            "Send user_id [reason]",
            InlineKeyboardMarkup([
                [InlineKeyboardButton("❌ Cancel", callback_data="cancel_input")]
            ])
        )

    elif data == "unban_user":
        user_states[user_id] = "unban_user"

        return await safe_edit(
            query.message,
            "Send user_id",
            InlineKeyboardMarkup([
                [InlineKeyboardButton("❌ Cancel", callback_data="cancel_input")]
            ])
        )

    elif data == "add_admin":
        user_states[user_id] = "add_admin"

        return await safe_edit(
            query.message,
            "Send user_id to add admin",
            InlineKeyboardMarkup([
                [InlineKeyboardButton("❌ Cancel", callback_data="cancel_input")]
            ])
        )

    elif data == "remove_admin":
        user_states[user_id] = "remove_admin"

        return await safe_edit(
            query.message,
            "Send user_id to remove admin",
            InlineKeyboardMarkup([
                [InlineKeyboardButton("❌ Cancel", callback_data="cancel_input")]
            ])
        )

    # -------------------------------
    # BANNED LIST
    # -------------------------------
    elif data == "banned_list":
        if not admin_status:
            return await query.answer("⚠️ Admins only!", show_alert=True)

        banned = list(banned_users.find({"is_banned": True}))

        if not banned:
            return await query.message.edit_text(
                "🚫 No banned users.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 Back", callback_data="ban_menu")]
                ])
            )

        text = "\n".join(
            [f"• {u['_id']} - {u.get('reason', 'No reason')}" for u in banned]
        )

        await query.message.edit_text(
            f"🚫 Banned Users:\n\n{text}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back", callback_data="ban_menu")]
            ])
        )

    # -------------------------------
    # ADMIN LIST
    # -------------------------------
    elif data == "admin_list":
        if not admin_status:
            return await query.answer("⚠️ Admins only!", show_alert=True)

        admins = list(admins_collection.find({}))

        if not admins:
            return await query.message.edit_text(
                "👨‍💻 No admins found.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 Back", callback_data="admin_menu")]
                ])
            )

        text = "\n".join([f"• {admin['_id']}" for admin in admins])

        await query.message.edit_text(
            f"👨‍💻 Admin List:\n\n{text}",
            reply_markup=InlineKeyboardMarkup([
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
