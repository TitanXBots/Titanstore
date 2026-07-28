import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated, UserDeactivated
from database.database import is_admin, get_all_users

@Client.on_message(filters.command("broadcast") & filters.private)
async def broadcast_command(client: Client, message: Message):
    if not await is_admin(message.from_user.id):
        return await message.reply_text("⚠️ ᴀᴄᴄᴇꜱꜱ ᴅᴇɴɪᴇᴅ: ᴀᴅᴍɪɴꜱ ᴏɴʟʏ!")
        
    if not message.reply_to_message:
        return await message.reply_text("ᴘʟᴇᴀꜱᴇ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇꜱꜱᴀɢᴇ ᴛᴏ ʙʀᴏᴀᴅᴄᴀꜱᴛ ɪᴛ.")
        
    users = await get_all_users()
    b_msg = await message.reply_text(f"📡 ʙʀᴏᴀᴅᴄᴀꜱᴛɪɴɢ ᴍᴇꜱꜱᴀɢᴇ ᴛᴏ {len(users)} ᴜꜱᴇʀꜱ. ᴘʟᴇᴀꜱᴇ ᴡᴀɪᴛ...")
    
    total = len(users)
    successful = 0
    blocked = 0
    deleted = 0
    unsuccessful = 0
    
    for user_id in users:
        try:
            await message.reply_to_message.copy(user_id)
            successful += 1
            await asyncio.sleep(0.1)
        except FloodWait as e:
            await asyncio.sleep(e.value)
            try:
                await message.reply_to_message.copy(user_id)
                successful += 1
            except UserIsBlocked: blocked += 1
            except (UserDeactivated, InputUserDeactivated): deleted += 1
            except Exception: unsuccessful += 1
        except UserIsBlocked: blocked += 1
        except (UserDeactivated, InputUserDeactivated): deleted += 1
        except Exception: unsuccessful += 1
            
    status = f"""
<b>📢 ʙʀᴏᴀᴅᴄᴀꜱᴛ ᴄᴏᴍᴘʟᴇᴛᴇᴅ</b>

<b>ᴛᴏᴛᴀʟ ᴜꜱᴇʀꜱ:</b> <code>{total}</code>
<b>ꜱᴜᴄᴄᴇꜱꜰᴜʟ:</b> <code>{successful}</code>
<b>ʙʟᴏᴄᴋᴇᴅ ᴜꜱᴇʀꜱ:</b> <code>{blocked}</code>
<b>ᴅᴇʟᴇᴛᴇᴅ ᴀᴄᴄᴏᴜɴᴛꜱ:</b> <code>{deleted}</code>
<b>ᴜɴꜱᴜᴄᴄᴇꜱꜱꜰᴜʟ:</b> <code>{unsuccessful}</code>
"""

    # Edit the message to show the final status
    await b_msg.edit_text(status)
    
    # Wait for 30 seconds, then delete the status message to avoid chat clutter
    await asyncio.sleep(30)
    try: 
        await b_msg.delete()
    except Exception: 
        pass
        
