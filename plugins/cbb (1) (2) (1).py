from bot import Bot
from config import *
from Script import COMMANDS_TXT, DISCLAIMER_TXT

from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors import MessageNotModified

from start import set_auto_delete
from database.database import add_admin, remove_admin, list_admins


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
    return user_id == OWNER_ID or user_id in ADMINS


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
                InlineKeyboardButton("🔐 Source", url="https://github.com/TitanXBots/FileStore-Bot")
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
    # SETTINGS PANEL
    # -------------------------------
    elif data == "settings":

        if user_id != OWNER_ID:
            await query.answer("⚠️ Only owner allowed.", show_alert=True)
            return

        buttons = InlineKeyboardMarkup([

            [
                InlineKeyboardButton("🟢 Auto Delete ON", callback_data="autodel_on"),
                InlineKeyboardButton("🔴 Auto Delete OFF", callback_data="autodel_off")
            ],

            [
                InlineKeyboardButton("➕ Add Admin", callback_data="add_admin"),
                InlineKeyboardButton("➖ Remove Admin", callback_data="remove_admin")
            ],

            [
                InlineKeyboardButton("📜 Admin List", callback_data="admin_list")
            ],

            [
                InlineKeyboardButton("🔙 Back", callback_data="start")
            ]

        ])

        await safe_edit(
            query.message,
            "⚙️ **Admin Settings Panel**\n\nManage bot settings and admins.",
            buttons
        )

    # -------------------------------
    # AUTO DELETE ON
    # -------------------------------
    elif data == "autodel_on":

        if user_id != OWNER_ID:
            await query.answer("Only owner allowed", show_alert=True)
            return

        set_auto_delete(True)

        await query.answer("✅ Auto Delete Enabled")

    # -------------------------------
    # AUTO DELETE OFF
    # -------------------------------
    elif data == "autodel_off":

        if user_id != OWNER_ID:
            await query.answer("Only owner allowed", show_alert=True)
            return

        set_auto_delete(False)

        await query.answer("❌ Auto Delete Disabled")

    # -------------------------------
    # ADMIN LIST
    # -------------------------------
    elif data == "admin_list":

        admins = await list_admins()

        if not admins:
            text = "No admins found."
        else:
            text = "**👮 Admin List**\n\n"
            for admin in admins:
                text += f"• `{admin}`\n"

        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back", callback_data="settings")]
        ])

        await safe_edit(query.message, text, buttons)

    # -------------------------------
    # ADD ADMIN BUTTON
    # -------------------------------
    elif data == "add_admin":

        await query.message.reply_text(
            "Send this command to add admin:\n\n`/addadmin USER_ID`",
            quote=True
        )

    # -------------------------------
    # REMOVE ADMIN BUTTON
    # -------------------------------
    elif data == "remove_admin":

        await query.message.reply_text(
            "Send this command to remove admin:\n\n`/removeadmin USER_ID`",
            quote=True
        )

    # -------------------------------
    # CLOSE
    # -------------------------------
    elif data == "close":

        await query.message.delete()

        try:
            await query.message.reply_to_message.delete()
        except:
            pass
