# -------------------------------
# IMPORTS
# -------------------------------
from motor.motor_asyncio import AsyncIOMotorClient
from config import DB_URI, DB_NAME, OWNER_ID
from datetime import datetime, timezone

# -------------------------------
# DB CONNECTION
# -------------------------------
client = AsyncIOMotorClient(DB_URI)
database = client[DB_NAME]

user_data = database["users"]
banned_users = database["banned_users"]
admins_collection = database["admins"]

# -------------------------------
# INIT (INDEXES)
# -------------------------------
async def init_db():
    await user_data.create_index("_id", unique=True)
    await banned_users.create_index("_id", unique=True)  # FIXED
    await banned_users.create_index([("is_banned", 1)])
    await admins_collection.create_index("_id", unique=True)


# -------------------------------
# USER MANAGEMENT
# -------------------------------
async def is_user_present(user_id: int) -> bool:
    data = await user_data.find_one({"_id": user_id}, {"_id": 1})
    return data is not None


async def add_user(user_id: int, first_name=None, username=None):
    now = datetime.now(timezone.utc)

    update_data = {
        "last_seen": now
    }

    if first_name is not None:
        update_data["first_name"] = first_name

    if username is not None:
        update_data["username"] = username

    update_query = {
        "$setOnInsert": {
            "_id": user_id,
            "created_at": now
        },
        "$set": update_data
    }

    await user_data.update_one(
        {"_id": user_id},
        update_query,
        upsert=True
    )


async def get_all_users():
    async for user in user_data.find({}, {"_id": 1}):
        yield user["_id"]


async def delete_user(user_id: int):
    if user_id == OWNER_ID:
        return
    await user_data.delete_one({"_id": user_id})


async def get_user_count():
    return await user_data.count_documents({})


# -------------------------------
# BAN SYSTEM
# -------------------------------
async def is_user_banned(user_id: int) -> bool:
    data = await banned_users.find_one(
        {"_id": user_id},
        {"is_banned": 1}
    )
    return bool(data and data.get("is_banned"))


async def get_ban_reason(user_id: int) -> str:
    data = await banned_users.find_one(
        {"_id": user_id},
        {"reason": 1}
    )
    return data.get("reason", "No reason provided") if data else "No reason provided"


async def ban_user(user_id: int, reason: str = "No reason"):
    if user_id == OWNER_ID:  # FIXED: prevent owner ban
        return

    await banned_users.update_one(
        {"_id": user_id},
        {
            "$set": {
                "is_banned": True,
                "reason": reason,
                "banned_at": datetime.now(timezone.utc)
            }
        },
        upsert=True
    )


async def unban_user(user_id: int):
    await banned_users.update_one(
        {"_id": user_id},
        {
            "$set": {
                "is_banned": False,
                "unbanned_at": datetime.now(timezone.utc)
            }
        }
    )
    # Optional cleanup:
    # await banned_users.delete_one({"_id": user_id})


async def get_banned_users():
    async for user in banned_users.find(
        {"is_banned": True},
        {"_id": 1, "reason": 1}
    ):
        yield user


# -------------------------------
# ADMIN SYSTEM
# -------------------------------
async def add_admin(user_id: int):
    await admins_collection.update_one(
        {"_id": user_id},
        {
            "$setOnInsert": {
                "_id": user_id,
                "added_at": datetime.now(timezone.utc)
            }
        },
        upsert=True
    )


async def remove_admin(user_id: int):
    if user_id == OWNER_ID:
        return
    await admins_collection.delete_one({"_id": user_id})


async def get_admins():
    async for admin in admins_collection.find({}, {"_id": 1}):
        yield admin["_id"]


# -------------------------------
# ROLE CHECKS
# -------------------------------
async def is_owner(user_id: int) -> bool:
    return user_id == OWNER_ID


async def is_admin(user_id: int) -> bool:
    if user_id == OWNER_ID:
        return True

    data = await admins_collection.find_one({"_id": user_id})
    return data is not None
