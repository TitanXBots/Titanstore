from bot import Bot
from config import *
from Script import COMMANDS_TXT, DISCLAIMER_TXT
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from database.database import add_admin, remove_admin, list_admins, ban_user, unban_user, banned_users_list

# -------------------------------
# STATE STORAGE
# -------------------------------

admin_state = {}


@Bot.on_callback_query()
async def cb_handler(client: Bot, query: CallbackQuery):

    data = query.data
    user_id = query.from_user.id

    try:
        await query.answer()
    except:
        pass

    is_admin_user = user_id == OWNER_ID or user_id in ADMINS

# -------------------------------
# START
# -------------------------------

    if data == "start":

        await query.message.edit_text(
            START_MSG.format(first=query.from_user.first_name),
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
                        InlineKeyboardButton("❌ Close", callback_data="close")
                    ]
                ]
            )
        )

# -------------------------------
# HELP
# -------------------------------

    elif data == "help":

        await query.message.edit_text(
            HELP_TXT.format(first=query.from_user.first_name),
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("💬 Commands", callback_data="commands")],
                    [
                        InlineKeyboardButton("⚓ Home", callback_data="start"),
                        InlineKeyboardButton("❌ Close", callback_data="close")
                    ]
                ]
            )
        )

# -------------------------------
# ABOUT
# -------------------------------

    elif data == "about":

        await query.message.edit_text(
            ABOUT_TXT.format(first=query.from_user.first_name),
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("📜 Disclaimer", callback_data="disclaimer")],
                    [
                        InlineKeyboardButton("⚓ Home", callback_data="start"),
                        InlineKeyboardButton("❌ Close", callback_data="close")
                    ]
                ]
            )
        )

# -------------------------------
# COMMANDS
# -------------------------------

    elif data == "commands":

        await query.message.edit_text(
            COMMANDS_TXT,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("🔙 Back", callback_data="help")]
                ]
            )
        )

# -------------------------------
# DISCLAIMER
# -------------------------------

    elif data == "disclaimer":

        await query.message.edit_text(
            DISCLAIMER_TXT,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("🔙 Back", callback_data="about")]
                ]
            )
        )

# -------------------------------
# SETTINGS
# -------------------------------

    elif data == "settings":

        if not is_admin_user:
            return await query.answer("Admins only.", show_alert=True)

        keyboard = [
            [InlineKeyboardButton("👑 Admin Menu", callback_data="admin_menu")],
            [InlineKeyboardButton("🚫 Ban Menu", callback_data="ban_menu")],
            [InlineKeyboardButton("⚓ Home", callback_data="start")]
        ]

        await query.message.edit_text(
            "⚙️ **Bot Settings Panel**",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

# -------------------------------
# ADMIN MENU
# -------------------------------

    elif data == "admin_menu":

        if user_id != OWNER_ID:
            return await query.answer("Owner only.", show_alert=True)

        keyboard = [
            [
                InlineKeyboardButton("➕ Add Admin", callback_data="add_admin_btn"),
                InlineKeyboardButton("➖ Remove Admin", callback_data="remove_admin_btn")
            ],
            [
                InlineKeyboardButton("📜 Admin List", callback_data="admin_list_btn")
            ],
            [
                InlineKeyboardButton("⬅ Back", callback_data="settings")
            ]
        ]

        await query.message.edit_text(
            "👑 **Admin Control Panel**",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

# -------------------------------
# ADD ADMIN
# -------------------------------

    elif data == "add_admin_btn":

        if user_id != OWNER_ID:
            return await query.answer("Owner only.", show_alert=True)

        admin_state[user_id] = "add_admin"

        await query.message.edit_text(
            "👤 Send **User ID** to add admin",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("❌ Cancel", callback_data="cancel")]]
            )
        )

# -------------------------------
# REMOVE ADMIN
# -------------------------------

    elif data == "remove_admin_btn":

        if user_id != OWNER_ID:
            return await query.answer("Owner only.", show_alert=True)

        admin_state[user_id] = "remove_admin"

        await query.message.edit_text(
            "👤 Send **User ID** to remove admin",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("❌ Cancel", callback_data="cancel")]]
            )
        )

# -------------------------------
# ADMIN LIST
# -------------------------------

    elif data == "admin_list_btn":

        admins = await list_admins()

        text = "👑 **Admin List**\n\n"

        if not admins:
            text += "No admins found."

        else:
            for admin in admins:
                text += f"• `{admin}`\n"

        await query.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("⬅ Back", callback_data="admin_menu"),
                        InlineKeyboardButton("❌ Close", callback_data="close")
                    ]
                ]
            )
        )

# -------------------------------
# BAN MENU
# -------------------------------

    elif data == "ban_menu":

        keyboard = [
            [
                InlineKeyboardButton("🚫 Ban User", callback_data="ban_user_btn"),
                InlineKeyboardButton("✅ Unban User", callback_data="unban_user_btn")
            ],
            [
                InlineKeyboardButton("📋 Banned List", callback_data="banned_list")
            ],
            [
                InlineKeyboardButton("⬅ Back", callback_data="settings")
            ]
        ]

        await query.message.edit_text(
            "🚫 **Ban Control Panel**",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

# -------------------------------
# BAN USER
# -------------------------------

    elif data == "ban_user_btn":

        admin_state[user_id] = "ban_user"

        await query.message.edit_text(
            "Send **User ID and reason**\n\nExample:\n`123456789 spam`",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("❌ Cancel", callback_data="cancel")]]
            )
        )

# -------------------------------
# UNBAN USER
# -------------------------------

    elif data == "unban_user_btn":

        admin_state[user_id] = "unban_user"

        await query.message.edit_text(
            "Send **User ID** to unban",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("❌ Cancel", callback_data="cancel")]]
            )
        )

# -------------------------------
# BANNED LIST
# -------------------------------

    elif data == "banned_list":

        users = await banned_users_list()

        text = "🚫 **Banned Users**\n\n"

        if not users:
            text += "No banned users."

        else:
            for user in users:
                uid = user["_id"]
                reason = user.get("reason", "No reason")
                text += f"• `{uid}` — {reason}\n"

        await query.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("⬅ Back", callback_data="ban_menu"),
                        InlineKeyboardButton("❌ Close", callback_data="close")
                    ]
                ]
            )
        )

# -------------------------------
# CANCEL
# -------------------------------

    elif data == "cancel":

        admin_state.pop(user_id, None)

        await query.message.edit_text(
            "❌ Operation cancelled.",
            reply_markup=InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("⚓ Home", callback_data="start")]
                ]
            )
        )

# -------------------------------
# CLOSE
# -------------------------------

    elif data == "close":
        await query.message.delete()
