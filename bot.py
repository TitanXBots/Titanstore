#TitanXBots
from aiohttp import web
from plugins import web_server

import pyromod.listen
from pyrogram import Client
from pyrogram.enums import ParseMode
import sys
from datetime import datetime

from config import (
    API_HASH, APP_ID, LOGGER, TG_BOT_TOKEN,
    TG_BOT_WORKERS,
    FORCE_SUB_CHANNEL_1, FORCE_SUB_CHANNEL_2,
    FORCE_SUB_CHANNEL_3, FORCE_SUB_CHANNEL_4,
    CHANNEL_ID, PORT
)

import pyrogram.utils
pyrogram.utils.MIN_CHANNEL_ID = -1009999999999


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
        self.LOGGER = LOGGER

        # DB will be imported here (Motor async DB)
        from database import (
            is_user_banned,
            add_user,
            is_user_present,
            is_admin,
            is_owner
        )

        self.db = {
            "is_user_banned": is_user_banned,
            "add_user": add_user,
            "is_user_present": is_user_present,
            "is_admin": is_admin,
            "is_owner": is_owner
        }

    async def start(self):
        await super().start()
        me = await self.get_me()

        self.uptime = datetime.now()
        self.username = me.username

        # -------------------------------
        # FORCE SUB CHANNEL HANDLING
        # -------------------------------
        self.invitelinks = {}

        async def get_invite(channel_id, key_name):
            if not channel_id:
                return None

            try:
                chat = await self.get_chat(channel_id)

                link = chat.invite_link
                if not link:
                    link = await self.export_chat_invite_link(channel_id)

                self.invitelinks[key_name] = link

            except Exception as e:
                self.LOGGER(__name__).warning(e)
                self.LOGGER(__name__).warning(
                    f"Force sub setup failed for {channel_id}"
                )
                sys.exit()

        await get_invite(FORCE_SUB_CHANNEL_1, "fs1")
        await get_invite(FORCE_SUB_CHANNEL_2, "fs2")
        await get_invite(FORCE_SUB_CHANNEL_3, "fs3")
        await get_invite(FORCE_SUB_CHANNEL_4, "fs4")

        # -------------------------------
        # DATABASE CHANNEL CHECK
        # -------------------------------
        try:
            db_channel = await self.get_chat(CHANNEL_ID)
            self.db_channel = db_channel

            msg = await self.send_message(db_channel.id, "Test Message")
            await msg.delete()

        except Exception as e:
            self.LOGGER(__name__).warning(e)
            self.LOGGER(__name__).warning(
                f"Bot is not admin in DB channel or CHANNEL_ID is wrong: {CHANNEL_ID}"
            )
            sys.exit()

        # -------------------------------
        # WEB SERVER START
        # -------------------------------
        app = web.AppRunner(await web_server())
        await app.setup()

        site = web.TCPSite(app, "0.0.0.0", PORT)
        await site.start()

        # -------------------------------
        # FINAL LOGS
        # -------------------------------
        self.set_parse_mode(ParseMode.HTML)

        self.LOGGER(__name__).info("Bot is running...")
        self.LOGGER(__name__).info(f"Username: @{self.username}")

    async def stop(self, *args):
        await super().stop()
        self.LOGGER(__name__).info("Bot stopped.")
