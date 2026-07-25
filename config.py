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

# SECURITY FIX: Always pull the token from environment variables, never hardcode it!
TG_BOT_TOKEN = os.environ.get("TG_BOT_TOKEN", "8879094453:AAF3akfIR6UO9eMxriVnlKq8LbK2a6TkQ3s") 
APP_ID = get_env_int("APP_ID", 12293838)
API_HASH = os.environ.get("API_HASH", "cf8c7db0d609148786e7ca5c706909bd")

CHANNEL_ID = get_env_int("CHANNEL_ID", -1002096962621)
LOG_CHANNEL_ID = get_env_int("LOG_CHANNEL_ID", -1002313688533)
OWNER_ID = get_env_int("OWNER_ID", 5356695781)
PORT = get_env_int("PORT", 8080)

# Load additional admins from environment variable (comma separated)
ADMINS_STR = os.environ.get("ADMINS", "5356695781")
ADMINS = [int(x) for x in ADMINS_STR.split(",") if x.strip().isdigit()]

DB_URI = os.environ.get("DATABASE_URL", "mongodb+srv://TITANBOTS:TITANBOTS@cluster0.yagdfyt.mongodb.net/?appName=Cluster0")
DB_NAME = os.environ.get("DATABASE_NAME", "TitanBot")

FORCE_SUB_CHANNEL_1 = get_env_int("FORCE_SUB_CHANNEL_1", -1002071945738)
FORCE_SUB_CHANNEL_2 = get_env_int("FORCE_SUB_CHANNEL_2", -1001972961497)
FORCE_SUB_CHANNEL_3 = get_env_int("FORCE_SUB_CHANNEL_3", -1001987271131)
FORCE_SUB_CHANNEL_4 = get_env_int("FORCE_SUB_CHANNEL_4", -1002038066716)

TG_BOT_WORKERS = get_env_int("TG_BOT_WORKERS", 4)

START_PIC = os.environ.get("START_PIC", "https://envs.sh/WeX.jpg")
FORCE_PIC = os.environ.get("FORCE_PIC", "https://envs.sh/TPh.jpg")

HELP_TXT = "<b>ᴛʜɪs ɪs ᴀɴ ꜰɪʟᴇꜱᴛᴏʀᴇ ʙᴏᴛ ᴡᴏʀᴋ ғᴏʀ @TitanCineplex\n\n✯ ʙᴏᴛ ᴄᴏᴍᴍᴀɴᴅs\n├/start : sᴛᴀʀᴛ ᴛʜᴇ ʙᴏᴛ\n├/about : ᴏᴜʀ Iɴғᴏʀᴍᴀᴛɪᴏɴ\n└/help : ʜᴇʟᴘ ʀᴇʟᴀᴛᴇᴅ ʙᴏᴛ\n\n sɪᴍᴘʟʏ ᴄʟɪᴄᴋ ᴏɴ ʟɪɴᴋ ᴀɴᴅ sᴛᴀʀᴛ ᴛʜᴇ ʙᴏᴛ ᴊᴏɪɴ 🫵 ᴄʜᴀɴɴᴇʟs ᴀɴᴅ ᴛʀʏ ᴀɢᴀɪɴ ᴛʜᴀᴛs ɪᴛ.....!</b>"
ABOUT_TXT = "<b>✯ ᴄʀᴇᴀᴛᴏʀ : <a href=https://t.me/TitanXBots>ᎩᎪᏚʜཛ</a>\n✯ ʟᴀɴɢᴜᴀɢᴇ : <a href=https://www.python.org>ᴘʏᴛʜᴏɴ3</a>\n✯ ʟɪʙʀᴀʀʏ : <a href='https://docs.pyrogram.org/'>ᴘʏʀᴏɢʀᴀᴍ</a>\n✯ ꜱᴏᴜʀᴄᴇ ᴄᴏᴅᴇ : ᴘʀɪᴠᴀᴛᴇ\n✯ ᴜᴘᴅᴀᴛᴇꜱ ᴄʜᴀɴɴᴇʟ : <a href=https://t.me/TitanXBots>ᴛɪᴛᴀɴxʙᴏᴛꜱ</a>\n✯ ꜱᴜᴘᴘᴏʀᴛ : <a href=https://t.me/TitanMattersSupport>ᴛɪᴛᴀɴ ɢʀᴏᴜᴘ</a></b>"
COMMANDS_TXT = "<b>🤖 Bot Commands Menu</b>\n\n• /start - Initialize the Bot\n• /help - Display Support Help Options\n• /about - Display Bot Metadata\n\n<b>Admin Commands:</b>\n• /users - Total Users Count\n• /broadcast - Send copy broadcasts\n• /batch - Multi-link Generator\n• /genlink - Single-link Generator\n• /maintenance - Toggle system down-time"
DISCLAIMER_TXT = "<b>⚠️ Disclaimer Notice</b>\n\nThis bot is strictly meant for sharing personal storage files. Content distributed via third-party storage channels is independent of the developer infrastructure. Compliance with copyright legislation remains the user's explicit responsibility."
START_MSG = os.environ.get("START_MESSAGE", "ʜᴇʟʟᴏ {first}\n\nɪ ᴄᴀɴ ꜱᴛᴏʀᴇ ᴘʀɪᴠᴀᴛᴇ ꜰɪʟᴇꜱ ɪɴ ꜱᴘᴇᴄɪꜰɪᴇᴅ ᴄʜᴀɴɴᴇʟ ᴀɴᴅ ᴏᴛʜᴇʀ ᴜꜱᴇʀꜱ ᴄᴀɴ ᴀᴄᴄᴇꜱꜱ ɪᴛ ꜰʀᴏᴍ ꜱᴘᴇᴄɪᴀʟ ʟɪɴᴋ.")
FORCE_MSG = os.environ.get("FORCE_SUB_MESSAGE", "ʜᴇʟʟᴏ {first}\n\n<b>ʏᴏᴜ ɴᴇᴇᴅ ᴛᴏ ᴊᴏɪɴ ɪɴ ᴍʏ ᴄʜᴀɴɴᴇʟ/ɢʀᴏᴜᴘ ᴛᴏ ᴜꜱᴇ ᴍᴇ\n\nᴋɪɴᴅʟʏ ᴘʟᴇᴀꜱᴇ ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟꜱ</b>")

CUSTOM_CAPTION = os.environ.get("CUSTOM_CAPTION", None)

BOT_STATS_TEXT = "<b>BOT UPTIME</b>\n{uptime}"
USER_REPLY_TEXT = "👋 ʜᴇʏ ꜰʀɪᴇɴᴅ, 🚫 ᴅᴏɴ'ᴛ ꜱᴇɴᴅ ᴀɴʏ ᴍᴇꜱꜱᴀɢᴇ ᴛᴏ ᴍᴇ ᴅɪʀᴇᴄᴛʟʏ ɪ'ᴍ ᴏɴʟʏ ꜰɪʟᴇ ꜱᴛᴏʀᴇ ʙᴏᴛ!"
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
    
