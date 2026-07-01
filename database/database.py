import motor.motor_asyncio
from config import DB_URI, DB_NAME, OWNER_ID

# ---------------- DB CONNECTION ----------------
client = motor.motor_asyncio.AsyncIOMotorClient(DB_URI)
db = client[DB_NAME]

users = db["users"]
banned = db["banned_users"]
admins = db["admins"]
files = db["files"]
maintenance = db["maintenance"]


# ---------------- USERS ----------------
async def add_user(user_id: int, first_name=None, username=None):
    await users.update_one(
        {"_id": user_id},
        {"$set": {
            "_id": user_id,
            "first_name": first_name,
            "username": username
        }},
        upsert=True
    )


async def get_user(user_id: int):
    return await users.find_one({"_id": user_id})


# ---------------- ADMIN SYSTEM ----------------
async def is_admin(user_id: int) -> bool:
    if user_id == OWNER_ID:
        return True
    return bool(await admins.find_one({"_id": user_id}))


async def add_admin(user_id: int):
    await admins.update_one(
        {"_id": user_id},
        {"$set": {"is_admin": True}},
        upsert=True
    )


async def remove_admin(user_id: int):
    await admins.delete_one({"_id": user_id})


async def get_admins():
    return await admins.find({}, {"_id": 1}).to_list(length=None)


# ---------------- BAN SYSTEM ----------------
async def ban_user(user_id: int, reason="No reason"):
    await banned.update_one(
        {"_id": user_id},
        {"$set": {"is_banned": True, "reason": reason}},
        upsert=True
    )


async def unban_user(user_id: int):
    await banned.update_one(
        {"_id": user_id},
        {"$set": {"is_banned": False, "reason": ""}},
        upsert=True
    )


async def is_banned(user_id: int) -> bool:
    data = await banned.find_one({"_id": user_id})
    return bool(data and data.get("is_banned"))


async def get_ban_reason(user_id: int):
    data = await banned.find_one({"_id": user_id})
    return data.get("reason", "No reason")


# ---------------- MAINTENANCE ----------------
async def set_maintenance(state: bool):
    await maintenance.update_one(
        {"_id": "mode"},
        {"$set": {"state": state}},
        upsert=True
    )


async def is_maintenance() -> bool:
    data = await maintenance.find_one({"_id": "mode"})
    return bool(data and data.get("state"))


# ---------------- FILE STORAGE (SAFE LINK SYSTEM) ----------------
async def save_file(message_id: int) -> str:
    import uuid

    file_id = str(uuid.uuid4())

    await files.insert_one({
        "_id": file_id,
        "message_id": message_id
    })

    return file_id


async def get_file(file_id: str):
    return await files.find_one({"_id": file_id})
