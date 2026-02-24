from pyrogram import filters
from bot import Bot
from config import *
from Script import *
from pyrogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery
)

from database.database import (
    add_admin,
    remove_admin,
    list_admins
)

# =====================================================
# 🔥 CALLBACK HANDLER
# =====================================================

@Bot.on_callback_query()
async def cb_handler(client: Bot, query: CallbackQuery):
    data = query.data

    # =====================================================
    # 🏠 START MENU
    # =====================================================

    if data == "start":

        await query.message.edit_text(
            text=START_MSG.format(first=query.from_user.first_name),
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("☆ ᴍᴏᴠɪᴇ ʀᴇQᴜᴇꜱᴛ ɢʀᴏᴜᴘ ☆", url="https://t.me/TitanMoviess")
                    ],
                    [
                        InlineKeyboardButton("🧠 ʜᴇʟᴘ", callback_data="help"),
                        InlineKeyboardButton("🔰 ᴀʙᴏᴜᴛ", callback_data="about")
                    ],
                    [
                        InlineKeyboardButton("⚙️ ꜱᴇᴛᴛɪɴɢꜱ", callback_data="settings")
                    ],
                    [
                        InlineKeyboardButton("🤖 ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ", url="https://t.me/TitanXBots"),
                        InlineKeyboardButton("🔍 ꜱᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ", url="https://t.me/TitanMattersSupport")
                    ]
                ]
            )
        )

    # =====================================================
    # ⚙️ SETTINGS PANEL
    # =====================================================

    elif data == "settings":

        if query.from_user.id != OWNER_ID:
            return await query.answer("Access Denied!", show_alert=True)

        await query.message.edit_text(
            text="⚙️ <b>Premium Settings Panel</b>\n\nManage your bot configuration.",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("👑 ᴀᴅᴍɪɴ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ", callback_data="admin_panel")
                    ],
                    [
                        InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="start")
                    ]
                ]
            )
        )

    # =====================================================
    # 👑 ADMIN PANEL
    # =====================================================

    elif data == "admin_panel":

        await query.message.edit_text(
            text="👑 <b>Admin Management</b>\n\nSelect an option below:",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("➕ ᴀᴅᴅ ᴀᴅᴍɪɴ", callback_data="add_admin"),
                        InlineKeyboardButton("➖ ʀᴇᴍᴏᴠᴇ ᴀᴅᴍɪɴ", callback_data="remove_admin")
                    ],
                    [
                        InlineKeyboardButton("📋 ᴀᴅᴍɪɴ ʟɪꜱᴛ", callback_data="admin_list")
                    ],
                    [
                        InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="settings")
                    ]
                ]
            )
        )

    # =====================================================
    # 📋 ADMIN LIST
    # =====================================================

    elif data == "admin_list":

        admins = await list_admins()

        if not admins:
            text = "📭 No admins found."
        else:
            text = "<b>👑 Current Admins:</b>\n\n"
            text += "\n".join([f"• <code>{x}</code>" for x in admins])

        await query.message.edit_text(
            text=text,
            reply_markup=InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="admin_panel")]
                ]
            )
        )

    # =====================================================
    # ➕ ADD ADMIN
    # =====================================================

    elif data == "add_admin":

        client.add_admin_mode = query.from_user.id

        await query.message.edit_text(
            text="➕ <b>Add Admin</b>\n\nSend the <code>User ID</code> to add.\n\nType /cancel to stop.",
            reply_markup=InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="admin_panel")]
                ]
            )
        )

    # =====================================================
    # ➖ REMOVE ADMIN MENU
    # =====================================================

    elif data == "remove_admin":

        admins = await list_admins()

        if not admins:
            return await query.answer("No admins available.", show_alert=True)

        buttons = []

        for admin in admins:
            buttons.append(
                [InlineKeyboardButton(f"❌ {admin}", callback_data=f"confirm_remove_{admin}")]
            )

        buttons.append(
            [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="admin_panel")]
        )

        await query.message.edit_text(
            text="➖ <b>Select Admin to Remove:</b>",
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    # =====================================================
    # ⚠️ CONFIRM REMOVE
    # =====================================================

    elif data.startswith("confirm_remove_"):

        user_id = data.split("_")[-1]

        await query.message.edit_text(
            text=f"⚠️ Are you sure you want to remove admin <code>{user_id}</code>?",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("✅ ᴄᴏɴꜰɪʀᴍ", callback_data=f"remove_yes_{user_id}"),
                        InlineKeyboardButton("❌ ᴄᴀɴᴄᴇʟ", callback_data="remove_admin")
                    ]
                ]
            )
        )

    # =====================================================
    # ✅ FINAL REMOVE
    # =====================================================

    elif data.startswith("remove_yes_"):

        user_id = int(data.split("_")[-1])
        await remove_admin(user_id)

        await query.message.edit_text(
            text=f"❌ Admin <code>{user_id}</code> removed successfully.",
            reply_markup=InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="admin_panel")]
                ]
            )
        )

# =====================================================
# 📨 MESSAGE HANDLER FOR ADD ADMIN
# =====================================================

@Bot.on_message(filters.private & filters.text)
async def admin_input_handler(client: Bot, message: Message):

    if getattr(client, "add_admin_mode", None) != message.from_user.id:
        return

    if message.text.lower() == "/cancel":
        client.add_admin_mode = None
        return await message.reply_text("❌ Cancelled.")

    try:
        user_id = int(message.text.strip())
        await add_admin(user_id)
        client.add_admin_mode = None
        await message.reply_text(f"✅ User <code>{user_id}</code> added as admin.")
    except:
        await message.reply_text("⚠️ Invalid User ID.")
