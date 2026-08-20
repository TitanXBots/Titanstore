import motor.motor_asyncio
from datetime import datetime, timezone, timedelta
from config import DB_URI, DB_NAME, OWNER_ID, ADMINS, CHANNEL_ID, FORCE_SUB_CHANNEL_1, FORCE_SUB_CHANNEL_2, FORCE_SUB_CHANNEL_3, FORCE_SUB_CHANNEL_4

dbclient = motor.motor_asyncio.AsyncIOMotorClient(DB_URI)
database = dbclient[DB_NAME]
db = database

user_data = database["users"]
banned_users = database["banned_users"]
admins_collection = database["admins"]
maintenance_collection = database["maintenance"]
settings_collection = database["settings"]
approvals_col = database["approvals"] 

# --- CORE USER ---
async def is_user_present(user_id: int) -> bool:
    return await user_data.find_one({"_id": user_id}) is not None

async def get_user(user_id: int):
    return await user_data.find_one({"_id": user_id})

async def add_user(user_id: int, first_name=None, username=None):
    user = await user_data.find_one({"_id": user_id})
    if not user:
        await user_data.insert_one({
            "_id": user_id, "first_name": first_name, "username": username,
            "points": 0, "is_premium": False, "premium_expiry": None,
            "trial_claimed": False
        })
    else:
        await user_data.update_one({"_id": user_id}, {"$set": {"first_name": first_name, "username": username}})

async def get_all_users(): return [user["_id"] for user in await user_data.find({}, {"_id": 1}).to_list(length=None)]
async def delete_user(user_id: int): await user_data.delete_one({"_id": user_id})

# --- PREMIUM, POINTS & 10-MIN TRIAL SYSTEM ---
async def add_referral_points(user_id: int, points: int):
    await user_data.update_one({"_id": user_id}, {"$inc": {"points": points}})

async def get_premium_status(user_id: int) -> bool:
    user = await get_user(user_id)
    if not user: return False
    expiry = user.get("premium_expiry")
    if not expiry: return False
    if datetime.now(timezone.utc).timestamp() > expiry:
        await remove_premium(user_id)
        return False
    return True

async def set_premium(user_id: int, days: int):
    expiry = (datetime.now(timezone.utc) + timedelta(days=days)).timestamp()
    await user_data.update_one({"_id": user_id}, {"$set": {"is_premium": True, "premium_expiry": expiry}})

async def remove_premium(user_id: int):
    # Removes Premium AND auto-wipes custom channels if they were a trial user
    await user_data.update_one({"_id": user_id}, {"$set": {"is_premium": False, "premium_expiry": None}})
    await approvals_col.delete_many({"user_id": user_id})

async def has_claimed_trial(user_id: int) -> bool:
    user = await get_user(user_id)
    return user.get("trial_claimed", False) if user else False

async def grant_free_trial(user_id: int):
    expiry = (datetime.now(timezone.utc) + timedelta(minutes=10)).timestamp()
    await user_data.update_one({"_id": user_id}, {"$set": {"is_premium": True, "premium_expiry": expiry, "trial_claimed": True}})

# --- CUSTOM CHANNEL MANAGEMENT ---
async def submit_channel(user_id: int, ch_type: str, channels: list, status: str = "pending"):
    await approvals_col.update_one(
        {"user_id": user_id, "type": ch_type}, 
        {"$set": {"channels": channels, "status": status}}, 
        upsert=True
    )

async def get_user_approved_channels(user_id: int, ch_type: str):
    data = await approvals_col.find_one({"user_id": user_id, "type": ch_type, "status": "approved"})
    return data.get("channels") if data else None

async def set_channel_status(user_id: int, ch_type: str, status: str):
    await approvals_col.update_one({"user_id": user_id, "type": ch_type}, {"$set": {"status": status}})

# --- SYSTEM GLOBALS & ADMINS ---
async def get_global_db_channel() -> int:
    data = await settings_collection.find_one({"_id": "global_db_channel"})
    return data.get("channel_id", CHANNEL_ID) if data else CHANNEL_ID

async def set_global_db_channel(channel_id: int):
    await settings_collection.update_one({"_id": "global_db_channel"}, {"$set": {"channel_id": channel_id}}, upsert=True)

async def get_global_fs_channels() -> list:
    data = await settings_collection.find_one({"_id": "global_fs_channels"})
    if data and "channels" in data: return data["channels"]
    defaults = [FORCE_SUB_CHANNEL_1, FORCE_SUB_CHANNEL_2, FORCE_SUB_CHANNEL_3, FORCE_SUB_CHANNEL_4]
    return [c for c in defaults if c and str(c) not in ["0", "-100"]]

async def set_global_fs_channels(fs_channels: list):
    await settings_collection.update_one({"_id": "global_fs_channels"}, {"$set": {"channels": fs_channels}}, upsert=True)

async def is_admin(user_id) -> bool:
    try:
        uid = int(user_id)
        if uid == int(OWNER_ID) or uid in ADMINS: return True
        data = await admins_collection.find_one({"_id": uid})
        return data is not None and data.get("is_admin", False)
    except: return False

async def get_admins(): return [admin["_id"] for admin in await admins_collection.find({}, {"_id": 1}).to_list(length=None)]
async def add_admin(user_id: int): await admins_collection.update_one({"_id": user_id}, {"$set": {"is_admin": True}}, upsert=True)
async def remove_admin(user_id: int): await admins_collection.delete_one({"_id": user_id})
async def is_owner(user_id) -> bool: return int(user_id) == int(OWNER_ID)

async def is_user_banned(user_id: int) -> bool: return (await banned_users.find_one({"_id": user_id}) or {}).get("is_banned", False)
async def get_ban_reason(user_id: int) -> str: return (await banned_users.find_one({"_id": user_id}) or {}).get("reason", "No reason provided")
async def ban_user(user_id: int, reason: str = "No reason"): await banned_users.update_one({"_id": user_id}, {"$set": {"is_banned": True, "reason": reason}}, upsert=True)
async def unban_user(user_id: int): await banned_users.update_one({"_id": user_id}, {"$set": {"is_banned": False, "reason": ""}}, upsert=True)
async def get_banned_users(): return await banned_users.find({"is_banned": True}).to_list(length=None)

async def is_maintenance(user_id: int) -> bool:
    if await is_admin(user_id): return False
    return (await maintenance_collection.find_one({"_id": "maintenance"}) or {}).get("maintenance") == "on"

async def get_auto_delete_status() -> bool: return (await settings_collection.find_one({"_id": "auto_delete"}) or {}).get("status", True)
async def set_auto_delete_status(status: bool): await settings_collection.update_one({"_id": "auto_delete"}, {"$set": {"status": status}}, upsert=True)
async def get_auto_delete_time() -> int: return (await settings_collection.find_one({"_id": "auto_delete_time"}) or {}).get("time", 600)
async def set_auto_delete_time(time: int): await settings_collection.update_one({"_id": "auto_delete_time"}, {"$set": {"time": time}}, upsert=True)

async def get_protect_status() -> bool: return (await settings_collection.find_one({"_id": "protect_content"}) or {}).get("status", False)
async def set_protect_status(status: bool): await settings_collection.update_one({"_id": "protect_content"}, {"$set": {"status": status}}, upsert=True)
async def get_force_sub_status() -> bool: return (await settings_collection.find_one({"_id": "force_sub"}) or {}).get("status", True)
async def set_force_sub_status(status: bool): await settings_collection.update_one({"_id": "force_sub"}, {"$set": {"status": status}}, upsert=True)
async def get_file_again_status() -> bool: return (await settings_collection.find_one({"_id": "get_file_again"}) or {}).get("status", True)
async def set_file_again_status(status: bool): await settings_collection.update_one({"_id": "get_file_again"}, {"$set": {"status": status}}, upsert=True)
    
