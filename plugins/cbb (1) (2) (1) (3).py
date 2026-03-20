from bot import Bot
from config import *
from Script import *
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors import MessageNotModified
from database.database import admins_collection, banned_users, is_admin

# -------------------------------
# USER STATE
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
        return
    except Exception:
        try:
            await message.reply_text(
                text=text,
                reply_markup=buttons,
                disable_web_page_preview=True
            )
        except Exception:
            pass


# -------------------------------
# CALLBACK HANDLER
# -------------------------------
@Bot.on_callback_query()
async def cb_handler(client: Bot, query: CallbackQuery):

    try:
        await query.answer()
    except:
        pass

    if not query.message or not query.data:
        return

    data = query.data.strip()
    user_id = query.from_user.id

    # Safe admin check
    try:
        admin_status = await is_admin(user_id)
    except:
        admin_status = False

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

        return await safe_edit(
            query.message,
            START_MSG.format(first=query.from_user.first_name),
            InlineKeyboardMarkup(buttons)
        )

    # -------------------------------
    # HELP
    # -------------------------------
    if data == "help":
        return await safe_edit(
            query.message,
            HELP_TXT.format(first=query.from_user.first_name),
            InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("🧑‍💻 Contact Owner", url=f"tg://user?id={OWNER_ID}"),
                    InlineKeyboardButton("💬 Commands", callback_data="commands")
                ],
                [
                    InlineKeyboardButton("⚓ Home", callback_data="start"),
                    InlineKeyboardButton("⚡ Close", callback_data="close")
                ]
            ])
        )

    # -------------------------------
    # COMMANDS
    # -------------------------------
    if data == "commands":
        return await safe_edit(
            query.message,
            COMMANDS_TXT,
            InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back", callback_data="help")],
                [
                    InlineKeyboardButton("⚓ Home", callback_data="start"),
                    InlineKeyboardButton("⚡ Close", callback_data="close")
                ]
            ])
        )

    # -------------------------------
    # ABOUT
    # -------------------------------
    if data == "about":
        return await safe_edit(
            query.message,
            ABOUT_TXT.format(first=query.from_user.first_name),
            InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("📜 Disclaimer", callback_data="disclaimer"),
                    InlineKeyboardButton("🔐 Source", url="https://github.com/TitanXBots/FileStore-Bot")
                ],
                [
                    InlineKeyboardButton("⚓ Home", callback_data="start"),
                    InlineKeyboardButton("⚡ Close", callback_data="close")
                ]
            ])
        )

    # -------------------------------
    # DISCLAIMER
    # -------------------------------
    if data == "disclaimer":
        return await safe_edit(
            query.message,
            DISCLAIMER_TXT,
            InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back", callback_data="about")],
                [
                    InlineKeyboardButton("⚓ Home", callback_data="start"),
                    InlineKeyboardButton("⚡ Close", callback_data="close")
                ]
            ])
        )

    # -------------------------------
    # SETTINGS
    # -------------------------------
    if data == "settings":
        if not admin_status:
            return await query.answer("⚠️ Admins only!", show_alert=True)

        return await safe_edit(
            query.message,
            "⚙️ Admin Settings Panel",
            InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("👨‍💻 Admin Menu", callback_data="admin_menu"),
                    InlineKeyboardButton("🚫 Ban Menu", callback_data="ban_menu")
                ],
                [InlineKeyboardButton("🔙 Back", callback_data="start")]
            ])
        )

    # -------------------------------
    # ADMIN MENU
    # -------------------------------
    if data == "admin_menu":
        if not admin_status:
            return await query.answer("⚠️ Admins only!", show_alert=True)

        return await safe_edit(
            query.message,
            "👨‍💻 Admin Management Panel",
            InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("➕ Add Admin", callback_data="add_admin"),
                    InlineKeyboardButton("➖ Remove Admin", callback_data="remove_admin")
                ],
                [InlineKeyboardButton("📜 Admin List", callback_data="admin_list")],
                [InlineKeyboardButton("🔙 Back", callback_data="settings")]
            ])
        )

    # -------------------------------
    # BAN MENU
    # -------------------------------
    if data == "ban_menu":
        if not admin_status:
            return await query.answer("⚠️ Admins only!", show_alert=True)

        return await safe_edit(
            query.message,
            "🚫 Ban Management Panel",
            InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("🚫 Ban User", callback_data="ban_user"),
                    InlineKeyboardButton("✅ Unban User", callback_data="unban_user")
                ],
                [InlineKeyboardButton("📋 Banned List", callback_data="banned_list")],
                [InlineKeyboardButton("🔙 Back", callback_data="settings")]
            ])
        )

    # -------------------------------
    # STATE SETTERS
    # -------------------------------
    if data in ["ban_user", "unban_user", "add_admin", "remove_admin"]:
        if not admin_status:
            return await query.answer("⚠️ Admins only!", show_alert=True)

        user_states[user_id] = data

        prompts = {
            "ban_user": "Send user_id [reason]",
            "unban_user": "Send user_id",
            "add_admin": "Send user_id to add admin",
            "remove_admin": "Send user_id to remove admin"
        }

        return await safe_edit(
            query.message,
            prompts[data],
            InlineKeyboardMarkup([
                [InlineKeyboardButton("❌ Cancel", callback_data="cancel_input")]
            ])
        )

    # -------------------------------
    # ADMIN LIST
    # -------------------------------
    if data == "admin_list":
        if not admin_status:
            return await query.answer("⚠️ Admins only!", show_alert=True)

        admins = list(admins_collection.find({}, {"_id": 1}))

        if not admins:
            return await safe_edit(
                query.message,
                "👨‍💻 No admins found.",
                InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 Back", callback_data="admin_menu")]
                ])
            )

        text = "\n".join([f"• {str(admin['_id'])}" for admin in admins])

        return await safe_edit(
            query.message,
            f"👨‍💻 Admin List:\n\n{text}",
            InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back", callback_data="admin_menu")]
            ])
        )

    # -------------------------------
    # BANNED LIST
    # -------------------------------
    if data == "banned_list":
        if not admin_status:
            return await query.answer("⚠️ Admins only!", show_alert=True)

        banned = list(banned_users.find({"is_banned": True}))

        if not banned:
            return await safe_edit(
                query.message,
                "🚫 No banned users.",
                InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 Back", callback_data="ban_menu")]
                ])
            )

        text = "\n".join([
            f"• {str(u['_id'])} - {u.get('reason', 'No reason')}"
            for u in banned
        ])

        return await safe_edit(
            query.message,
            f"🚫 Banned Users:\n\n{text}",
            InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back", callback_data="ban_menu")]
            ])
        )

    # -------------------------------
    # CLOSE
    # -------------------------------
    if data == "close":
        try:
            await query.message.delete()
        except:
            pass
