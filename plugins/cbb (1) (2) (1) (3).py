from bot import Bot
from config import *
from Script import *
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors import MessageNotModified
from database.database import admins_collection, banned_users, is_admin
import asyncio

# -------------------------------
# AUTO DELETE (1 MINUTE)
# -------------------------------
async def auto_delete(msg, delay=60):
    await asyncio.sleep(delay)
    try:
        await msg.delete()
    except:
        pass

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
        pass
    except:
        try:
            await message.reply_text(
                text=text,
                reply_markup=buttons,
                disable_web_page_preview=True
            )
        except:
            pass

# -------------------------------
# INPUT HELPER
# -------------------------------
async def get_input(client, message, prompt, back_data="start"):
    await message.edit_text(prompt)

    try:
        msg = await client.listen(message.chat.id, timeout=300)

        if not msg.text:
            m = await msg.reply(
                "❌ Invalid input!",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 Back", callback_data=back_data)]
                ])
            )
            asyncio.create_task(auto_delete(m))
            return None

        if msg.text.lower() == "/cancel":
            m = await msg.reply(
                "❌ Cancelled!",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 Back", callback_data=back_data)]
                ])
            )
            asyncio.create_task(auto_delete(m))
            return None

        return msg.text

    except asyncio.TimeoutError:
        m = await message.reply(
            "⌛ Timeout! Try again.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back", callback_data=back_data)]
            ])
        )
        asyncio.create_task(auto_delete(m))
        return None

# -------------------------------
# CALLBACK HANDLER
# -------------------------------
@Bot.on_callback_query()
async def cb_handler(client: Bot, query: CallbackQuery):

    await query.answer()

    if not query.message:
        return

    data = query.data
    user_id = query.from_user.id
    admin_status = await is_admin(user_id)

    # -------------------------------
    # START
    # -------------------------------
    if data == "start":
        buttons = [
            [InlineKeyboardButton("🧠 Help", callback_data="help"),
             InlineKeyboardButton("🔰 About", callback_data="about")]
        ]

        if admin_status:
            buttons.append([InlineKeyboardButton("⚙️ Settings", callback_data="settings")])

        await safe_edit(
            query.message,
            START_MSG.format(first=query.from_user.first_name),
            InlineKeyboardMarkup(buttons)
        )

    # -------------------------------
    # HELP
    # -------------------------------
    elif data == "help":
        await safe_edit(
            query.message,
            HELP_TXT.format(first=query.from_user.first_name),
            InlineKeyboardMarkup([
                [InlineKeyboardButton("🧑‍💻 Contact Owner", user_id=OWNER_ID),
                 InlineKeyboardButton("💬 Commands", callback_data="commands")],
                [InlineKeyboardButton("⚓ Home", callback_data="start"),
                 InlineKeyboardButton("⚡ Close", callback_data="close")]
            ])
        )

    # -------------------------------
    # COMMANDS
    # -------------------------------
    elif data == "commands":
        await safe_edit(
            query.message,
            COMMANDS_TXT,
            InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back", callback_data="help")],
                [InlineKeyboardButton("⚓ Home", callback_data="start"),
                 InlineKeyboardButton("⚡ Close", callback_data="close")]
            ])
        )

    # -------------------------------
    # ABOUT
    # -------------------------------
    elif data == "about":
        await safe_edit(
            query.message,
            ABOUT_TXT.format(first=query.from_user.first_name),
            InlineKeyboardMarkup([
                [InlineKeyboardButton("📜 Disclaimer", callback_data="disclaimer"),
                 InlineKeyboardButton("🔐 Source", url="https://github.com/TitanXBots/FileStore-Bot")],
                [InlineKeyboardButton("⚓ Home", callback_data="start"),
                 InlineKeyboardButton("⚡ Close", callback_data="close")]
            ])
        )

    # -------------------------------
    # DISCLAIMER
    # -------------------------------
    elif data == "disclaimer":
        await safe_edit(
            query.message,
            DISCLAIMER_TXT,
            InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back", callback_data="about")],
                [InlineKeyboardButton("⚓ Home", callback_data="start"),
                 InlineKeyboardButton("⚡ Close", callback_data="close")]
            ])
        )

    # -------------------------------
    # SETTINGS
    # -------------------------------
    elif data == "settings":
        if not admin_status:
            return await query.answer("⚠️ Admins only!", show_alert=True)

        await safe_edit(
            query.message,
            "⚙️ Admin Settings Panel",
            InlineKeyboardMarkup([
                [InlineKeyboardButton("👨‍💻 Admin Menu", callback_data="admin_menu"),
                 InlineKeyboardButton("🚫 Ban Menu", callback_data="ban_menu")],
                [InlineKeyboardButton("🔙 Back", callback_data="start")]
            ])
        )

    # -------------------------------
    # ADMIN MENU
    # -------------------------------
    elif data == "admin_menu":
        if not admin_status:
            return await query.answer("⚠️ Admins only!", show_alert=True)

        await safe_edit(
            query.message,
            "👨‍💻 Admin Management Panel",
            InlineKeyboardMarkup([
                [InlineKeyboardButton("➕ Add Admin", callback_data="add_admin"),
                 InlineKeyboardButton("➖ Remove Admin", callback_data="remove_admin")],
                [InlineKeyboardButton("📜 Admin List", callback_data="admin_list")],
                [InlineKeyboardButton("🔙 Back", callback_data="settings")]
            ])
        )

    # -------------------------------
    # BAN MENU
    # -------------------------------
    elif data == "ban_menu":
        if not admin_status:
            return await query.answer("⚠️ Admins only!", show_alert=True)

        await safe_edit(
            query.message,
            "🚫 Ban Management Panel",
            InlineKeyboardMarkup([
                [InlineKeyboardButton("🚫 Ban User", callback_data="ban_user"),
                 InlineKeyboardButton("✅ Unban User", callback_data="unban_user")],
                [InlineKeyboardButton("📋 Banned List", callback_data="banned_list")],
                [InlineKeyboardButton("🔙 Back", callback_data="settings")]
            ])
        )

    # -------------------------------
    # BAN USER
    # -------------------------------
    elif data == "ban_user":
        if not admin_status:
            return await query.answer("⚠️ Admins only!", show_alert=True)

        text = await get_input(client, query.message, "Send user_id [reason]", "ban_menu")
        if not text:
            return

        parts = text.split(maxsplit=1)
        if not parts[0].isdigit():
            m = await query.message.reply("❌ Invalid User ID!")
            asyncio.create_task(auto_delete(m))
            return

        uid = int(parts[0])
        reason = parts[1] if len(parts) > 1 else "No reason"

        banned_users.update_one(
            {"_id": uid},
            {"$set": {"is_banned": True, "reason": reason}},
            upsert=True
        )

        await query.message.reply(f"✅ User `{uid}` banned.\nReason: {reason}")

    # -------------------------------
    # UNBAN USER
    # -------------------------------
    elif data == "unban_user":
        if not admin_status:
            return await query.answer("⚠️ Admins only!", show_alert=True)

        text = await get_input(client, query.message, "Send user_id", "ban_menu")
        if not text or not text.isdigit():
            return

        uid = int(text)

        banned_users.update_one(
            {"_id": uid},
            {"$set": {"is_banned": False, "reason": ""}}
        )

        await query.message.reply(f"✅ User `{uid}` unbanned.")

    # -------------------------------
    # BANNED LIST
    # -------------------------------
    elif data == "banned_list":
        if not admin_status:
            return await query.answer("⚠️ Admins only!", show_alert=True)

        banned = list(banned_users.find({"is_banned": True}))

        if not banned:
            return await query.message.edit_text("No banned users.")

        text = "\n".join(
            [f"• {u['_id']} - {u.get('reason', 'No reason')}" for u in banned]
        )

        await query.message.edit_text(f"🚫 Banned Users:\n\n{text}")

    # -------------------------------
    # ADD ADMIN
    # -------------------------------
    elif data == "add_admin":
        if not admin_status:
            return await query.answer("⚠️ Admins only!", show_alert=True)

        text = await get_input(client, query.message, "Send user_id to add admin", "admin_menu")
        if not text or not text.isdigit():
            return

        uid = int(text)

        admins_collection.update_one(
            {"_id": uid},
            {"$set": {"is_admin": True}},
            upsert=True
        )

        await query.message.reply(f"✅ User `{uid}` added as admin.")

    # -------------------------------
    # REMOVE ADMIN
    # -------------------------------
    elif data == "remove_admin":
        if not admin_status:
            return await query.answer("⚠️ Admins only!", show_alert=True)

        text = await get_input(client, query.message, "Send user_id to remove admin", "admin_menu")
        if not text or not text.isdigit():
            return

        uid = int(text)

        admins_collection.delete_one({"_id": uid})

        await query.message.reply(f"✅ User `{uid}` removed from admin.")

    # -------------------------------
    # ADMIN LIST
    # -------------------------------
    elif data == "admin_list":
        if not admin_status:
            return await query.answer("⚠️ Admins only!", show_alert=True)

        admins = list(admins_collection.find({}))

        if not admins:
            return await query.message.edit_text("No admins found.")

        text = "\n".join([f"• {admin['_id']}" for admin in admins])

        await query.message.edit_text(f"👨‍💻 Admin List:\n\n{text}")

    # -------------------------------
    # CLOSE
    # -------------------------------
    elif data == "close":
        try:
            await query.message.delete()
        except:
            pass
