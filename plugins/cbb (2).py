from pyrogram import Client
from bot import Bot
from config import *
from Script import COMMANDS_TXT, DISCLAIMER_TXT
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from database.database import ban_user, unban_user, banned_users_list
import asyncio
from pyrogram.errors import PeerIdInvalid
from pyromod import listen


@Bot.on_callback_query()
async def cb_handler(client: Bot, query: CallbackQuery):

    data = query.data
    user_id = query.from_user.id
    is_admin_user = user_id == OWNER_ID or user_id in ADMINS

    # Always answer callback to avoid "loading" state
    try:
        await query.answer()
    except:
        pass

    # Safe edit helper
    async def safe_edit(text, buttons=None, disable_preview=True):
        try:
            await query.message.edit_text(
                text=text,
                disable_web_page_preview=disable_preview,
                reply_markup=InlineKeyboardMarkup(buttons) if buttons else None
            )
        except:
            # fallback: send new message if editing fails
            await client.send_message(
                chat_id=query.message.chat.id,
                text=text,
                disable_web_page_preview=disable_preview,
                reply_markup=InlineKeyboardMarkup(buttons) if buttons else None
            )

    # -------------------------------
    # START PANEL
    # -------------------------------
    if data == "start":
        await safe_edit(
            text=START_MSG.format(first=query.from_user.first_name),
            buttons=[
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

    # -------------------------------
    # HELP PANEL
    # -------------------------------
    elif data == "help":
        await safe_edit(
            text=HELP_TXT.format(first=query.from_user.first_name),
            buttons=[
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

    # -------------------------------
    # ABOUT PANEL
    # -------------------------------
    elif data == "about":
        await safe_edit(
            text=ABOUT_TXT.format(first=query.from_user.first_name),
            buttons=[
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

    # -------------------------------
    # SETTINGS PANEL
    # -------------------------------
    elif data == "settings":
        if not is_admin_user:
            # View-only panel for non-admins
            await safe_edit(
                text=(
                    "⚙️ **Settings Panel (View Only)**\n\n"
                    "❌ You do not have admin rights to modify settings.\n"
                    f"- Owner: [{OWNER_ID}](tg://user?id={OWNER_ID})\n"
                    "- Only admins can access Ban Controls.\n"
                ),
                buttons=[[InlineKeyboardButton("⚓ Home", callback_data="start")]]
            )
            return

        await safe_edit(
            text="⚙️ **Bot Settings Panel**",
            buttons=[
                [InlineKeyboardButton("🚫 Ban Menu", callback_data="ban_menu")],
                [InlineKeyboardButton("⚓ Home", callback_data="start")]
            ]
        )

    # -------------------------------
    # BAN MENU
    # -------------------------------
    elif data == "ban_menu":
        if not is_admin_user:
            await safe_edit(
                text=(
                    "🚫 **Ban Control Panel (View Only)**\n\n"
                    "❌ You cannot ban/unban users.\n"
                    "- Only admins can manage users."
                ),
                buttons=[[InlineKeyboardButton("⚓ Home", callback_data="start")]]
            )
            return

        await safe_edit(
            text="🚫 **Ban Control Panel**",
            buttons=[
                [
                    InlineKeyboardButton("🚫 Ban User", callback_data="ban_user"),
                    InlineKeyboardButton("✅ Unban User", callback_data="unban_user")
                ],
                [InlineKeyboardButton("📋 Banned List", callback_data="banned_list")],
                [InlineKeyboardButton("⬅ Back", callback_data="settings")]
            ]
        )

    # -------------------------------
    # BAN USER
    # -------------------------------
    elif data == "ban_user":
        if not is_admin_user:
            await safe_edit(
                text="❌ You are not authorized to ban users.",
                buttons=[[InlineKeyboardButton("⚓ Home", callback_data="start")]]
            )
            return

        await safe_edit(
            text="Send **User ID and reason**\n\nExample:\n`123456789 spam`",
            buttons=[
                [
                    InlineKeyboardButton("⬅ Back", callback_data="ban_menu"),
                    InlineKeyboardButton("⚡ Close", callback_data="close")
                ]
            ]
        )

        try:
            msg = await client.listen(query.message.chat.id, timeout=120)
            parts = msg.text.split(maxsplit=1)
            if not parts[0].isdigit():
                return await client.send_message(chat_id=msg.chat.id, text="❌ Invalid user ID")

            uid = int(parts[0])
            reason = parts[1] if len(parts) > 1 else "No reason"
            await ban_user(uid, reason)

            # Send confirmation as new message
            await client.send_message(chat_id=msg.chat.id, text=f"✅ User `{uid}` banned\nReason: {reason}")
        except asyncio.TimeoutError:
            await client.send_message(chat_id=query.message.chat.id, text="⏰ Time expired")

    # -------------------------------
    # UNBAN USER
    # -------------------------------
    elif data == "unban_user":
        if not is_admin_user:
            await safe_edit(
                text="❌ You are not authorized to unban users.",
                buttons=[[InlineKeyboardButton("⚓ Home", callback_data="start")]]
            )
            return

        await safe_edit(
            text="Send **User ID** to unban",
            buttons=[
                [
                    InlineKeyboardButton("⬅ Back", callback_data="ban_menu"),
                    InlineKeyboardButton("⚡ Close", callback_data="close")
                ]
            ]
        )

        try:
            msg = await client.listen(query.message.chat.id, timeout=120)
            if not msg.text.isdigit():
                return await client.send_message(chat_id=msg.chat.id, text="❌ Invalid user ID")

            uid = int(msg.text)
            await unban_user(uid)

            # Send confirmation as new message
            await client.send_message(chat_id=msg.chat.id, text=f"✅ User `{uid}` unbanned")
        except asyncio.TimeoutError:
            await client.send_message(chat_id=query.message.chat.id, text="⏰ Time expired")

    # -------------------------------
    # BANNED LIST
    # -------------------------------
    elif data == "banned_list":
        if not is_admin_user:
            await safe_edit(
                text="❌ You are not authorized to view the banned list.",
                buttons=[[InlineKeyboardButton("⚓ Home", callback_data="start")]]
            )
            return

        users = await banned_users_list()
        text = "🚫 **Banned Users**\n\n" + ("No banned users." if not users else "")
        for user in users or []:
            uid = user["_id"]
            reason = user.get("reason", "No reason")
            try:
                user_obj = await client.get_users(uid)
                name = user_obj.mention
            except PeerIdInvalid:
                name = f"`{uid}`"
            text += f"• {name} — {reason}\n"

        await safe_edit(
            text=text,
            buttons=[
                [
                    InlineKeyboardButton("⬅ Back", callback_data="ban_menu"),
                    InlineKeyboardButton("⚡ Close", callback_data="close")
                ]
            ]
        )

    # -------------------------------
    # COMMANDS
    # -------------------------------
    elif data == "commands":
        await safe_edit(
            text=COMMANDS_TXT,
            buttons=[
                [InlineKeyboardButton("🔙 Back to Help", callback_data="help")],
                [
                    InlineKeyboardButton("⚓ Home", callback_data="start"),
                    InlineKeyboardButton("⚡ Close", callback_data="close")
                ]
            ]
        )

    # -------------------------------
    # DISCLAIMER
    # -------------------------------
    elif data == "disclaimer":
        await safe_edit(
            text=DISCLAIMER_TXT,
            buttons=[
                [InlineKeyboardButton("🔰 About", callback_data="about")],
                [
                    InlineKeyboardButton("⚓ Home", callback_data="start"),
                    InlineKeyboardButton("⚡ Close", callback_data="close")
                ]
            ]
        )

    # -------------------------------
    # CLOSE
    # -------------------------------
    elif data == "close":
        try:
            await query.message.delete()
        except:
            pass
