from pyrogram import Client
from bot import Bot
from config import *
from Script import COMMANDS_TXT, DISCLAIMER_TXT
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from database.database import add_user, del_user, full_userbase, present_user
from database.database import ban_user, unban_user, banned_users, is_admin
from pyrogram.errors import PeerIdInvalid


@Bot.on_callback_query()
async def cb_handler(client: Bot, query: CallbackQuery):
    data = query.data

    if data == "help":
        await query.message.edit_text(
            text=HELP_TXT.format(first=query.from_user.first_name),
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("🧑‍💻 ᴄᴏɴᴛᴀᴄᴛ ᴏᴡɴᴇʀ", user_id=5356695781),
                        InlineKeyboardButton("💬 ᴄᴏᴍᴍᴀɴᴅꜱ", callback_data="commands")
                    ],
                    [
                        InlineKeyboardButton("⚓ ʜᴏᴍᴇ", callback_data="start"),
                        InlineKeyboardButton("⚡ ᴄʟᴏꜱᴇ", callback_data="close")
                    ]
                ]
            )
        )

    elif data == "about":
        await query.message.edit_text(
            text=ABOUT_TXT.format(first=query.from_user.first_name),
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("📜 ᴅɪꜱᴄʟᴀɪᴍᴇʀ", callback_data="disclaimer"),
                        InlineKeyboardButton("🔐 ꜱᴏᴜʀᴄᴇ ᴄᴏᴅᴇ", url="https://github.com/TitanXBots/FileStore-Bot")
                    ],
                    [
                        InlineKeyboardButton("⚓ ʜᴏᴍᴇ", callback_data="start"),
                        InlineKeyboardButton("⚡ ᴄʟᴏꜱᴇ", callback_data="close")
                    ]
                ]
            )
        )

    elif data == "start":  
        await query.message.edit_text(  
            text=START_MSG.format(first=query.from_user.first_name),  
            disable_web_page_preview=True,  
            reply_markup=InlineKeyboardMarkup(  
                [  
                    [  
                        InlineKeyboardButton("🧠 ʜᴇʟᴘ", callback_data="help"),  
                        InlineKeyboardButton("🔰 ᴀʙᴏᴜᴛ", callback_data="about")  
                    ],  
                    [  
                        InlineKeyboardButton("⚙️ ꜱᴇᴛᴛɪɴɢꜱ", callback_data="settings")  # <- New button added
                    ],  
                    [  
                        InlineKeyboardButton("🤖 ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ", url="https://t.me/TitanXBots"),  
                        InlineKeyboardButton("🔍 ꜱᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ", url="https://t.me/TitanMattersSupport")  
                    ]  
                ]  
            )  
        )

    elif data == "commands":
        await query.message.edit_text(
            text=COMMANDS_TXT,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("🔙 ʙᴀᴄᴋ ᴛᴏ ʜᴇʟᴘ", callback_data="help")
                    ],
                    [
                        InlineKeyboardButton("⚓ ʜᴏᴍᴇ", callback_data="start"),
                        InlineKeyboardButton("⚡ ᴄʟᴏꜱᴇ", callback_data="close")
                    ]
                ]
            )
        )

    elif data == "disclaimer":
        await query.message.edit_text(
            text=DISCLAIMER_TXT,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("🔰 ᴀʙᴏᴜᴛ", callback_data="about")
                    ],
                    [
                        InlineKeyboardButton("⚓ ʜᴏᴍᴇ", callback_data="start"),
                        InlineKeyboardButton("⚡ ᴄʟᴏꜱᴇ", callback_data="close")
                    ]
                ]
            )
        )

    elif data == "close":
        await query.message.delete()
        try:
            await query.message.reply_to_message.delete()
        except:
            pass




# -------------------------------
# CALLBACK HANDLER
# -------------------------------
async def settings_callbacks(client: Bot, query: CallbackQuery):

    await query.answer()

    user_id = query.from_user.id
    data = query.data

    is_admin_user = user_id == OWNER_ID or await is_admin(user_id)


# -------------------------------
# CLOSE
# -------------------------------

    if data == "close":
        return await query.message.delete()


# -------------------------------
# BAN MENU
# -------------------------------

    elif data == "ban_menu":

        if not is_admin_user:
            return await query.answer("Admins only.", show_alert=True)

        btn = [
            [
                InlineKeyboardButton("🚫 Ban User", callback_data="ban_user"),
                InlineKeyboardButton("✅ Unban User", callback_data="unban_user")
            ],
            [
                InlineKeyboardButton("📋 Banned List", callback_data="banned_list")
            ],
            [
                InlineKeyboardButton("⬅ Back", callback_data="settings_back")
            ]
        ]

        await query.message.edit_text(
            "🚫 **Ban Control Panel**",
            reply_markup=InlineKeyboardMarkup(btn)
        )


# -------------------------------
# BACK
# -------------------------------

    elif data == "settings_back":

        btn = [
            [InlineKeyboardButton("🚫 Ban Menu", callback_data="ban_menu")],
            [InlineKeyboardButton("❌ Close", callback_data="close")]
        ]

        await query.message.edit_text(
            "⚙️ **Bot Settings Panel**",
            reply_markup=InlineKeyboardMarkup(btn)
        )


# -------------------------------
# BAN USER
# -------------------------------

    elif data == "ban_user":

        if not is_admin_user:
            return await query.answer("Admins only.", show_alert=True)

        btn = [[InlineKeyboardButton("⬅ Back", callback_data="ban_menu")]]

        await query.message.edit_text(
            "Send **User ID** to ban.\n\nExample:\n`123456789 spam`",
            reply_markup=InlineKeyboardMarkup(btn)
        )

        try:

            msg = await client.listen(query.message.chat.id, timeout=120)

            if not msg.text:
                return await msg.reply("❌ Send valid user id")

            parts = msg.text.split(maxsplit=1)

            if not parts[0].isdigit():
                return await msg.reply("❌ Invalid user id")

            uid = int(parts[0])
            reason = parts[1] if len(parts) > 1 else "No reason"

            await ban_user(uid, reason)

            await msg.reply(
                f"✅ User `{uid}` banned\nReason: {reason}",
                reply_markup=InlineKeyboardMarkup(btn)
            )

        except asyncio.TimeoutError:
            await query.message.reply("⏰ Time expired")

        except Exception as e:
            await query.message.reply(f"Error: {e}")


# -------------------------------
# UNBAN USER
# -------------------------------

    elif data == "unban_user":

        if not is_admin_user:
            return await query.answer("Admins only.", show_alert=True)

        btn = [[InlineKeyboardButton("⬅ Back", callback_data="ban_menu")]]

        await query.message.edit_text(
            "Send **User ID** to unban.",
            reply_markup=InlineKeyboardMarkup(btn)
        )

        try:

            msg = await client.listen(query.message.chat.id, timeout=120)

            if not msg.text or not msg.text.isdigit():
                return await msg.reply("❌ Invalid user id")

            uid = int(msg.text)

            await unban_user(uid)

            await msg.reply(
                f"✅ User `{uid}` unbanned",
                reply_markup=InlineKeyboardMarkup(btn)
            )

        except asyncio.TimeoutError:
            await query.message.reply("⏰ Time expired")

        except Exception as e:
            await query.message.reply(f"Error: {e}")


# -------------------------------
# BANNED LIST
# -------------------------------

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

        btn = [[InlineKeyboardButton("⬅ Back", callback_data="ban_menu")]]

        await query.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup(btn)
                                     )
