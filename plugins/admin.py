# TitanXBots - Premium Admin Settings UI

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from config import OWNER_ID
from database.database import add_admin, remove_admin, list_admins, is_admin

# -------------------------------
# SETTINGS MENU ENTRY
# -------------------------------

@Client.on_message(filters.command("settings") & filters.private)
async def settings_menu(client, message):

    if message.from_user.id != OWNER_ID:
        return await message.reply_text("⛔ Access Denied.")

    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("👑 Admin Management", callback_data="admin_panel")]
    ])

    await message.reply_text(
        "⚙️ <b>Settings Panel</b>\n\nManage your bot configuration.",
        reply_markup=buttons
    )


# -------------------------------
# ADMIN PANEL
# -------------------------------

@Client.on_callback_query(filters.regex("^admin_panel$"))
async def admin_panel(client, query: CallbackQuery):

    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("➕ Add Admin", callback_data="add_admin"),
            InlineKeyboardButton("➖ Remove Admin", callback_data="remove_admin")
        ],
        [
            InlineKeyboardButton("📋 Admin List", callback_data="admin_list")
        ],
        [
            InlineKeyboardButton("🔙 Back", callback_data="back_settings")
        ]
    ])

    await query.message.edit_text(
        "👑 <b>Admin Management Panel</b>\n\nSelect an option below:",
        reply_markup=buttons
    )


# -------------------------------
# ADMIN LIST
# -------------------------------

@Client.on_callback_query(filters.regex("^admin_list$"))
async def admin_list_callback(client, query: CallbackQuery):

    admins = await list_admins()

    if not admins:
        text = "📭 No admins found."
    else:
        text = "<b>👑 Current Admins:</b>\n\n"
        text += "\n".join([f"• <code>{x}</code>" for x in admins])

    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Back", callback_data="admin_panel")]
    ])

    await query.message.edit_text(text, reply_markup=buttons)


# -------------------------------
# ADD ADMIN (Step 1: Ask ID)
# -------------------------------

@Client.on_callback_query(filters.regex("^add_admin$"))
async def ask_add_admin(client, query: CallbackQuery):

    await query.message.edit_text(
        "➕ <b>Add Admin</b>\n\nSend the <code>User ID</code> to add as admin.\n\n🔙 Press /cancel to stop."
    )

    client.add_admin_mode = query.from_user.id


@Client.on_message(filters.private & filters.text)
async def receive_admin_id(client, message):

    if getattr(client, "add_admin_mode", None) != message.from_user.id:
        return

    try:
        user_id = int(message.text.strip())
        await add_admin(user_id)
        await message.reply_text(f"✅ User <code>{user_id}</code> added as admin.")
        client.add_admin_mode = None
    except:
        await message.reply_text("⚠️ Invalid User ID.")


# -------------------------------
# REMOVE ADMIN (Step 1: Show List)
# -------------------------------

@Client.on_callback_query(filters.regex("^remove_admin$"))
async def remove_admin_menu(client, query: CallbackQuery):

    admins = await list_admins()

    if not admins:
        return await query.answer("No admins available.", show_alert=True)

    buttons = [
        [InlineKeyboardButton(f"❌ {x}", callback_data=f"confirm_remove_{x}")]
        for x in admins
    ]

    buttons.append([InlineKeyboardButton("🔙 Back", callback_data="admin_panel")])

    await query.message.edit_text(
        "➖ <b>Select Admin to Remove:</b>",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


# -------------------------------
# CONFIRM REMOVE
# -------------------------------

@Client.on_callback_query(filters.regex("^confirm_remove_"))
async def confirm_remove(client, query: CallbackQuery):

    user_id = query.data.split("_")[-1]

    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Confirm", callback_data=f"remove_yes_{user_id}"),
            InlineKeyboardButton("❌ Cancel", callback_data="remove_admin")
        ]
    ])

    await query.message.edit_text(
        f"⚠️ Are you sure you want to remove admin <code>{user_id}</code>?",
        reply_markup=buttons
    )


@Client.on_callback_query(filters.regex("^remove_yes_"))
async def remove_admin_confirmed(client, query: CallbackQuery):

    user_id = int(query.data.split("_")[-1])
    await remove_admin(user_id)

    await query.message.edit_text(
        f"❌ Admin <code>{user_id}</code> removed successfully."
    )


# -------------------------------
# BACK BUTTON
# -------------------------------

@Client.on_callback_query(filters.regex("^back_settings$"))
async def back_settings(client, query: CallbackQuery):

    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("👑 Admin Management", callback_data="admin_panel")]
    ])

    await query.message.edit_text(
        "⚙️ <b>Settings Panel</b>\n\nManage your bot configuration.",
        reply_markup=buttons
    )
