from bot import Bot
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from config import OWNER_ID, ADMINS
from database.database import is_admin, ban_user, unban_user, banned_users_list
import asyncio
import logging
from pyrogram.errors import PeerIdInvalid
from pyromod import listen

# ---------- CALLBACK HANDLER ----------
@Bot.on_callback_query()
async def cb_handler(client: Bot, query: CallbackQuery):
    user_id = query.from_user.id
    data = query.data

    try:
        await query.answer()
    except:
        pass

    is_admin_user = user_id == OWNER_ID or user_id in ADMINS or await is_admin(user_id)

    # -------------------------------
    # PANEL NAVIGATION
    # -------------------------------
    panels = {
        "start": lambda: start_panel(query),
        "help": lambda: help_panel(query),
        "about": lambda: about_panel(query),
        "commands": lambda: commands_panel(query),
        "disclaimer": lambda: disclaimer_panel(query)
    }

    if data in panels:
        await panels[data]()
        return

    # -------------------------------
    # SETTINGS PANEL
    # -------------------------------
    if data == "settings":
        if not is_admin_user:
            return await query.answer("Admins only.", show_alert=True)
        await settings_panel(query)

    # -------------------------------
    # BAN PANEL
    # -------------------------------
    elif data.startswith("ban"):
        if not is_admin_user:
            return await query.answer("Admins only.", show_alert=True)
        await handle_ban_panel(client, query, data)
    
    # CLOSE
    elif data == "close":
        await query.message.delete()

# ---------- PANELS ----------
async def start_panel(query): 
    buttons = [
        [InlineKeyboardButton("🧠 Help", callback_data="help"),
         InlineKeyboardButton("🔰 About", callback_data="about")],
        [InlineKeyboardButton("⚙️ Settings", callback_data="settings")]
    ]
    await query.message.edit_text(
        text=f"Hello, {query.from_user.first_name}!\nWelcome to the bot.",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

async def help_panel(query):
    buttons = [
        [InlineKeyboardButton("🧑‍💻 Contact Owner", user_id=OWNER_ID),
         InlineKeyboardButton("💬 Commands", callback_data="commands")],
        [InlineKeyboardButton("⚓ Home", callback_data="start"),
         InlineKeyboardButton("⚡ Close", callback_data="close")]
    ]
    await query.message.edit_text(text=HELP_TXT.format(first=query.from_user.first_name),
                                  disable_web_page_preview=True,
                                  reply_markup=InlineKeyboardMarkup(buttons))

async def about_panel(query):
    buttons = [
        [InlineKeyboardButton("📜 Disclaimer", callback_data="disclaimer"),
         InlineKeyboardButton("🔐 Source Code", url="https://github.com/TitanXBots/FileStore-Bot")],
        [InlineKeyboardButton("⚓ Home", callback_data="start"),
         InlineKeyboardButton("⚡ Close", callback_data="close")]
    ]
    await query.message.edit_text(text=ABOUT_TXT.format(first=query.from_user.first_name),
                                  disable_web_page_preview=True,
                                  reply_markup=InlineKeyboardMarkup(buttons))

async def commands_panel(query):
    buttons = [[InlineKeyboardButton("🔙 Back to Help", callback_data="help")],
               [InlineKeyboardButton("⚓ Home", callback_data="start"),
                InlineKeyboardButton("⚡ Close", callback_data="close")]]
    await query.message.edit_text(text=COMMANDS_TXT,
                                  disable_web_page_preview=True,
                                  reply_markup=InlineKeyboardMarkup(buttons))

async def disclaimer_panel(query):
    buttons = [[InlineKeyboardButton("🔰 About", callback_data="about")],
               [InlineKeyboardButton("⚓ Home", callback_data="start"),
                InlineKeyboardButton("⚡ Close", callback_data="close")]]
    await query.message.edit_text(text=DISCLAIMER_TXT,
                                  disable_web_page_preview=True,
                                  reply_markup=InlineKeyboardMarkup(buttons))

async def settings_panel(query):
    buttons = [
        [InlineKeyboardButton("🚫 Ban Menu", callback_data="ban_menu")],
        [InlineKeyboardButton("⬅ Back", callback_data="start"),
         InlineKeyboardButton("⚡ Close", callback_data="close")]
    ]
    await query.message.edit_text("⚙️ Bot Settings Panel", reply_markup=InlineKeyboardMarkup(buttons))

# ---------- BAN HANDLER ----------
async def handle_ban_panel(client, query, action):
    if action == "ban_menu":
        buttons = [
            [InlineKeyboardButton("🚫 Ban User", callback_data="ban_user"),
             InlineKeyboardButton("✅ Unban User", callback_data="unban_user")],
            [InlineKeyboardButton("📋 Banned List", callback_data="banned_list")],
            [InlineKeyboardButton("⬅ Back", callback_data="settings")]
        ]
        await query.message.edit_text("🚫 Ban Control Panel", reply_markup=InlineKeyboardMarkup(buttons))

    elif action == "ban_user":
        await query.message.edit_text(
            "Send **User ID and reason** (Example: `123456789 spam`)",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅ Back", callback_data="ban_menu"),
                                               InlineKeyboardButton("⚡ Close", callback_data="close")]])
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

    elif action == "unban_user":
        await query.message.edit_text(
            "Send **User ID** to unban",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅ Back", callback_data="ban_menu"),
                                               InlineKeyboardButton("⚡ Close", callback_data="close")]])
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

    elif action == "banned_list":
        users = await banned_users_list()
        text = "🚫 **Banned Users**\n\n"
        if not users:
            text += "No banned users."
        else:
            for user in users:
                uid = user["_id"]
                reason = user.get("reason", "No reason")
                try:
                    user_obj = await client.get_users(uid)
                    name = user_obj.mention
                except PeerIdInvalid:
                    name = f"`{uid}`"
                text += f"• {name} — {reason}\n"
        await query.message.edit_text(text,
                                      reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅ Back", callback_data="ban_menu"),
                                                                         InlineKeyboardButton("⚡ Close", callback_data="close")]]))
