from bot import Bot
from config import *
from Script import *
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors import MessageNotModified
from database.database import admins_collection, banned_users, is_admin
import asyncio

# -------------------------------
# CANCEL STATE
# -------------------------------
cancel_states = {}

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
# INPUT HELPER (WITH CANCEL BUTTON)
# -------------------------------
async def get_input(client, message, prompt):
    user_id = message.chat.id
    cancel_states[user_id] = False

    cancel_btn = InlineKeyboardMarkup([
        [InlineKeyboardButton("❌ Cancel", callback_data="cancel_input")]
    ])

    await message.edit_text(prompt, reply_markup=cancel_btn)

    try:
        while True:
            msg = await client.listen(message.chat.id, timeout=300)

            # ✅ If cancel pressed → stop immediately
            if cancel_states.get(user_id):
                cancel_states[user_id] = False
                return None

            if not msg.text:
                await msg.reply("❌ Invalid input!")
                continue

            if msg.text.lower() == "/cancel":
                return None

            return msg.text

    except asyncio.TimeoutError:
        await message.reply("⌛ Timeout! Try again.")
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
    # CANCEL BUTTON HANDLER (FIXED)
    # -------------------------------
    if data == "cancel_input":
        cancel_states[user_id] = True

        # 🔥 IMPORTANT: stop listener
        try:
            await client.stop_listening(query.message.chat.id)
        except:
            pass

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

        await safe_edit(
            query.message,
            START_MSG.format(first=query.from_user.first_name),
            InlineKeyboardMarkup(buttons)
        )

    # -------------------------------
    # HELP
    # -------------------------------
    elif data == "help":
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("🧑‍💻 Contact Owner", url=f"tg://user?id={OWNER_ID}"),
             InlineKeyboardButton("💬 Commands", callback_data="commands")],
            [InlineKeyboardButton("⚓ Home", callback_data="start"),
             InlineKeyboardButton("⚡ Close", callback_data="close")]
        ])

        await safe_edit(
            query.message,
            HELP_TXT.format(first=query.from_user.first_name),
            buttons
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

        text = await get_input(client, query.message, "Send user_id [reason]")
        if text is None:
            return

        parts = text.split(maxsplit=1)
        if not parts[0].isdigit():
            return await query.message.reply("❌ Invalid User ID!")

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

        text = await get_input(client, query.message, "Send user_id")
        if text is None or not text.isdigit():
            return

        uid = int(text)

        banned_users.update_one(
            {"_id": uid},
            {"$set": {"is_banned": False, "reason": ""}}
        )

        await query.message.reply(f"✅ User `{uid}` unbanned.")

    # -------------------------------
    # ADD ADMIN
    # -------------------------------
    elif data == "add_admin":
        if not admin_status:
            return await query.answer("⚠️ Admins only!", show_alert=True)

        text = await get_input(client, query.message, "Send user_id to add admin")
        if text is None or not text.isdigit():
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

        text = await get_input(client, query.message, "Send user_id to remove admin")
        if text is None or not text.isdigit():
            return

        uid = int(text)

        admins_collection.delete_one({"_id": uid})

        await query.message.reply(f"✅ User `{uid}` removed from admin.")

    # -------------------------------
    # CLOSE
    # -------------------------------
    elif data == "close":
        try:
            await query.message.delete()
        except:
            pass
