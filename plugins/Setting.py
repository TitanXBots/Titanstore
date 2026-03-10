import asyncio
from bot import Bot
from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from config import OWNER_ID
from database.database import ban_user, unban_user, is_banned, get_ban_reason, banned_users
from database.database import is_admin
from pyrogram.errors import PeerIdInvalid

# SETTINGS COMMAND

@Bot.on_message(filters.command("settings") & filters.private)
async def settings_command(client, message: Message):

    user_id = message.from_user.id

    if not (user_id == OWNER_ID or await is_admin(user_id)):
        return await message.reply("You are not allowed to use this.")

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Ban Menu", callback_data="ban_menu")],
        [InlineKeyboardButton("Close", callback_data="close")]
    ])

    await message.reply(
        "⚙️ **Bot Settings Panel**",
        reply_markup=keyboard
    )


# CALLBACK HANDLER

@Bot.on_callback_query()
async def settings_callbacks(client: Bot, query):

    user_id = query.from_user.id
    data = query.data

    is_admin_user = user_id == OWNER_ID or await is_admin(user_id)

# CLOSE

    if data == "close":
        await query.message.delete()

# BAN MENU

    elif data == "ban_menu":

        if not is_admin_user:
            return await query.answer("Only admins allowed.", show_alert=True)

        btn = [
            [InlineKeyboardButton("Ban User", callback_data="ban_user"),
             InlineKeyboardButton("Unban User", callback_data="unban_user")],
            [InlineKeyboardButton("Banned List", callback_data="banned_list")],
            [InlineKeyboardButton("Back", callback_data="settings_back")]
        ]

        await query.message.edit_text(
            "🚫 **Ban Control Panel**",
            reply_markup=InlineKeyboardMarkup(btn)
        )

# BACK

    elif data == "settings_back":

        btn = [
            [InlineKeyboardButton("Ban Menu", callback_data="ban_menu")],
            [InlineKeyboardButton("Close", callback_data="close")]
        ]

        await query.message.edit_text(
            "⚙️ **Bot Settings Panel**",
            reply_markup=InlineKeyboardMarkup(btn)
        )

# BAN USER

    elif data == "ban_user":

        if not is_admin_user:
            return await query.answer("Admins only.", show_alert=True)

        btn = [[InlineKeyboardButton("Back", callback_data="ban_menu")]]

        await query.message.edit_text(
            "Send the **User ID** to ban.\n\nExample:\n`123456789 spam`",
            reply_markup=InlineKeyboardMarkup(btn)
        )

        try:

            msg = await client.listen(query.message.chat.id, timeout=120)

            parts = msg.text.split(maxsplit=1)

            uid = int(parts[0])
            reason = parts[1] if len(parts) > 1 else "No reason"

            await ban_user(uid, reason)

            await msg.reply(
                f"✅ User `{uid}` banned\nReason: {reason}",
                reply_markup=InlineKeyboardMarkup(btn)
            )

        except Exception as e:
            await query.message.reply(f"Error: {e}")

# UNBAN USER

    elif data == "unban_user":

        if not is_admin_user:
            return await query.answer("Admins only.", show_alert=True)

        btn = [[InlineKeyboardButton("Back", callback_data="ban_menu")]]

        await query.message.edit_text(
            "Send the **User ID** to unban.",
            reply_markup=InlineKeyboardMarkup(btn)
        )

        try:

            msg = await client.listen(query.message.chat.id, timeout=120)

            uid = int(msg.text)

            await unban_user(uid)

            await msg.reply(
                f"✅ User `{uid}` unbanned.",
                reply_markup=InlineKeyboardMarkup(btn)
            )

        except Exception as e:
            await query.message.reply(f"Error: {e}")

# BANNED LIST

    elif data == "banned_list":

        if not is_admin_user:
            return await query.answer("Admins only.", show_alert=True)

        users = banned_users.find()

        text = "🚫 **Banned Users**\n\n"
        count = 0

        for user in users:

            uid = user["_id"]
            reason = user.get("reason", "No reason")

            try:
                user_obj = await client.get_users(uid)
                name = user_obj.mention
            except PeerIdInvalid:
                name = f"`{uid}`"

            text += f"• {name} — {reason}\n"
            count += 1

        if count == 0:
            text = "No banned users."

        btn = [[InlineKeyboardButton("Back", callback_data="ban_menu")]]

        await query.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup(btn)
        )
