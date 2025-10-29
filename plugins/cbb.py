from pyrogram import Client
from bot import Bot
from config import *
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from database.database import add_user, del_user, full_userbase, present_user


# --- Global variable to control the join channels feature ---
JOIN_CHANNELS_ENABLED = True  # Default ON
ADMIN_USER_ID = int(os.environ.get("ADMIN_USER_ID", "5356695781"))


@Bot.on_callback_query()
async def cb_handler(client: Bot, query: CallbackQuery):
    data = query.data

    # ==========================================================
    #                      HELP SECTION
    # ==========================================================
    if data == "help":
        await query.message.edit_text(
            text=HELP_TXT.format(first=query.from_user.first_name),
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("⚓ ʜᴏᴍᴇ", callback_data="start"),
                        InlineKeyboardButton("⚡ ᴄʟᴏꜱᴇ", callback_data="close")
                    ]
                ]
            )
        )

    # ==========================================================
    #                      ABOUT SECTION
    # ==========================================================
    elif data == "about":
        await query.message.edit_text(
            text=ABOUT_TXT.format(first=query.from_user.first_name),
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("⚓ ʜᴏᴍᴇ", callback_data="start"),
                        InlineKeyboardButton("⚡ ᴄʟᴏꜱᴇ", callback_data="close")
                    ]
                ]
            )
        )

    # ==========================================================
    #                    DISCLAIMER SECTION
    # ==========================================================
    elif data == "disclaimer":
        await query.message.edit_text(
            text=DISCLAIMER_TXT.format(first=query.from_user.first_name),
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("⚓ ʜᴏᴍᴇ", callback_data="start"),
                        InlineKeyboardButton("⚡ ᴄʟᴏꜱᴇ", callback_data="close")
                    ]
                ]
            )
        )

    # ==========================================================
    #                    START / MAIN MENU
    # ==========================================================
    elif data == "start":
        await query.message.edit_text(
            text=START_MSG.format(first=query.from_user.first_name),
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("☆ ᴍᴏᴠɪᴇ ʀᴇQᴜᴇꜱᴛ ɢʀᴏᴜᴘ ☆", url="https://t.me/TitanMoviess")
                    ],
                    [
                        InlineKeyboardButton("🧠 ʜᴇʟᴘ", callback_data="help"),
                        InlineKeyboardButton("🔰 ᴀʙᴏᴜᴛ", callback_data="about")
                    ],
                    [
                        InlineKeyboardButton("⚠️ ᴅɪꜱᴄʟᴀɪᴍᴇʀ", callback_data="disclaimer")
                    ],
                    [
                        InlineKeyboardButton("🧩 ꜱᴇᴛᴛɪɴɢꜱ", callback_data="settings")
                    ],
                    [
                        InlineKeyboardButton("🧑‍💻 ᴄᴏɴᴛᴀᴄᴛ ᴏᴡɴᴇʀ", user_id=5356695781),
                        InlineKeyboardButton("🔐 ꜱᴏᴜʀᴄᴇ ᴄᴏᴅᴇ", url="https://github.com/TitanXBots/FileStore-Bot")
                    ],
                    [
                        InlineKeyboardButton("🤖 ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ", url="https://t.me/TitanXBots"),
                        InlineKeyboardButton("🔍 ꜱᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ", url="https://t.me/TitanMattersSupport")
                    ],
                    [
                        InlineKeyboardButton("ʜᴏᴡ ᴛᴏ ᴜꜱᴇ ʙᴏᴛ", url="https://t.me/TitanXBackup/33")
                    ]
                ]
            )
        )

    # ==========================================================
    #                    SETTINGS SECTION
    # ==========================================================
    elif data == "settings":
        if query.from_user.id != ADMIN_USER_ID:
            await query.answer("🚫 Only the admin can access settings.", show_alert=True)
            return

        text = (
            "⚙️ **ʙᴏᴛ ꜱᴇᴛᴛɪɴɢꜱ**\n\n"
            f"ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟꜱ ꜰᴇᴀᴛᴜʀᴇ: {'✅ ON' if JOIN_CHANNELS_ENABLED else '❌ OFF'}\n\n"
            "ᴘʀᴇꜱꜱ ʙᴇʟᴏᴡ ᴛᴏ ᴇɴᴀʙʟᴇ/ᴅɪꜱᴀʙʟᴇ 👇"
        )

        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    text=f"{'🟢 Disable' if JOIN_CHANNELS_ENABLED else '🟢 Enable'} Join Channels",
                    callback_data="toggle_joinchannels"
                )
            ],
            [
                InlineKeyboardButton("⚓ ʜᴏᴍᴇ", callback_data="start")
            ]
        ])

        await query.message.edit_text(text, reply_markup=keyboard)

    # ==========================================================
    #                    TOGGLE JOIN CHANNELS
    # ==========================================================
    elif data == "toggle_joinchannels":
        global JOIN_CHANNELS_ENABLED

        if query.from_user.id != ADMIN_USER_ID:
            await query.answer("🚫 You are not allowed to do this.", show_alert=True)
            return

        # Toggle ON/OFF
        JOIN_CHANNELS_ENABLED = not JOIN_CHANNELS_ENABLED

        new_text = (
            "⚙️ **ʙᴏᴛ ꜱᴇᴛᴛɪɴɢꜱ (ᴜᴘᴅᴀᴛᴇᴅ)**\n\n"
            f"ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟꜱ ꜰᴇᴀᴛᴜʀᴇ: {'✅ ON' if JOIN_CHANNELS_ENABLED else '❌ OFF'}\n\n"
            "ᴘʀᴇꜱꜱ ʙᴇʟᴏᴡ ᴛᴏ ᴇɴᴀʙʟᴇ/ᴅɪꜱᴀʙʟᴇ 👇"
        )

        new_keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    text=f"{'🟢 Disable' if JOIN_CHANNELS_ENABLED else '🟢 Enable'} Join Channels",
                    callback_data="toggle_joinchannels"
                )
            ],
            [
                InlineKeyboardButton("⚓ ʜᴏᴍᴇ", callback_data="start")
            ]
        ])

        await query.message.edit_text(new_text, reply_markup=new_keyboard)
        await query.answer("✅ Settings updated!")

    # ==========================================================
    #                       CLOSE SECTION
    # ==========================================================
    elif data == "close":
        await query.message.delete()
        try:
            await query.message.reply_to_message.delete()
        except:
            pass
