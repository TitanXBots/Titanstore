# TitanXBots - database.py (Motor Async Version)

from motor.motor_asyncio import AsyncIOMotorClient
from config import DB_URI, DB_NAME, OWNER_ID

# -------------------------------
# DB CONNECTION (ASYNC)
# -------------------------------
client = AsyncIOMotorClient(DB_URI)
db = client[DB_NAME]

user_data = db['users']
banned_users = db['banned_users']
admins_collection = db['admins']

# -------------------------------
# USER MANAGEMENT
# -------------------------------
async def is_user_present(user_id: int) -> bool:
    """Check if user exists"""
    return await user_data.find_one({'_id': user_id}) is not None


async def add_user(user_id: int, first_name=None, username=None):
    """Add or update user"""
    await user_data.update_one(
        {'_id': user_id},
        {'$set': {
            '_id': user_id,
            'first_name': first_name,
            'username': username
        }},
        upsert=True
    )


async def get_all_users():
    """Get all user IDs"""
    users = []
    async for user in user_data.find():
        users.append(user['_id'])
    return users


async def delete_user(user_id: int):
    """Delete user"""
    await user_data.delete_one({'_id': user_id})


async def get_user_by_username(username: str):
    """Find user by username (for ban by username feature)"""
    return await user_data.find_one({"username": username})


# -------------------------------
# BAN SYSTEM
# -------------------------------
async def is_user_banned(user_id: int) -> bool:
    """Check if user is banned"""
    data = await banned_users.find_one({'_id': user_id})
    return data.get("is_banned", False) if data else False


async def get_ban_reason(user_id: int) -> str:
    """Get ban reason"""
    data = await banned_users.find_one({'_id': user_id})
    return data.get("reason", "No reason provided") if data else "No reason provided"


async def ban_user(user_id: int, reason: str = "No reason"):
    """Ban user"""
    await banned_users.update_one(
        {"_id": user_id},
        {"$set": {"is_banned": True, "reason": reason}},
        upsert=True
    )


async def unban_user(user_id: int):
    """Unban user"""
    await banned_users.update_one(
        {"_id": user_id},
        {"$set": {"is_banned": False, "reason": ""}}
    )


async def get_banned_users():
    """Get all banned users"""
    users = []
    async for user in banned_users.find({"is_banned": True}):
        users.append(user)
    return users


async def search_banned_user(user_id: int):
    """Search banned user"""
    return await banned_users.find_one({"_id": user_id, "is_banned": True})


# -------------------------------
# ADMIN SYSTEM
# -------------------------------
async def add_admin(user_id: int):
    """Add admin"""
    await admins_collection.update_one(
        {"_id": user_id},
        {"$set": {"is_admin": True}},
        upsert=True
    )


async def remove_admin(user_id: int):
    """Remove admin"""
    await admins_collection.delete_one({"_id": user_id})


async def get_admins():
    """Get all admins"""
    admins = []
    async for admin in admins_collection.find():
        admins.append(admin["_id"])
    return admins


async def search_admin(user_id: int):
    """Search admin"""
    return await admins_collection.find_one({"_id": user_id})


# -------------------------------
# ROLE CHECKS
# -------------------------------
async def is_owner(user_id: int) -> bool:
    """Check owner"""
    return user_id == OWNER_ID


async def is_admin(user_id: int) -> bool:
    """Check admin or owner"""
    if user_id == OWNER_ID:
        return True
    return await admins_collection.find_one({"_id": user_id}) is not None


# -------------------------------
# STATS (OPTIONAL BUT USEFUL)
# -------------------------------
async def total_users_count() -> int:
    return await user_data.count_documents({})


async def total_banned_count() -> int:
    return await banned_users.count_documents({"is_banned": True})


async def total_admins_count() -> int:
    return await admins_collection.count_documents({})
