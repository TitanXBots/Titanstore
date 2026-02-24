from config import OWNER_ID
from database.database import add_admin, remove_admin, list_admins
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from bot import Bot


@Bot.on_callback_query()
async def cb_handler(client: Bot, query: CallbackQuery):
    data = query.data

    # ==============================
    # CLOSE
    # ==============================
    if data == "close":
        await query.message.delete()
        try:
            await query.message.reply_to_message.delete()
        except:
            pass

    # ==============================
    # START MENU
    # ==============================
    elif data == "start":

        buttons = [
            [
                InlineKeyboardButton("☆ ᴍᴏᴠɪᴇ ʀᴇQᴜᴇꜱᴛ ɢʀᴏᴜᴘ ☆", url="https://t.me/TitanMoviess")
            ],
            [
                InlineKeyboardButton("🧠 ʜᴇʟᴘ", callback_data="help"),
                InlineKeyboardButton("🔰 ᴀʙᴏᴜᴛ", callback_data="about")
            ],
            [
                InlineKeyboardButton("🤖 ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ", url="https://t.me/TitanXBots"),
                InlineKeyboardButton("🔍 ꜱᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ", url="https://t.me/TitanMattersSupport")
            ],
            [
                InlineKeyboardButton("ʜᴏᴡ ᴛᴏ ᴜꜱᴇ ʙᴏᴛ", url="https://t.me/TitanXBackup/33")
            ]
        ]

        # 👑 Owner Only Admin Button
        if query.from_user.id == OWNER_ID:
            buttons.append(
                [InlineKeyboardButton("⚙️ ᴀᴅᴍɪɴ ꜱᴇᴛᴛɪɴɢꜱ", callback_data="admin_settings")]
            )

        await query.message.edit_text(
            text=START_MSG.format(first=query.from_user.first_name),
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    # ==============================
    # HELP
    # ==============================
    elif data == "help":
        await query.message.edit_text(
            text=HELP_TXT.format(first=query.from_user.first_name),
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("🧑‍💻 ᴄᴏɴᴛᴀᴄᴛ ᴏᴡɴᴇʀ", user_id=OWNER_ID),
                        InlineKeyboardButton("💬 ᴄᴏᴍᴍᴀɴᴅꜱ", callback_data="commands")
                    ],
                    [
                        InlineKeyboardButton("⚓ ʜᴏᴍᴇ", callback_data="start"),
                        InlineKeyboardButton("⚡ ᴄʟᴏꜱᴇ", callback_data="close")
                    ]
                ]
            )
        )

    # ==============================
    # ABOUT
    # ==============================
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

    # ==============================
    # COMMANDS
    # ==============================
    elif data == "commands":
        await query.message.edit_text(
            text=COMMANDS_TXT,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("🔙 ʙᴀᴄᴋ ᴛᴏ ʜᴇʟᴘ", callback_data="help")],
                    [
                        InlineKeyboardButton("⚓ ʜᴏᴍᴇ", callback_data="start"),
                        InlineKeyboardButton("⚡ ᴄʟᴏꜱᴇ", callback_data="close")
                    ]
                ]
            )
        )

    # ==============================
    # DISCLAIMER
    # ==============================
    elif data == "disclaimer":
        await query.message.edit_text(
            text=DISCLAIMER_TXT,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("🔰 ᴀʙᴏᴜᴛ", callback_data="about")],
                    [
                        InlineKeyboardButton("⚓ ʜᴏᴍᴇ", callback_data="start"),
                        InlineKeyboardButton("⚡ ᴄʟᴏꜱᴇ", callback_data="close")
                    ]
                ]
            )
        )

    # ==============================
    # ADMIN SETTINGS PANEL
    # ==============================
    elif data == "admin_settings":

        if query.from_user.id != OWNER_ID:
            return await query.answer("Access Denied", show_alert=True)

        await query.message.edit_text(
            "<b>⚙️ ᴀᴅᴍɪɴ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ ᴘᴀɴᴇʟ</b>\n\n"
            "Manage administrators below.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("➕ ᴀᴅᴅ ᴀᴅᴍɪɴ", callback_data="add_admin")],
                [InlineKeyboardButton("➖ ʀᴇᴍᴏᴠᴇ ᴀᴅᴍɪɴ", callback_data="remove_admin")],
                [InlineKeyboardButton("📋 ᴀᴅᴍɪɴ ʟɪꜱᴛ", callback_data="admin_list")],
                [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="start")]
            ])
        )

    # ==============================
    # ADD ADMIN
    # ==============================
    elif data == "add_admin":

        if query.from_user.id != OWNER_ID:
            return await query.answer("Access Denied", show_alert=True)

        client.admin_state = {"action": "add"}

        await query.message.edit_text(
            "<b>➕ ᴀᴅᴅ ɴᴇᴡ ᴀᴅᴍɪɴ</b>\n\n"
            "Send the <code>User ID</code> to promote.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="admin_settings")]
            ])
        )

    # ==============================
    # REMOVE ADMIN MENU
    # ==============================
    elif data == "remove_admin":

        if query.from_user.id != OWNER_ID:
            return await query.answer("Access Denied", show_alert=True)

        admins = await list_admins()

        if not admins:
            return await query.answer("No admins found.", show_alert=True)

        buttons = [
            [InlineKeyboardButton(f"👤 {x}", callback_data=f"confirm_remove_{x}")]
            for x in admins
        ]

        buttons.append([InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="admin_settings")])

        await query.message.edit_text(
            "<b>➖ ꜱᴇʟᴇᴄᴛ ᴀɴ ᴀᴅᴍɪɴ ᴛᴏ ʀᴇᴍᴏᴠᴇ</b>",
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    # ==============================
    # CONFIRM REMOVE
    # ==============================
    elif data.startswith("confirm_remove_"):

        user_id = int(data.split("_")[-1])

        await query.message.edit_text(
            f"<b>⚠️ ᴄᴏɴꜰɪʀᴍ ʀᴇᴍᴏᴠᴀʟ</b>\n\n"
            f"Remove admin:\n<code>{user_id}</code> ?",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("✅ ʏᴇꜱ", callback_data=f"remove_{user_id}"),
                    InlineKeyboardButton("❌ ɴᴏ", callback_data="remove_admin")
                ]
            ])
        )

    # ==============================
    # FINAL REMOVE
    # ==============================
    elif data.startswith("remove_"):

        user_id = int(data.split("_")[-1])
        await remove_admin(user_id)

        await query.message.edit_text(
            f"❌ <b>ᴀᴅᴍɪɴ ʀᴇᴍᴏᴠᴇᴅ</b>\n\n"
            f"👤 <code>{user_id}</code>",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="admin_settings")]
            ])
        )

    # ==============================
    # ADMIN LIST
    # ==============================
    elif data == "admin_list":

        admins = await list_admins()

        if not admins:
            text = "📭 No admins found."
        else:
            text = "<b>👑 ᴄᴜʀʀᴇɴᴛ ᴀᴅᴍɪɴꜱ</b>\n\n"
            text += "\n".join([f"• <code>{x}</code>" for x in admins])

        await query.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="admin_settings")]
            ])
        )

