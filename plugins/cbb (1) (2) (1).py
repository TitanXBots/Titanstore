from bot import Bot
from config import *
from Script import COMMANDS_TXT, DISCLAIMER_TXT

from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors import MessageNotModified


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
# OWNER / ADMIN CHECK
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
            [
                InlineKeyboardButton("🧑‍💻 Contact Owner", user_id=OWNER_ID),
                InlineKeyboardButton("💬 Commands", callback_data="commands")
            ],
            [
                InlineKeyboardButton("🏠 Home", callback_data="start"),
                InlineKeyboardButton("❌ Close", callback_data="close")
            ]
        ])

        await safe_edit(
            query.message,
            HELP_TXT.format(first=query.from_user.first_name),
            buttons
        )

    # -------------------------------
    # ABOUT
    # -------------------------------
    elif data == "about":

        buttons = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("📜 Disclaimer", callback_data="disclaimer"),
                InlineKeyboardButton(
                    "🔐 Source",
                    url="https://github.com/TitanXBots/FileStore-Bot"
                )
            ],
            [
                InlineKeyboardButton("🏠 Home", callback_data="start"),
                InlineKeyboardButton("❌ Close", callback_data="close")
            ]
        ])

        await safe_edit(
            query.message,
            ABOUT_TXT.format(first=query.from_user.first_name),
            buttons
        )

    # -------------------------------
    # START MENU
    # -------------------------------
    elif data == "start":

        buttons = [
            [
                InlineKeyboardButton("🧠 Help", callback_data="help"),
                InlineKeyboardButton("📗 About", callback_data="about")
            ]
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
    # COMMANDS
    # -------------------------------
    elif data == "commands":

        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back", callback_data="help")],
            [
                InlineKeyboardButton("🏠 Home", callback_data="start"),
                InlineKeyboardButton("❌ Close", callback_data="close")
            ]
        ])

        await safe_edit(query.message, COMMANDS_TXT, buttons)

    # -------------------------------
    # DISCLAIMER
    # -------------------------------
    elif data == "disclaimer":

        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back", callback_data="about")],
            [
                InlineKeyboardButton("🏠 Home", callback_data="start"),
                InlineKeyboardButton("❌ Close", callback_data="close")
            ]
        ])

        await safe_edit(query.message, DISCLAIMER_TXT, buttons)

    # -------------------------------
    # SETTINGS
    # -------------------------------
    elif data == "settings":

        if not admin_status:
            await query.answer("⚠️ Only admins allowed.", show_alert=True)
            return

        buttons = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("👨‍💻 Admin Menu", callback_data="admin_menu"),
                InlineKeyboardButton("🚫 Ban Menu", callback_data="ban_menu")
            ],
            [
                InlineKeyboardButton("🔙 Back", callback_data="start")
            ]
        ])

        await safe_edit(
            query.message,
            "⚙️ **Admin Settings Panel**",
            buttons
        )

    # -------------------------------
    # ADMIN MENU
    # -------------------------------
    elif data == "admin_menu":

        if not admin_status:
            await query.answer("⚠️ Only admins allowed.", show_alert=True)
            return

        buttons = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("➕ Add Admin", callback_data="add_admin"),
                InlineKeyboardButton("➖ Remove Admin", callback_data="remove_admin")
            ],
            [
                InlineKeyboardButton("📜 Admin List", callback_data="admin_list")
            ],
            [
                InlineKeyboardButton("🔙 Back", callback_data="settings")
            ]
        ])

        await safe_edit(
            query.message,
            "👨‍💻 **Admin Management Panel**",
            buttons
        )

    # -------------------------------
    # BAN MENU
    # -------------------------------
    elif data == "ban_menu":

        if not admin_status:
            await query.answer("⚠️ Only admins allowed.", show_alert=True)
            return

        buttons = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🚫 Ban User", callback_data="ban_user"),
                InlineKeyboardButton("✅ Unban User", callback_data="unban_user")
            ],
            [
                InlineKeyboardButton("📋 Banned List", callback_data="banned_list")
            ],
            [
                InlineKeyboardButton("🔙 Back", callback_data="settings")
            ]
        ])

        await safe_edit(
            query.message,
            "🚫 **Ban Management Panel**",
            buttons
        )

    # -------------------------------
    # ADD ADMIN
    # -------------------------------
    elif data == "add_admin":

        if not admin_status:
            await query.answer("⚠️ Only admins allowed.", show_alert=True)
            return

        await query.answer("Use command: /addadmin user_id", show_alert=True)

    # -------------------------------
    # REMOVE ADMIN
    # -------------------------------
    elif data == "remove_admin":

        if not admin_status:
            await query.answer("⚠️ Only admins allowed.", show_alert=True)
            return

        await query.answer("Use command: /removeadmin user_id", show_alert=True)

    # -------------------------------
    # ADMIN LIST
    # -------------------------------
    elif data == "admin_list":

        if not admin_status:
            await query.answer("⚠️ Only admins allowed.", show_alert=True)
            return

        await query.answer("Use command: /adminlist", show_alert=True)

    # -------------------------------
    # BAN USER
    # -------------------------------
    elif data == "ban_user":

        if not admin_status:
            await query.answer("⚠️ Only admins allowed.", show_alert=True)
            return

        await query.answer("Use command: /ban user_id reason", show_alert=True)

    # -------------------------------
    # UNBAN USER
    # -------------------------------
    elif data == "unban_user":

        if not admin_status:
            await query.answer("⚠️ Only admins allowed.", show_alert=True)
            return

        await query.answer("Use command: /unban user_id", show_alert=True)

    # -------------------------------
    # BANNED LIST
    # -------------------------------
    elif data == "banned_list":

        if not admin_status:
            await query.answer("⚠️ Only admins allowed.", show_alert=True)
            return

        await query.answer("Use command: /banlist", show_alert=True)

    # -------------------------------
    # CLOSE
    # -------------------------------
    elif data == "close":

        await query.message.delete()

        try:
            await query.message.reply_to_message.delete()
        except:
            pass
