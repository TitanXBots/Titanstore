import motor.motor_asyncio
from config import DB_URI, DB_NAME, OWNER_ID

client = motor.motor_asyncio.AsyncIOMotorClient(DB_URI)
db = client[DB_NAME]

users = db["users"]
admins = db["admins"]
banned = db["banned"]
files = db["files"]
settings = db["settings"]

# USERS
async def add_user(uid, name, username):
    await users.update_one({"_id": uid}, {"$set": {
        "_id": uid,
        "name": name,
        "username": username
    }}, upsert=True)

async def is_user(uid):
    return bool(await users.find_one({"_id": uid}))

# ADMINS
async def is_admin(uid):
    if uid == OWNER_ID:
        return True
    return bool(await admins.find_one({"_id": uid}))

async def add_admin(uid):
    await admins.update_one({"_id": uid}, {"$set": {"is_admin": True}}, upsert=True)

async def remove_admin(uid):
    await admins.delete_one({"_id": uid})

async def get_admins():
    return await admins.find({}, {"_id": 1}).to_list(None)

# BAN
async def ban_user(uid, reason="No reason"):
    await banned.update_one({"_id": uid}, {"$set": {"banned": True, "reason": reason}}, upsert=True)

async def unban_user(uid):
    await banned.update_one({"_id": uid}, {"$set": {"banned": False}}, upsert=True)

async def is_banned(uid):
    d = await banned.find_one({"_id": uid})
    return bool(d and d.get("banned"))

async def ban_reason(uid):
    d = await banned.find_one({"_id": uid})
    return d.get("reason", "")

# FILE SYSTEM (SAFE)
async def save_file(message_id):
    import uuid
    fid = str(uuid.uuid4())
    await files.insert_one({"_id": fid, "msg_id": message_id})
    return fid

async def get_file(fid):
    return await files.find_one({"_id": fid})

# SETTINGS
async def set_maintenance(state: bool):
    await settings.update_one({"_id": "maintenance"}, {"$set": {"state": state}}, upsert=True)

async def is_maintenance():
    d = await settings.find_one({"_id": "maintenance"})
    return bool(d and d.get("state"))
