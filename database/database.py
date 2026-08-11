import motor.motor_asyncio
from datetime import datetime, timedelta, timezone
from config import DB_URI, DB_NAME, OWNER_ID, ADMINS, CHANNEL_ID, FORCE_SUB_CHANNEL_1, FORCE_SUB_CHANNEL_2, FORCE_SUB_CHANNEL_3, FORCE_SUB_CHANNEL_4

dbclient = motor.motor_asyncio.AsyncIOMotorClient(DB_URI)
database = dbclient[DB_NAME]

user_data = database["users"]
banned_users = database["banned_users"]
admins_collection = database["admins"]
maintenance_collection = database["maintenance"]
premium_collection = database["premium_users"]
settings_collection = database["settings"]
tenant_collection = database["tenant_configs"]

# --- GLOBAL DYNAMIC CHANNELS FUNCTIONS ---
async def get_global_db_channel() -> int:
    data = await settings_collection.find_one({"_id": "global_db_channel"})
    return data.get("channel_id", CHANNEL_ID) if data else CHANNEL_ID

async def set_global_db_channel(channel_id: int):
    await settings_collection.update_one({"_id": "global_db_channel"}, {"$set": {"channel_id": channel_id}}, upsert=True)

async def get_global_fs_channels() -> list:
    data = await settings_collection.find_one({"_id": "global_fs_channels"})
    if data and "channels" in data:
        return data["channels"]
    defaults = [FORCE_SUB_CHANNEL_1, FORCE_SUB_CHANNEL_2, FORCE_SUB_CHANNEL_3, FORCE_SUB_CHANNEL_4]
    return [c for c in defaults if c and str(c) not in ["0", "-100"]]

async def set_global_fs_channels(fs_channels: list):
    await settings_collection.update_one({"_id": "global_fs_channels"}, {"$set": {"channels": fs_channels}}, upsert=True)

# --- SAAS TENANT FUNCTIONS ---
async def save_tenant_request(user_id: int, db_channel: int, fs_channels: list):
    await tenant_collection.update_one(
        {"_id": user_id},
        {"$set": {"db_channel": db_channel, "fs_channels": fs_channels, "status": "pending"}},
        upsert=True
    )

async def update_tenant_status(user_id: int, status: str):
    await tenant_collection.update_one({"_id": user_id}, {"$set": {"status": status}})

async def get_tenant_config(user_id: int):
    return await tenant_collection.find_one({"_id": user_id, "status": "approved"})

async def get_tenant_by_db(db_channel: int):
    return await tenant_collection.find_one({"db_channel": db_channel, "status": "approved"})

async def get_pending_tenants():
    cursor = tenant_collection.find({"status": "pending"})
    return await cursor.to_list(length=None)

async def delete_tenant_config(user_id: int):
    await tenant_collection.delete_one({"_id": user_id})

# --- USER FUNCTIONS ---
async def is_user_present(user_id: int) -> bool:
    return await user_data.find_one({"_id": user_id}) is not None

async def add_user(user_id: int, first_name=None, username=None, referred_by: int = 0):
    user = await user_data.find_one({"_id": user_id})
    if not user:
        await user_data.insert_one({
            "_id": user_id,
            "first_name": first_name,
            "username": username,
            "joined_at": datetime.now(timezone.utc),
            "referred_by": referred_by,
            "points": 0
        })
    else:
        await user_data.update_one(
            {"_id": user_id},
            {"$set": {"first_name": first_name, "username": username}}
        )

# --- REFERRAL & POINTS FUNCTIONS ---
async def add_points(user_id: int, points: int):
    await user_data.update_one({"_id": user_id}, {"$inc": {"points": points}}, upsert=True)

async def get_points(user_id: int) -> int:
    user = await user_data.find_one({"_id": user_id})
    return user.get("points", 0) if user else 0

async def deduct_points(user_id: int, points: int):
    await user_data.update_one({"_id": user_id}, {"$inc": {"points": -points}})

async def get_all_users():
    cursor = user_data.find({}, {"_id": 1})
    users = await cursor.to_list(length=None)
    return [user["_id"] for user in users]

async def delete_user(user_id: int):
    await user_data.delete_one({"_id": user_id})

async def is_user_banned(user_id: int) -> bool:
    data = await banned_users.find_one({"_id": user_id})
    return data.get("is_banned", False) if data else False

async def get_ban_reason(user_id: int) -> str:
    data = await banned_users.find_one({"_id": user_id})
    return data.get("reason", "No reason provided") if data else "No reason provided"

async def ban_user(user_id: int, reason: str = "No reason"):
    await banned_users.update_one({"_id": user_id}, {"$set": {"is_banned": True, "reason": reason}}, upsert=True)

async def unban_user(user_id: int):
    await banned_users.update_one({"_id": user_id}, {"$set": {"is_banned": False, "reason": ""}}, upsert=True)

async def get_banned_users():
    cursor = banned_users.find({"is_banned": True})
    return await cursor.to_list(length=None)

# --- ADMIN & PREMIUM FUNCTIONS ---
async def add_admin(user_id: int):
    await admins_collection.update_one({"_id": user_id}, {"$set": {"is_admin": True}}, upsert=True)

async def remove_admin(user_id: int):
    await admins_collection.delete_one({"_id": user_id})

async def get_admins():
    cursor = admins_collection.find({}, {"_id": 1})
    admins = await cursor.to_list(length=None)
    return [admin["_id"] for admin in admins]

async def is_owner(user_id) -> bool:
    try: return int(user_id) == int(OWNER_ID)
    except (ValueError, TypeError): return False

async def is_admin(user_id) -> bool:
    try:
        uid = int(user_id)
        if uid == int(OWNER_ID) or uid in ADMINS: return True
        data = await admins_collection.find_one({"_id": uid})
        return data is not None and data.get("is_admin", False)
    except (ValueError, TypeError): return False

async def add_premium(user_id: int, days: int):
    # Check if they are already premium to add days correctly
    existing_user = await premium_collection.find_one({"_id": user_id})
    now = datetime.now(timezone.utc)
    
    if existing_user and existing_user.get("is_premium") and existing_user.get("expires_at") > now:
        # Extend current expiry
        expires_at = existing_user["expires_at"] + timedelta(days=days)
    else:
        # New premium
        expires_at = now + timedelta(days=days)
        
    await premium_collection.update_one(
        {"_id": user_id}, 
        {"$set": {"is_premium": True, "expires_at": expires_at, "notified": False}}, 
        upsert=True
    )

async def remove_premium(user_id: int):
    await premium_collection.delete_one({"_id": user_id})

async def get_premium_users():
    cursor = premium_collection.find({}, {"_id": 1})
    users = await cursor.to_list(length=None)
    return [user["_id"] for user in users]

async def is_premium(user_id) -> bool:
    if await is_admin(user_id): return True
    try:
        uid = int(user_id)
        data = await premium_collection.find_one({"_id": uid})
        if data and data.get("is_premium"):
            expires_at = data.get("expires_at")
            if expires_at and datetime.now(timezone.utc) > expires_at.replace(tzinfo=timezone.utc):
                return True
            else:
                await remove_premium(uid)
                return False
        return False
    except (ValueError, TypeError): return False

# --- SETTINGS FUNCTIONS ---
async def is_maintenance(user_id: int) -> bool:
    if await is_admin(user_id): return False
    data = await maintenance_collection.find_one({"_id": "maintenance"})
    return data is not None and data.get("maintenance") == "on"

async def get_auto_delete_status() -> bool:
    data = await settings_collection.find_one({"_id": "auto_delete"})
    return data.get("status", True) if data else True

async def set_auto_delete_status(status: bool):
    await settings_collection.update_one({"_id": "auto_delete"}, {"$set": {"status": status}}, upsert=True)

async def get_auto_delete_time() -> int:
    data = await settings_collection.find_one({"_id": "auto_delete_time"})
    return data.get("time", 600) if data else 600

async def set_auto_delete_time(time_in_seconds: int):
    await settings_collection.update_one({"_id": "auto_delete_time"}, {"$set": {"time": time_in_seconds}}, upsert=True)

async def get_protect_status() -> bool:
    data = await settings_collection.find_one({"_id": "protect_content"})
    return data.get("status", False) if data else False

async def set_protect_status(status: bool):
    await settings_collection.update_one({"_id": "protect_content"}, {"$set": {"status": status}}, upsert=True)

async def get_force_sub_status() -> bool:
    data = await settings_collection.find_one({"_id": "force_sub"})
    return data.get("status", True) if data else True

async def set_force_sub_status(status: bool):
    await settings_collection.update_one({"_id": "force_sub"}, {"$set": {"status": status}}, upsert=True)

async def get_file_again_status() -> bool:
    data = await settings_collection.find_one({"_id": "get_file_again"})
    return data.get("status", True) if data else True

async def set_file_again_status(status: bool):
    await settings_collection.update_one({"_id": "get_file_again"}, {"$set": {"status": status}}, upsert=True)
    
