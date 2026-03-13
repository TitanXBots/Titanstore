# cb_handler.py (Admin settings without auto-delete)
from pyrogram import Client
from bot import Bot
from config import *
from Script import COMMANDS_TXT, DISCLAIMER_TXT
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from database.database import is_admin

@Bot.on_callback_query()
async def cb_handler(client: Bot, query: CallbackQuery):
    data = query.data
    user_id = query.from_user.id

    # Check if user is admin
    admin_status = is_admin(user_id)

    if data == "help":
        await query.message.edit_text(
            text=HELP_TXT.format(first=query.from_user.first_name),
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("🧑‍💻 ᴄᴏɴᴛᴀᴄᴛ ᴏᴡɴᴇʀ", user_id=5356695781),
                        InlineKeyboardButton("💬 ᴄᴏᴍᴍᴀɴᴅꜱ", callback_data="commands")
                    ],
                    [
                        InlineKeyboardButton("⚓ ʜᴏᴍᴇ", callback_data="start"),
                        InlineKeyboardButton("⚡ ᴄʟᴏꜱᴇ", callback_data="close")
                    ]
                ]
            )
        )

    elif data == "about":
        await query.message.edit_text(
            text=ABOUT_TXT.format(first=query.from_user.first_name),
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("📜 ᴅɪꜱᴄʟᴀɪᴍᴇʀ", callback_data="disclaimer"),
                        InlineKeyboardButton("🔐 ꜱᴏᴜʀᴄᴇ ᴄᴏᴅᴇ", url="https://github.com/TitanXBots/FileStore-Bot")
                    ],
                    [
                        InlineKeyboardButton("⚓ ʜᴏᴍᴇ", callback_data="start"),
                        InlineKeyboardButton("⚡ ᴄʟᴏꜱᴇ", callback_data="close")
                    ]
                ]
            )
        )

    elif data == "start":
        buttons = [
            [
                InlineKeyboardButton("🧠 ʜᴇʟᴘ", callback_data="help"),
                InlineKeyboardButton("🔰 ᴀʙᴏᴜᴛ", callback_data="about")
            ]
        ]
        # Show Settings button only for admins
        if admin_status:
            buttons.append([InlineKeyboardButton("⚙️ ꜱᴇᴛᴛɪɴɢꜱ", callback_data="settings")])

        await query.message.edit_text(
            text=START_MSG.format(first=query.from_user.first_name),
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    elif data == "commands":
        await query.message.edit_text(
            text=COMMANDS_TXT,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("🔙 ʙᴀᴄᴋ ᴛᴏ ʜᴇʟᴘ", callback_data="help")],
                    [InlineKeyboardButton("⚓ ʜᴏᴍᴇ", callback_data="start"),
                     InlineKeyboardButton("⚡ ᴄʟᴏꜱᴇ", callback_data="close")]
                ]
            )
        )

    elif data == "disclaimer":
        await query.message.edit_text(
            text=DISCLAIMER_TXT,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("🔰 ᴀʙᴏᴜᴛ", callback_data="about")],
                    [InlineKeyboardButton("⚓ ʜᴏᴍᴇ", callback_data="start"),
                     InlineKeyboardButton("⚡ ᴄʟᴏꜱᴇ", callback_data="close")]
                ]
            )
        )

    elif data == "settings":
        if not admin_status:
            await query.answer("⚠️ You are not allowed to access this.", show_alert=True)
            return

        # Simple placeholder menu for admins
        buttons = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("🔙 Back", callback_data="disclaimer")]
            ]
        )
        await query.message.edit_text(
            "⚙️ ᴛʜɪꜱ ɪꜱ ᴛʜᴇ ꜱᴇᴛᴛɪɴɢꜱ ᴍᴇɴᴜ. Admin options will appear here.",
            reply_markup=buttons
        )

    elif data == "close":
        await query.message.delete()
        try:
            await query.message.reply_to_message.delete()
        except:
            pass
