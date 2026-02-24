from pyrogram import Client
from bot import Bot
from config import *
from Script import COMMANDS_TXT, DISCLAIMER_TXT
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from database.database import add_user, del_user, full_userbase, present_user
from main_file_name import get_setting, set_setting

@Bot.on_callback_query()
async def cb_handler(client: Bot, query: CallbackQuery):

    data = query.data

    # ================= HELP ================= #
    if data == "help":
        await query.message.edit_text(
            text=HELP_TXT.format(first=query.from_user.first_name),
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("💬 Commands", callback_data="commands")
                    ],
                    [
                        InlineKeyboardButton("⚓ Home", callback_data="start"),
                        InlineKeyboardButton("❌ Close", callback_data="close")
                    ]
                ]
            )
        )

    # ================= ABOUT ================= #
    elif data == "about":
        await query.message.edit_text(
            text=ABOUT_TXT.format(first=query.from_user.first_name),
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("📜 Disclaimer", callback_data="disclaimer")
                    ],
                    [
                        InlineKeyboardButton("⚓ Home", callback_data="start"),
                        InlineKeyboardButton("❌ Close", callback_data="close")
                    ]
                ]
            )
        )

    # ================= START ================= #
    elif data == "start":
        await query.message.edit_text(
            text=START_MSG.format(first=query.from_user.first_name),
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
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
        )

    # ================= SETTINGS PANEL ================= #
    elif data == "settings":

        auto_delete = await get_setting("auto_delete", True)
        maintenance = await get_setting("maintenance", False)

        auto_status = "🟢 ON" if auto_delete else "🔴 OFF"
        main_status = "🟢 ON" if maintenance else "🔴 OFF"

        await query.message.edit_text(
            text=(
                "⚙️ <b>ADVANCED BOT SETTINGS</b>\n\n"
                f"🗑 Auto Delete: {auto_status}\n"
                f"🛠 Maintenance Mode: {main_status}"
            ),
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("🗑 Toggle Auto Delete", callback_data="toggle_auto")
                    ],
                    [
                        InlineKeyboardButton("🛠 Toggle Maintenance", callback_data="toggle_maint")
                    ],
                    [
                        InlineKeyboardButton("⚓ Home", callback_data="start"),
                        InlineKeyboardButton("❌ Close", callback_data="close")
                    ]
                ]
            )
        )

    # ================= TOGGLE AUTO DELETE ================= #
    elif data == "toggle_auto":

        if query.from_user.id not in ADMINS:
            return await query.answer("Admin Only ❌", show_alert=True)

        current = await get_setting("auto_delete", True)
        await set_setting("auto_delete", not current)

        await query.answer("Auto Delete Updated ✅")
        await cb_handler(client, query)

    # ================= TOGGLE MAINTENANCE ================= #
    elif data == "toggle_maint":

        if query.from_user.id not in ADMINS:
            return await query.answer("Admin Only ❌", show_alert=True)

        current = await get_setting("maintenance", False)
        await set_setting("maintenance", not current)

        await query.answer("Maintenance Updated ✅")
        await cb_handler(client, query)

    # ================= CLOSE ================= #
    elif data == "close":
        await query.message.delete()
