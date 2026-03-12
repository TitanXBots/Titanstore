from pyrogram import Client
from bot import Bot
from config import *
from Script import COMMANDS_TXT, DISCLAIMER_TXT
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from database.database import ban_user, unban_user, banned_users_list
from pyrogram.errors import PeerIdInvalid
from pyromod import listen
import asyncio


# -------------------------------
# PANEL FUNCTIONS
# -------------------------------

async def start_panel(query: CallbackQuery):
    try:
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
    except:
        pass


async def help_panel(query: CallbackQuery):
    try:
        await query.message.edit_text(
            text=HELP_TXT.format(first=query.from_user.first_name),
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("🧑‍💻 Contact Owner", user_id=OWNER_ID),
                        InlineKeyboardButton("💬 Commands", callback_data="commands")
                    ],
                    [
                        InlineKeyboardButton("⚓ Home", callback_data="start"),
                        InlineKeyboardButton("⚡ Close", callback_data="close")
                    ]
                ]
            )
        )
    except:
        pass


async def about_panel(query: CallbackQuery):
    try:
        await query.message.edit_text(
            text=ABOUT_TXT.format(first=query.from_user.first_name),
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("📜 Disclaimer", callback_data="disclaimer"),
                        InlineKeyboardButton("🔐 Source Code", url="https://github.com/TitanXBots/FileStore-Bot")
                    ],
                    [
                        InlineKeyboardButton("⚓ Home", callback_data="start"),
                        InlineKeyboardButton("⚡ Close", callback_data="close")
                    ]
                ]
            )
        )
    except:
        pass


async def commands_panel(query: CallbackQuery):
    try:
        await query.message.edit_text(
            text=COMMANDS_TXT,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("🔙 Back to Help", callback_data="help")],
                    [
                        InlineKeyboardButton("⚓ Home", callback_data="start"),
                        InlineKeyboardButton("⚡ Close", callback_data="close")
                    ]
                ]
            )
        )
    except:
        pass


async def disclaimer_panel(query: CallbackQuery):
    try:
        await query.message.edit_text(
            text=DISCLAIMER_TXT,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("🔰 About", callback_data="about")],
                    [
                        InlineKeyboardButton("⚓ Home", callback_data="start"),
                        InlineKeyboardButton("⚡ Close", callback_data="close")
                    ]
                ]
            )
        )
    except:
        pass


async def settings_panel(query: CallbackQuery, is_admin_user: bool):
    if not is_admin_user:
        return await query.answer("Admins only.", show_alert=True)

    buttons = [
        [InlineKeyboardButton("🚫 Ban Menu", callback_data="ban_menu")],
        [InlineKeyboardButton("⚓ Home", callback_data="start")]
    ]
    try:
        await query.message.edit_text(
            "⚙️ **Bot Settings Panel**",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    except:
        pass


async def ban_menu_panel(query: CallbackQuery, is_admin_user: bool):
    if not is_admin_user:
        return await query.answer("Admins only.", show_alert=True)

    buttons = [
        [
            InlineKeyboardButton("🚫 Ban User", callback_data="ban_user"),
            InlineKeyboardButton("✅ Unban User", callback_data="unban_user")
        ],
        [InlineKeyboardButton("📋 Banned List", callback_data="banned_list")],
        [InlineKeyboardButton("⬅ Back", callback_data="settings")]
    ]
    try:
        await query.message.edit_text(
            "🚫 **Ban Control Panel**",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    except:
        pass


async def banned_list_panel(query: CallbackQuery, client: Bot, is_admin_user: bool):
    if not is_admin_user:
        return await query.answer("Admins only.", show_alert=True)

    users = await banned_users_list()
    text = "🚫 **Banned Users**\n\n" + ("No banned users." if not users else "")

    if users:
        for user in users:
            uid = user["_id"]
            reason = user.get("reason", "No reason")
            try:
                user_obj = await client.get_users(uid)
                name = user_obj.mention
            except PeerIdInvalid:
                name = f"`{uid}`"
            text += f"• {name} — {reason}\n"

    buttons = [
        [InlineKeyboardButton("⬅ Back", callback_data="ban_menu")],
        [InlineKeyboardButton("⚡ Close", callback_data="close")]
    ]
    try:
        await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons))
    except:
        pass


async def close_panel(query: CallbackQuery):
    try:
        await query.message.delete()
    except:
        try:
            await query.message.edit_text("⚡ Closed")
        except:
            pass


# -------------------------------
# CALLBACK QUERY HANDLER
# -------------------------------

@Bot.on_callback_query()
async def cb_handler(client: Bot, query: CallbackQuery):

    user_id = query.from_user.id
    is_admin_user = user_id == OWNER_ID or user_id in ADMINS
    data = query.data

    try:
        await query.answer()
    except:
        pass

    # ROUTE TO PANEL FUNCTIONS
    if data == "start":
        await start_panel(query)

    elif data == "help":
        await help_panel(query)

    elif data == "about":
        await about_panel(query)

    elif data == "commands":
        await commands_panel(query)

    elif data == "disclaimer":
        await disclaimer_panel(query)

    elif data == "settings":
        await settings_panel(query, is_admin_user)

    elif data == "ban_menu":
        await ban_menu_panel(query, is_admin_user)

    elif data == "banned_list":
        await banned_list_panel(query, client, is_admin_user)

    elif data == "close":
        await close_panel(query)

    # -------------------------------
    # BAN USER
    # -------------------------------
    elif data == "ban_user":
        if not is_admin_user:
            return await query.answer("Admins only.", show_alert=True)

        await query.message.edit_text(
            "Send **User ID and reason**\n\nExample:\n`123456789 spam`",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("⬅ Back", callback_data="ban_menu"),
                        InlineKeyboardButton("⚡ Close", callback_data="close")
                    ]
                ]
            )
        )

        try:
            msg = await client.listen(query.message.chat.id, timeout=120)
            parts = msg.text.split(maxsplit=1)
            if not parts[0].isdigit():
                return await msg.reply_text("❌ Invalid user ID")
            uid = int(parts[0])
            reason = parts[1] if len(parts) > 1 else "No reason"
            await ban_user(uid, reason)
            await msg.reply_text(f"✅ User `{uid}` banned\nReason: {reason}")
        except asyncio.TimeoutError:
            await query.message.reply_text("⏰ Time expired")

    # -------------------------------
    # UNBAN USER
    # -------------------------------
    elif data == "unban_user":
        if not is_admin_user:
            return await query.answer("Admins only.", show_alert=True)

        await query.message.edit_text(
            "Send **User ID** to unban",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("⬅ Back", callback_data="ban_menu"),
                        InlineKeyboardButton("⚡ Close", callback_data="close")
                    ]
                ]
            )
        )

        try:
            msg = await client.listen(query.message.chat.id, timeout=120)
            if not msg.text.isdigit():
                return await msg.reply_text("❌ Invalid user ID")
            uid = int(msg.text)
            await unban_user(uid)
            await msg.reply_text(f"✅ User `{uid}` unbanned")
        except asyncio.TimeoutError:
            await query.message.reply_text("⏰ Time expired")
