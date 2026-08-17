import os
import logging
from logging.handlers import RotatingFileHandler

def get_env_int(env_key, default_value):
    val = os.environ.get(env_key)
    if val:
        try: return int(val)
        except ValueError: return default_value
    return default_value

TG_BOT_TOKEN = os.environ.get("TG_BOT_TOKEN", "8879317604:AAGy1bEfrjzeAMeBmBBKFA-WfcgtZcQQOKE") 
APP_ID = get_env_int("APP_ID", 12293838)
API_HASH = os.environ.get("API_HASH", "cf8c7db0d609148786e7ca5c706909bd")

CHANNEL_ID = get_env_int("CHANNEL_ID", -1002096962621)
LOG_CHANNEL_ID = get_env_int("LOG_CHANNEL_ID", -1002313688533)
OWNER_ID = get_env_int("OWNER_ID", 5356695781)
PORT = get_env_int("PORT", 8080)

ADMINS_STR = os.environ.get("ADMINS", "5356695781")
ADMINS = [int(x) for x in ADMINS_STR.split(",") if x.strip().isdigit()]

DB_URI = os.environ.get("DATABASE_URL", "mongodb+srv://TITANCINEPLEX:TITANCINEPLEX@cluster0.pzecgto.mongodb.net/?appName=Cluster0")
DB_NAME = os.environ.get("DATABASE_NAME", "TitanBot")

FORCE_SUB_CHANNEL_1 = get_env_int("FORCE_SUB_CHANNEL_1", -1002071945738)
FORCE_SUB_CHANNEL_2 = get_env_int("FORCE_SUB_CHANNEL_2", -1001972961497)
FORCE_SUB_CHANNEL_3 = get_env_int("FORCE_SUB_CHANNEL_3", -1001987271131)
FORCE_SUB_CHANNEL_4 = get_env_int("FORCE_SUB_CHANNEL_4", -1002038066716)

TG_BOT_WORKERS = get_env_int("TG_BOT_WORKERS", 4)

START_PIC = os.environ.get("START_PIC", "https://i.ibb.co/7xBNgdvj/x.jpg")
FORCE_PIC = os.environ.get("FORCE_PIC", "https://i.ibb.co/7xBNgdvj/x.jpg")

# --- PREMIUM & REFERRAL CONFIG ---
OWNER_USERNAME = os.environ.get("OWNER_USERNAME", "TitanXBots")
REFERRAL_POINTS = 10
POINTS_TO_PREMIUM = 100
PREMIUM_DAYS = 30
# ---------------------------------

HELP_TXT = """<b>ɪ ᴀᴍ ᴘᴇʀᴍᴀɴᴇɴᴛ ꜰɪʟᴇ ꜱᴛᴏʀᴇ ʙᴏᴛ.
ʏᴏᴜ ᴄᴀɴ ꜱᴛᴏʀᴇ ꜰɪʟᴇꜱ ꜰʀᴏᴍ ʙᴏᴛʜ ᴘᴜʙʟɪᴄ ᴀɴᴅ ᴘʀɪᴠᴀᴛᴇ ᴄʜᴀɴɴᴇʟꜱ.</b>"""

ABOUT_TXT = """<b>✯ ᴄʀᴇᴀᴛᴏʀ : <a href=https://t.me/TitanXBots>ʏᴀꜱʜ</a>
✯ ʟᴀɴɢᴜᴀɢᴇ : ᴘʏᴛʜᴏɴ3
✯ ʟɪʙʀᴀʀʏ : ᴘʏʀᴏɢʀᴀᴍ
✯ ꜱᴜᴘᴘᴏʀᴛ : <a href=https://t.me/TitanMattersSupport>ᴛɪᴛᴀɴ ɢʀᴏᴜᴘ</a></b>"""

COMMANDS_TXT = """<b>🤖 ᴘʀᴇᴍɪᴜᴍ ᴜꜱᴇʀꜱ ᴄᴏᴍᴍᴀɴᴅ</b>
• /genlink - ᴄʀᴇᴀᴛᴇ ʟɪɴᴋ ꜰᴏʀ ᴏɴᴇ ᴘᴏꜱᴛ
• /batch - ᴄʀᴇᴀᴛᴇ ʟɪɴᴋ ꜰᴏʀ ᴍᴏʀᴇ ᴘᴏꜱᴛꜱ
• /plan - ᴏᴘᴇɴꜱ ʏᴏᴜʀ ᴀᴄᴄᴏᴜɴᴛ ᴅᴀꜱʜʙᴏᴀʀᴅ

<b>ᴀᴅᴍɪɴ ᴄᴏᴍᴍᴀɴᴅꜱ:</b>
• /start, /restart, /maintenance, /broadcast, /users, /stats
• /addpremium [id] [days] - ɢɪᴠᴇ ᴘʀᴇᴍɪᴜᴍ
• /rmpremium [id] - ʀᴇᴍᴏᴠᴇ ᴘʀᴇᴍɪᴜᴍ
• /revokechannel [id] [db/fs] - ʀᴇᴠᴏᴋᴇ ᴀᴘᴘʀᴏᴠᴀʟ"""

DISCLAIMER_TXT = """<b>ᴛʜɪꜱ ɪꜱ ᴀɴ ᴘʀɪᴠᴀᴛᴇ ꜱᴏᴜʀᴄᴇ ᴘʀᴏᴊᴇᴄᴛ.</b>
ᴛʜᴇ ʙᴏᴛ ᴅᴏᴇꜱ ɴᴏᴛ ᴏᴡɴ ᴀɴʏ ᴏꜰ ᴛʜᴇꜱᴇ ᴄᴏɴᴛᴇɴᴛꜱ — ɪᴛ ᴏɴʟʏ ɪɴᴅᴇxᴇꜱ ᴛʜᴇ ꜰɪʟᴇꜱ ꜰʀᴏᴍ ᴛᴇʟᴇɢʀᴀᴍ."""

START_MSG = os.environ.get("START_MESSAGE", "👋 ʜᴇʟʟᴏ <b>{first}</b>,\n\n🚀 ɪ ᴄᴀɴ ꜱᴛᴏʀᴇ ᴘʀɪᴠᴀᴛᴇ ꜰɪʟᴇꜱ ɪɴ ꜱᴘᴇᴄɪꜰɪᴇᴅ ᴄʜᴀɴɴᴇʟꜱ ᴀɴᴅ ᴘʀᴏᴠɪᴅᴇ ꜱᴇᴄᴜʀᴇ ᴀᴄᴄᴇꜱꜱ ʟɪɴᴋꜱ.")
FORCE_MSG = os.environ.get("FORCE_SUB_MESSAGE", "👋 ʜᴇʟʟᴏ <b>{first}</b>,\n\n<b>⚠️ ʏᴏᴜ ɴᴇᴇᴅ ᴛᴏ ᴊᴏɪɴ ᴏᴜʀ ᴜᴘᴅᴀᴛᴇꜱ ᴄʜᴀɴɴᴇʟꜱ ᴛᴏ ᴜꜱᴇ ᴍᴇ!\n\nᴋɪɴᴅʟʏ ᴊᴏɪɴ ʙᴇʟᴏᴡ ᴀɴᴅ ᴛʀʏ ᴀɢᴀɪɴ 👇</b>")
CUSTOM_CAPTION = os.environ.get("CUSTOM_CAPTION", None)
BOT_STATS_TEXT = "<b>📊 ʙᴏᴛ ᴜᴘᴛɪᴍᴇ</b>\n<code>{uptime}</code>"
LOG_FILE_NAME = "filesharingbot.txt"

logging.basicConfig(level=logging.INFO, format="[%(asctime)s - %(levelname)s] - %(name)s - %(message)s", datefmt='%d-%b-%y %H:%M:%S', handlers=[RotatingFileHandler(LOG_FILE_NAME, maxBytes=50000000, backupCount=10), logging.StreamHandler()])
logging.getLogger("pyrogram").setLevel(logging.WARNING)

def LOGGER(name: str) -> logging.Logger:
    return logging.Logger(name)
    
