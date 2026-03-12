from pyrogram import Client
from bot import Bot
from config import *
from Script import COMMANDS_TXT, DISCLAIMER_TXT
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from database.database import ban_user, unban_user, banned_users_list

@Bot.on_callback_query()
async def cb_handler(client: Bot, query: CallbackQuery):
    data = query.data  
    user_id = query.from_user.id  

    try:  
        await query.answer()  
    except:  
        pass  

    # OWNER + ADMIN CHECK  
    is_admin_user = user_id == OWNER_ID or user_id in ADMINS

    # -------------------------------
    # HELP
    # -------------------------------
    if data == "help":  
        await query.message.edit_text(
            text=HELP_TXT.format(first=query.from_user.first_name),
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🧑‍💻 Contact Owner", user_id=OWNER_ID),
                 InlineKeyboardButton("💬 Commands", callback_data="commands")],
                [InlineKeyboardButton("⚓ Home", callback_data="start"),
                 InlineKeyboardButton("⚡ Close", callback_data="close")]
            ])
        )

    # -------------------------------
    # ABOUT
    # -------------------------------
    elif data == "about":  
        await query.message.edit_text(
            text=ABOUT_TXT.format(first=query.from_user.first_name),
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📜 Disclaimer", callback_data="disclaimer"),
                 InlineKeyboardButton("🔐 Source Code", url="https://github.com/TitanXBots/FileStore-Bot")],
                [InlineKeyboardButton("⚓ Home", callback_data="start"),
                 InlineKeyboardButton("⚡ Close", callback_data="close")]
            ])
        )

    # -------------------------------
    # START PANEL
    # -------------------------------
    elif data == "start":  
        await query.message.edit_text(
            text=START_MSG.format(first=query.from_user.first_name),
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🧠 Help", callback_data="help"),
                 InlineKeyboardButton("🔰 About", callback_data="about")],
                [InlineKeyboardButton("⚙️ Settings", callback_data="settings")],
                [InlineKeyboardButton("🤖 Update Channel", url="https://t.me/TitanXBots"),
                 InlineKeyboardButton("🔍 Support Group", url="https://t.me/TitanMattersSupport")]
            ])
        )

    # -------------------------------
    # SETTINGS PANEL
    # -------------------------------
    elif data == "settings":  
        if not is_admin_user:  
            return await query.answer("Admins only.", show_alert=True)

        buttons = [
            [InlineKeyboardButton("🚫 Ban Menu", callback_data="ban_menu")],
            [InlineKeyboardButton("⚓ Home", callback_data="start")]
        ]
        await query.message.edit_text("⚙️ **Bot Settings Panel**", reply_markup=InlineKeyboardMarkup(buttons))

    # -------------------------------
    # BAN MENU
    # -------------------------------
    elif data == "ban_menu":  
        if not is_admin_user:  
            return await query.answer("Admins only.", show_alert=True)

        buttons = [
            [InlineKeyboardButton("🚫 Ban User", callback_data="ban_user"),
             InlineKeyboardButton("✅ Unban User", callback_data="unban_user")],
            [InlineKeyboardButton("📋 Banned List", callback_data="banned_list")],
            [InlineKeyboardButton("⬅ Back", callback_data="settings")]
        ]
        await query.message.edit_text("🚫 **Ban Control Panel**", reply_markup=InlineKeyboardMarkup(buttons))

    # -------------------------------
    # BAN USER (direct action removed listen)
    # -------------------------------
    elif data == "ban_user":  
        if not is_admin_user:  
            return await query.answer("Admins only.", show_alert=True)

        await query.message.edit_text(
            "🚫 To ban a user, send:\n`/ban <user_id> <reason>`\nExample:\n`/ban 123456789 spam`",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅ Back", callback_data="ban_menu"),
                                                InlineKeyboardButton("⚡ Close", callback_data="close")]])
        )

    # -------------------------------
    # UNBAN USER (direct action removed listen)
    # -------------------------------
    elif data == "unban_user":  
        if not is_admin_user:  
            return await query.answer("Admins only.", show_alert=True)

        await query.message.edit_text(
            "✅ To unban a user, send:\n`/unban <user_id>`",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅ Back", callback_data="ban_menu"),
                                                InlineKeyboardButton("⚡ Close", callback_data="close")]])
        )

    # -------------------------------
    # BANNED LIST
    # -------------------------------
    elif data == "banned_list":  
        if not is_admin_user:  
            return await query.answer("Admins only.", show_alert=True)

        users = await banned_users_list()
        text = "🚫 **Banned Users**\n\n" or "No banned users."
        if users:
            text = "🚫 **Banned Users**\n\n"
            for user in users:
                uid = user["_id"]
                reason = user.get("reason", "No reason")
                try:
                    user_obj = await client.get_users(uid)
                    name = user_obj.mention
                except:
                    name = f"`{uid}`"
                text += f"• {name} — {reason}\n"
        else:
            text = "No banned users."

        await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("⬅ Back", callback_data="ban_menu"),
             InlineKeyboardButton("⚡ Close", callback_data="close")]
        ]))

    # -------------------------------
    # COMMANDS
    # -------------------------------
    elif data == "commands":  
        await query.message.edit_text(
            text=COMMANDS_TXT,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back to Help", callback_data="help")],
                [InlineKeyboardButton("⚓ Home", callback_data="start"),
                 InlineKeyboardButton("⚡ Close", callback_data="close")]
            ])
        )

    # -------------------------------
    # DISCLAIMER
    # -------------------------------
    elif data == "disclaimer":  
        await query.message.edit_text(
            text=DISCLAIMER_TXT,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔰 About", callback_data="about")],
                [InlineKeyboardButton("⚓ Home", callback_data="start"),
                 InlineKeyboardButton("⚡ Close", callback_data="close")]
            ])
        )

    # -------------------------------
    # CLOSE
    # -------------------------------
    elif data == "close":  
        await query.message.delete()
