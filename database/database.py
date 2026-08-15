import motor.motor_asyncio
from config import DB_URI, DB_NAME, OWNER_ID, ADMINS, CHANNEL_ID, FORCE_SUB_CHANNEL_1, FORCE_SUB_CHANNEL_2, FORCE_SUB_CHANNEL_3, FORCE_SUB_CHANNEL_4

dbclient = motor.motor_asyncio.AsyncIOMotorClient(DB_URI)
database = dbclient[DB_NAME]
db = database  # Added compatibility alias for plugins importing 'db'

user_data = database["users"]
banned_users = database["banned_users"]
admins_collection = database["admins"]
maintenance_collection = database["maintenance"]
settings_collection = database["settings"]
media_col = database["media"]

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

async def is_user_present(user_id: int) -> bool:
    return await user_data.find_one({"_id": user_id}) is not None

async def add_user(user_id: int, first_name=None, username=None):
    user = await user_data.find_one({"_id": user_id})
    if not user:
        await user_data.insert_one({
            "_id": user_id,
            "first_name": first_name,
            "username": username
        })
    else:
        await user_data.update_one(
            {"_id": user_id},
            {"$set": {"first_name": first_name, "username": username}}
        )

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
    
