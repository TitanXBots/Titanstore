import os
import logging
from logging.handlers import RotatingFileHandler

def get_env_int(env_key, default_value):
    val = os.environ.get(env_key)
    if val:
        try:
            return int(val)
        except ValueError:
            return default_value
    return default_value

 
PORT = get_env_int("PORT", 8080)

OWNER_ID = get_env_int("OWNER_ID", 5356695781)

APP_ID = get_env_int("APP_ID", 12293838)

API_HASH = os.environ.get("API_HASH", "cf8c7db0d609148786e7ca5c706909bd")

TG_BOT_WORKERS = get_env_int("TG_BOT_WORKERS", 4)

TG_BOT_TOKEN = os.environ.get("TG_BOT_TOKEN", "8879094453:AAF3akfIR6UO9eMxriVnlKq8LbK2a6TkQ3s")

CHANNEL_ID = get_env_int("CHANNEL_ID", -1002096962621)

LOG_CHANNEL_ID = get_env_int("LOG_CHANNEL_ID", -1002313688533)


DB_NAME = os.environ.get("DATABASE_NAME", "TitanBot")
DB_URI = os.environ.get("DATABASE_URL", "mongodb+srv://TITANBOTS:TITANBOTS@cluster0.yagdfyt.mongodb.net/?appName=Cluster0")


ADMINS_STR = os.environ.get("ADMINS", "5356695781")
ADMINS = [int(x) for x in ADMINS_STR.split(",") if x.strip().isdigit()]


FORCE_SUB_CHANNEL_1 = get_env_int("FORCE_SUB_CHANNEL_1", -1002071945738)
FORCE_SUB_CHANNEL_2 = get_env_int("FORCE_SUB_CHANNEL_2", -1001972961497)
FORCE_SUB_CHANNEL_3 = get_env_int("FORCE_SUB_CHANNEL_3", -1001987271131)
FORCE_SUB_CHANNEL_4 = get_env_int("FORCE_SUB_CHANNEL_4", -1002038066716)


START_PIC = os.environ.get("START_PIC", "https://envs.sh/WeX.jpg")
FORCE_PIC = os.environ.get("FORCE_PIC", "https://envs.sh/TPh.jpg")


HELP_TXT = """<b>ɪ ᴀᴍ ᴘᴇʀᴍᴀɴᴇɴᴛ ꜰɪʟᴇ ꜱᴛᴏʀᴇ ʙᴏᴛ.

ʏᴏᴜ ᴄᴀɴ ꜱᴛᴏʀᴇ ꜰɪʟᴇꜱ ꜰʀᴏᴍ ʙᴏᴛʜ ᴘᴜʙʟɪᴄ ᴀɴᴅ ᴘʀɪᴠᴀᴛᴇ ᴄʜᴀɴɴᴇʟꜱ, ʙᴜᴛ ʏᴏᴜ ᴍᴜꜱᴛ ᴀᴅᴅ ᴍᴇ ᴀꜱ ᴀɴ ᴀᴅᴍɪɴ ɪɴ ᴛʜᴇ ᴄʜᴀɴɴᴇʟ ᴛᴏ ɢᴇɴᴇʀᴀᴛᴇ ꜱʜᴀʀᴇᴀʙʟᴇ ʟɪɴᴋꜱ.
ᴄʟɪᴄᴋ ᴛʜᴇ ᴄᴏᴍᴍᴀɴᴅꜱ ʙᴜᴛᴛᴏɴ ᴛᴏ ᴠɪᴇᴡ ᴛʜᴇ ᴀᴅᴍɪɴ ᴄᴏᴍᴍᴀɴᴅꜱ.</b>"""

ABOUT_TXT = """<b>✯ ᴄʀᴇᴀᴛᴏʀ : <a href=https://t.me/TitanXBots>ʏᴀꜱʜ</a>
✯ ʟᴀɴɢᴜᴀɢᴇ : <a href=https://www.python.org>ᴘʏᴛʜᴏɴ3</a>
✯ ʟɪʙʀᴀʀʏ : <a href='https://docs.pyrogram.org/'>ᴘʏʀᴏɢʀᴀᴍ</a>
✯ ꜱᴏᴜʀᴄᴇ ᴄᴏᴅᴇ : ᴘʀɪᴠᴀᴛᴇ
✯ ᴜᴘᴅᴀᴛᴇꜱ ᴄʜᴀɴɴᴇʟ : <a href=https://t.me/TitanXBots>ᴛɪᴛᴀɴxʙᴏᴛꜱ</a>
✯ ꜱᴜᴘᴘᴏʀᴛ : <a href=https://t.me/TitanMattersSupport>ᴛɪᴛᴀɴ ɢʀᴏᴜᴘ</a></b>"""


COMMANDS_TXT = """<b>🤖 ᴘʀᴇᴍɪᴜᴍ ᴜꜱᴇʀꜱ ᴄᴏᴍᴍᴀɴᴅ</b>

• /genlink - ᴄʀᴇᴀᴛᴇ ʟɪɴᴋ ꜰᴏʀ ᴏɴᴇ ᴘᴏꜱᴛ
• /batch - ᴄʀᴇᴀᴛᴇ ʟɪɴᴋ ꜰᴏʀ ᴍᴏʀᴇ ᴛʜᴀɴ ᴏɴᴇ ᴘᴏꜱᴛꜱ

<b>ᴀᴅᴍɪɴ ᴄᴏᴍᴍᴀɴᴅꜱ:</b>
• /start - ᴛᴏ ꜱᴛᴀʀᴛ ᴛʜᴇ ʙᴏᴛ
• /restart - ᴛᴏ ʀᴇꜱᴛᴀʀᴛ ᴛʜᴇ ʙᴏᴛ
• /maintenance - ʙᴏᴛ ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ ᴍᴏᴅᴇ
• /genlink - ᴄʀᴇᴀᴛᴇ ʟɪɴᴋ ꜰᴏʀ ᴏɴᴇ ᴘᴏꜱᴛ
• /batch - ᴄʀᴇᴀᴛᴇ ʟɪɴᴋ ꜰᴏʀ ᴍᴏʀᴇ ᴛʜᴀɴ ᴏɴᴇ ᴘᴏꜱᴛꜱ
• /broadcast - ʙʀᴏᴀᴅᴄᴀꜱᴛ ᴀɴʏ ᴍᴇꜱꜱᴀɢᴇ ᴛᴏ ʙᴏᴛ ᴜꜱᴇʀꜱ
• /users - ᴠɪᴇᴡ ʙᴏᴛ ꜱᴛᴀᴛɪꜱᴛɪᴄꜱ
• /stats - ᴄʜᴇᴄᴋɪɴɢ ʏᴏᴜʀ ʙᴏᴛ ᴜᴘᴛɪᴍᴇ"""

DISCLAIMER_TXT = """
<b>ᴛʜɪꜱ ɪꜱ ᴀɴ ᴘʀɪᴠᴀᴛᴇ ꜱᴏᴜʀᴄᴇ ᴘʀᴏᴊᴇᴄᴛ.</b>

ᴀʟʟ ᴛʜᴇ ꜰɪʟᴇꜱ ɪɴ ᴛʜɪꜱ ʙᴏᴛ ᴀʀᴇ ꜰʀᴇᴇʟʏ ᴀᴠᴀɪʟᴀʙʟᴇ ᴏɴ ᴛʜᴇ ɪɴᴛᴇʀɴᴇᴛ ᴏʀ ᴘᴏꜱᴛᴇᴅ ʙʏ ꜱᴏᴍᴇʙᴏᴅʏ ᴇʟꜱᴇ. ᴊᴜꜱᴛ ꜰᴏʀ ᴇᴀꜱʏ ꜱᴇᴀʀᴄʜɪɴɢ, ᴛʜɪꜱ ʙᴏᴛ ɪꜱ ɪɴᴅᴇxɪɴɢ ꜰɪʟᴇꜱ ᴡʜɪᴄʜ ᴀʀᴇ ᴀʟʀᴇᴀᴅʏ ᴜᴘʟᴏᴀᴅᴇᴅ ᴏɴ ᴛᴇʟᴇɢʀᴀᴍ. 
ᴡᴇ ʀᴇꜱᴘᴇᴄᴛ ᴀʟʟ ᴛʜᴇ ᴄᴏᴘʏʀɪɢʜᴛ ʟᴀᴡꜱ ᴀɴᴅ ᴡᴏʀᴋ ɪɴ ᴄᴏᴍᴘʟɪᴀɴᴄᴇ ᴡɪᴛʜ ᴅᴍᴄᴀ ᴀɴᴅ ᴇᴜᴄᴅ. 

ɪꜰ ᴀɴʏᴛʜɪɴɢ ɪꜱ ᴀɢᴀɪɴꜱᴛ ʟᴀᴡ, ᴘʟᴇᴀꜱᴇ ᴄᴏɴᴛᴀᴄᴛ ᴍᴇ ꜱᴏ ᴛʜᴀᴛ ɪᴛ ᴄᴀɴ ʙᴇ ʀᴇᴍᴏᴠᴇᴅ ᴀꜱᴀᴘ. 
ɪᴛ ɪꜱ ꜰᴏʀʙɪʙʙᴇɴ ᴛᴏ ᴅᴏᴡɴʟᴏᴀᴅ, ꜱᴛʀᴇᴀᴍ, ʀᴇᴘʀᴏᴅᴜᴄᴇ, ꜱʜᴀʀᴇ ᴏʀ ᴄᴏɴꜱᴜᴍᴇ ᴄᴏɴᴛᴇɴᴛ ᴡɪᴛʜᴏᴜᴛ ᴇxᴘʟɪᴄɪᴛ ᴘᴇʀᴍɪꜱꜱɪᴏɴ ꜰʀᴏᴍ ᴛʜᴇ ᴄᴏɴᴛᴇɴᴛ ᴄʀᴇᴀᴛᴏʀ ᴏʀ ʟᴇɢᴀʟ ᴄᴏᴘʏʀɪɢʜᴛ ʜᴏʟᴅᴇʀ. 
ɪꜰ ʏᴏᴜ ʙᴇʟɪᴇᴠᴇ ᴛʜɪꜱ ʙᴏᴛ ɪꜱ ᴠɪᴏʟᴀᴛɪɴɢ ʏᴏᴜʀ ɪɴᴛᴇʟʟᴇᴄᴛᴜᴀʟ ᴘʀᴏᴘᴇʀᴛʏ, ᴄᴏɴᴛᴀᴄᴛ ᴛʜᴇ ʀᴇꜱᴘᴇᴄᴛɪᴠᴇ ᴄʜᴀɴɴᴇʟꜱ ꜰᴏʀ ʀᴇᴍᴏᴠᴀʟ. 
ᴛʜᴇ ʙᴏᴛ ᴅᴏᴇꜱ ɴᴏᴛ ᴏᴡɴ ᴀɴʏ ᴏꜰ ᴛʜᴇꜱᴇ ᴄᴏɴᴛᴇɴᴛꜱ — ɪᴛ ᴏɴʟʏ ɪɴᴅᴇxᴇꜱ ᴛʜᴇ ꜰɪʟᴇꜱ ꜰʀᴏᴍ ᴛᴇʟᴇɢʀᴀᴍ. 

<blockquote><b>🌿 ᴍᴀɪɴᴛᴀɪɴᴇᴅ ʙʏ :</b> <a href="https://t.me/TitanXBots">ᴛɪᴛᴀɴxʙᴏᴛꜱ</a></blockquote>
"""

START_MSG = os.environ.get("START_MESSAGE", "ʜᴇʟʟᴏ {first}\n\nɪ ᴄᴀɴ ꜱᴛᴏʀᴇ ᴘʀɪᴠᴀᴛᴇ ꜰɪʟᴇꜱ ɪɴ ꜱᴘᴇᴄɪꜰɪᴇᴅ ᴄʜᴀɴɴᴇʟ ᴀɴᴅ ᴏᴛʜᴇʀ ᴜꜱᴇʀꜱ ᴄᴀɴ ᴀᴄᴄᴇꜱꜱ ɪᴛ ꜰʀᴏᴍ ꜱᴘᴇᴄɪᴀʟ ʟɪɴᴋ.")

FORCE_MSG = os.environ.get("FORCE_SUB_MESSAGE", "ʜᴇʟʟᴏ {first}\n\n<b>ʏᴏᴜ ɴᴇᴇᴅ ᴛᴏ ᴊᴏɪɴ ɪɴ ᴍʏ ᴄʜᴀɴɴᴇʟ/ɢʀᴏᴜᴘ ᴛᴏ ᴜꜱᴇ ᴍᴇ\n\nᴋɪɴᴅʟʏ ᴘʟᴇᴀꜱᴇ ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟꜱ</b>")

CUSTOM_CAPTION = os.environ.get("CUSTOM_CAPTION", None)

BOT_STATS_TEXT = "<b>ʙᴏᴛ ᴜᴘᴛɪᴍᴇ</b>\n{uptime}"

USER_REPLY_TEXT = "👋 ʜᴇʏ ꜰʀɪᴇɴᴅ, 🚫 ᴅᴏɴ'ᴛ ꜱᴇɴᴅ ᴀɴʏ ᴍᴇꜱꜱᴀɢᴇ ᴛᴏ ᴍᴇ ᴅɪʀᴇᴄᴛʟʏ. ɪ'ᴍ ᴏɴʟʏ ᴀ ꜰɪʟᴇ ꜱᴛᴏʀᴇ ʙᴏᴛ!"

LOG_FILE_NAME = "filesharingbot.txt"

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s - %(levelname)s] - %(name)s - %(message)s",
    datefmt='%d-%b-%y %H:%M:%S',
    handlers=[
        RotatingFileHandler(LOG_FILE_NAME, maxBytes=50000000, backupCount=10),
        logging.StreamHandler()
    ]
)
logging.getLogger("pyrogram").setLevel(logging.WARNING)

def LOGGER(name: str) -> logging.Logger:
    return logging.getLogger(name)
    
