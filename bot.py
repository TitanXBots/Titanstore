import sys
from datetime import datetime

from aiohttp import web
from pyrogram import Client
from pyrogram.enums import ParseMode

import pyrogram.utils
pyrogram.utils.MIN_CHANNEL_ID = -1009999999999

from config import *
from database.database import is_admin
from plugins import web_server


class Bot(Client):

    def __init__(self):
        super().__init__(
            name="TitanXBots",
            api_id=APP_ID,
            api_hash=API_HASH,
            bot_token=TG_BOT_TOKEN,
            workers=TG_BOT_WORKERS,
            plugins={"root": "plugins"}
        )

        self.start_time = datetime.utcnow()
        self.logger = LOGGER(__name__)

        # DB functions injected (clean access layer)
        self.db = {
            "is_admin": is_admin
        }

        self.invitelinks = {}

    # ---------------- START BOT ----------------
    async def start(self):
        await super().start()

        me = await self.get_me()
        self.username = me.username

        self.logger.info(f"Bot started as @{self.username}")

        # ---------------- FORCE SUB LINKS ----------------
        await self.setup_invites()

        # ---------------- DATABASE CHANNEL CHECK ----------------
        try:
            self.db_channel = await self.get_chat(CHANNEL_ID)

            msg = await self.send_message(self.db_channel.id, "🔹 DB Check")
            await msg.delete()

        except Exception as e:
            self.logger.error("DB Channel error: %s", e)
            sys.exit()

        # ---------------- WEB SERVER ----------------
        app = web.AppRunner(await web_server())
        await app.setup()

        site = web.TCPSite(app, "0.0.0.0", PORT)
        await site.start()

        self.set_parse_mode(ParseMode.HTML)

        self.logger.info("Web server started")
        self.logger.info("Bot is fully running")

    # ---------------- FORCE SUB ----------------
    async def setup_invites(self):

        channels = FORCE_CHANNELS

        for i, channel_id in enumerate(channels, start=1):
            try:
                chat = await self.get_chat(channel_id)

                link = chat.invite_link
                if not link:
                    link = await self.export_chat_invite_link(channel_id)

                self.invitelinks[f"fs{i}"] = link

            except Exception as e:
                self.logger.warning(f"ForceSub error {channel_id}: {e}")
                sys.exit()

        self.invitelink = self.invitelinks.get("fs1")
        self.invitelink2 = self.invitelinks.get("fs2")
        self.invitelink3 = self.invitelinks.get("fs3")
        self.invitelink4 = self.invitelinks.get("fs4")

    # ---------------- STOP BOT ----------------
    async def stop(self, *args):
        await super().stop()
        self.logger.info("Bot stopped")
