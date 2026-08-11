import sys
import asyncio
from datetime import datetime, timedelta, timezone
from aiohttp import web
from plugins.web_server import web_server
import pyromod.listen
from pyrogram import Client
from pyrogram.enums import ParseMode
import pyrogram.utils
from pyrogram.errors import FloodWait, UserIsBlocked, UserDeactivated

pyrogram.utils.MIN_CHANNEL_ID = -1009999999999

from config import (
    API_HASH, APP_ID, LOGGER, TG_BOT_TOKEN, TG_BOT_WORKERS,
    PORT
)
from database.database import premium_collection, remove_premium, get_global_db_channel, get_global_fs_channels, delete_tenant_config

TITAN_BANNER = """
████████╗██╗████████╗░█████╗░███╗░░██╗██╗░░██╗██████╗░░█████╗░████████╗░██████╗
╚══██╔══╝██║╚══██╔══╝██╔══██╗████╗░██║╚██╗██╔╝██╔══██╗██╔══██╗╚══██╔══╝██╔════╝
░░░██║░░░██║░░░██║░░░███████║██╔██╗██║░╚███╔╝░██████╦╝██║░░██║░░░██║░░░╚█████╗░
░░░██║░░░██║░░░██║░░░██╔══██║██║╚████║░██╔██╗░██╔══██╗██║░░██║░░░██║░░░░╚═══██╗
░░░██║░░░██║░░░██║░░░██║░░██║██║░╚███║██╔╝╚██╗██████╦╝╚█████╔╝░░░██║░░░██████╔╝
░░░╚═╝░░░╚═╝░░░╚═╝░░░╚═╝░░╚═╝╚═╝░░╚══╝╚═╝░░╚═╝╚═════╝░░╚════╝░░░░╚═╝░░░╚═════╝░
"""

class Bot(Client):
    def __init__(self):
        super().__init__(
            name="Bot",
            api_hash=API_HASH,
            api_id=APP_ID,
            plugins={"root": "plugins"},
            workers=TG_BOT_WORKERS,
            bot_token=TG_BOT_TOKEN
        )
        self.logger = LOGGER(__name__)

    async def premium_expiry_task(self):
        while True:
            try:
                now = datetime.now(timezone.utc)
                warning_time = now + timedelta(days=1)
                
                cursor = premium_collection.find({"is_premium": True})
                async for user in cursor:
                    user_id = user["_id"]
                    expires_at = user.get("expires_at")
                    if not expires_at: continue
                    
                    expires_at = expires_at.replace(tzinfo=timezone.utc)
                    
                    # --- AUTO-REMOVE PREMIUM & CUSTOM CHANNELS ON EXPIRY ---
                    if now > expires_at:
                        await remove_premium(user_id)
                        await delete_tenant_config(user_id)
                        try:
                            await self.send_message(
                                user_id, 
                                f"⚠️ <b>ʏᴏᴜʀ ᴘʀᴇᴍɪᴜᴍ ᴍᴇᴍʙᴇʀꜱʜɪᴘ ʜᴀꜱ ᴇɴᴅᴇᴅ.</b>\n\n"
                                f"ʏᴏᴜʀ ᴄᴜꜱᴛᴏᴍ ᴅᴀᴛᴀʙᴀꜱᴇ ᴀɴᴅ ꜰᴏʀᴄᴇ-ꜱᴜʙ ᴄʜᴀɴɴᴇʟꜱ ʜᴀᴠᴇ ʙᴇᴇɴ ᴀᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ ʀᴇᴍᴏᴠᴇᴅ ꜰʀᴏᴍ ᴛʜᴇ ʙᴏᴛ.\n"
                                f"ɪᴛ ᴏꜰꜰɪᴄɪᴀʟʟʏ ᴄʟᴏꜱᴇᴅ ᴏɴ: {expires_at.strftime('%Y-%m-%d %H:%M:%S')} UTC"
                            )
                        except (UserIsBlocked, UserDeactivated): pass
                        except Exception as e: self.logger.error(f"Expiry notify error for {user_id}: {e}")
                    
                    # --- SEND 24 HOUR WARNING ---
                    elif warning_time > expires_at and not user.get("notified", False):
                        try:
                            await self.send_message(
                                user_id, 
                                f"⚠️ <b>ʀᴇᴍɪɴᴅᴇʀ:</b> ʏᴏᴜʀ ᴘʀᴇᴍɪᴜᴍ ᴍᴇᴍʙᴇʀꜱʜɪᴘ ɪꜱ ᴄʟᴏꜱɪɴɢ ꜱᴏᴏɴ!\n\n"
                                f"<b>ᴇxᴘɪʀʏ ᴅᴀᴛᴇ:</b> {expires_at.strftime('%Y-%m-%d %H:%M:%S')} UTC"
                            )
                            await premium_collection.update_one({"_id": user_id}, {"$set": {"notified": True}})
                        except (UserIsBlocked, UserDeactivated): pass
                        except Exception as e: self.logger.error(f"Warning notify error for {user_id}: {e}")
            except Exception as e:
                self.logger.error(f"Premium check error: {e}")
            await asyncio.sleep(3600) 

    async def start(self):
        await super().start()
        me = await self.get_me()
        self.uptime = datetime.now(timezone.utc)
        self.username = me.username
        
        asyncio.create_task(self.premium_expiry_task())
        self.logger.info("✅ Premium Expiry Monitor started.")

        self.invitelinks = {}
        async def get_invite(channel_id, key_name, label):
            if not channel_id or str(channel_id) == "0" or str(channel_id) == "-100":
                self.invitelinks[key_name] = None
                return
            try:
                chat = await self.get_chat(channel_id)
                link = chat.invite_link
                if not link: link = await self.export_chat_invite_link(channel_id)
                self.invitelinks[key_name] = link
                self.logger.info(f"✅ Force Sub Link generated for {label} ({channel_id})")
            except Exception as e:
                self.logger.error(f"❌ FORCE SUB CRITICAL: Failed to get link for {label} ({channel_id}). Error: {e}")
                self.invitelinks[key_name] = None

        active_fs_channels = await get_global_fs_channels()
        for idx, channel_id in enumerate(active_fs_channels, start=1):
            await get_invite(channel_id, str(channel_id), f"Channel {idx}")

        try:
            active_db = await get_global_db_channel()
            db_channel = await self.get_chat(active_db)
            self.db_channel = db_channel
            msg = await self.send_message(db_channel.id, "Test Message")
            await msg.delete()
            self.logger.info("✅ Database Channel verified successfully.")
        except Exception as e:
            self.logger.error(f"❌ CRITICAL: Bot is not admin in DB channel or CHANNEL_ID is wrong. Error: {e}")
            sys.exit()

        try:
            app = web.AppRunner(await web_server())
            await app.setup()
            site = web.TCPSite(app, "0.0.0.0", PORT)
            await site.start()
            self.logger.info(f"✅ Web Server started successfully on port {PORT}")
        except Exception as e:
            self.logger.warning(f"⚠️ Web Server failed to initialize: {e}")

        self.set_parse_mode(ParseMode.HTML)
        self.logger.info(f"Bot Running..!\n\nCreated by TitanXBots")
        self.logger.info(f"Username: @{self.username}")
        self.logger.info(f"\n{TITAN_BANNER}\n")

    async def stop(self, *args):
        await super().stop()
        self.logger.info("Bot stopped.")
        
