from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import OWNER_ID
from database.database import add_admin, remove_admin, list_admins, is_admin

# ===============================
# SETTINGS MAIN MENU
# ===============================

@Client.on_message(filters.command("settings") & filters.private)
async def settings_menu(client, message):

    if message.from_user.id != OWNER_ID:
        return await message.reply_text("⛔ Access Denied.")

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("➕ Add Admin", callback_data="add_admin"),
            InlineKeyboardButton("➖ Remove Admin", callback_data="remove_admin")
        ],
        [
            InlineKeyboardButton("📋 Admin List", callback_data="admin_list")
        ],
        [
            InlineKeyboardButton("🔙 Back", callback_data="back_main")
        ]
    ])

    await message.reply_text(
        "<b>⚙️ Admin Management Panel</b>\n\n"
        "Manage your bot administrators easily.\n"
        "Select an option below:",
        reply_markup=keyboard
    )

# ===============================
# ADD ADMIN BUTTON
# ===============================

@Client.on_callback_query(filters.regex("add_admin"))
async def add_admin_button(client, callback_query):

    if callback_query.from_user.id != OWNER_ID:
        return await callback_query.answer("Not allowed", show_alert=True)

    await callback_query.message.edit_text(
        "<b>➕ Add New Admin</b>\n\n"
        "Send the <code>User ID</code> of the user you want to promote.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back", callback_data="settings_menu")]
        ])
    )

    client.admin_state = {"action": "add"}

@Client.on_message(filters.private & filters.text)
async def handle_admin_input(client, message):

    if message.from_user.id != OWNER_ID:
        return

    if not hasattr(client, "admin_state"):
        return

    if client.admin_state.get("action") == "add":

        try:
            user_id = int(message.text)
            await add_admin(user_id)

            await message.reply_text(
                f"✅ <b>Admin Added Successfully</b>\n\n"
                f"👤 User ID: <code>{user_id}</code>",
            )

        except ValueError:
            await message.reply_text("⚠️ Invalid User ID format.")

        client.admin_state = {}
# ===============================
# REMOVE ADMIN MENU
# ===============================

@Client.on_callback_query(filters.regex("remove_admin"))
async def remove_admin_menu(client, callback_query):

    if callback_query.from_user.id != OWNER_ID:
        return await callback_query.answer("Not allowed", show_alert=True)

    admins = await list_admins()

    if not admins:
        return await callback_query.answer("No admins found.", show_alert=True)

    buttons = []

    for admin in admins:
        buttons.append(
            [InlineKeyboardButton(f"👤 {admin}", callback_data=f"confirm_remove_{admin}")]
        )

    buttons.append([InlineKeyboardButton("🔙 Back", callback_data="settings_menu")])

    await callback_query.message.edit_text(
        "<b>➖ Remove Admin</b>\n\n"
        "Select an admin to remove:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

@Client.on_callback_query(filters.regex("confirm_remove_"))
async def confirm_remove(client, callback_query):

    if callback_query.from_user.id != OWNER_ID:
        return await callback_query.answer("Not allowed", show_alert=True)

    user_id = int(callback_query.data.split("_")[-1])

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Yes, Remove", callback_data=f"remove_{user_id}"),
            InlineKeyboardButton("❌ Cancel", callback_data="remove_admin")
        ]
    ])

    await callback_query.message.edit_text(
        f"<b>⚠️ Confirm Removal</b>\n\n"
        f"Are you sure you want to remove:\n"
        f"<code>{user_id}</code> ?",
        reply_markup=keyboard
    )


@Client.on_callback_query(filters.regex("remove_"))
async def remove_admin_final(client, callback_query):

    if callback_query.from_user.id != OWNER_ID:
        return await callback_query.answer("Not allowed", show_alert=True)

    user_id = int(callback_query.data.split("_")[-1])

    await remove_admin(user_id)

    await callback_query.message.edit_text(
        f"❌ <b>Admin Removed Successfully</b>\n\n"
        f"👤 User ID: <code>{user_id}</code>",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back to Settings", callback_data="settings_menu")]
        ])
    )


@Client.on_callback_query(filters.regex("admin_list"))
async def admin_list_button(client, callback_query):

    if callback_query.from_user.id != OWNER_ID and not await is_admin(callback_query.from_user.id):
        return await callback_query.answer("Access Denied", show_alert=True)

    admins = await list_admins()

    if not admins:
        text = "📭 No admins found."
    else:
        text = "<b>👑 Current Admins</b>\n\n"
        text += "\n".join([f"• <code>{x}</code>" for x in admins])

    await callback_query.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back", callback_data="settings_menu")]
        ])
    )



@Client.on_callback_query(filters.regex("settings_menu|back_main"))
async def back_to_settings(client, callback_query):

    if callback_query.from_user.id != OWNER_ID:
        return await callback_query.answer("Access Denied", show_alert=True)

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("➕ Add Admin", callback_data="add_admin"),
            InlineKeyboardButton("➖ Remove Admin", callback_data="remove_admin")
        ],
        [
            InlineKeyboardButton("📋 Admin List", callback_data="admin_list")
        ]
    ])

    await callback_query.message.edit_text(
        "<b>⚙️ Admin Management Panel</b>\n\n"
        "Manage your bot administrators easily.\n"
        "Select an option below:",
        reply_markup=keyboard
    )
    
