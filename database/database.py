#TitanXBots

import pymongo, os
from config import DB_URI, DB_NAME

dbclient = pymongo.MongoClient(DB_URI)
database = dbclient[DB_NAME]

user_data = database['users']
banned_users = database['banned_users']
admin_data = database['admins']  # <-- NEW COLLECTION

# -------------------------------
# User management
# -------------------------------
async def present_user(user_id: int):
    found = user_data.find_one({'_id': user_id})
    return bool(found)

async def add_user(user_id: int):
    user_data.update_one({'_id': user_id}, {'$set': {'_id': user_id}}, upsert=True)

async def full_userbase():
    users = user_data.find()
    return [doc['_id'] for doc in users]

async def del_user(user_id: int):
    user_data.delete_one({'_id': user_id})

# -------------------------------
# Ban and Unban management 
# -------------------------------
async def is_banned(user_id: int) -> bool:
    return banned_users.find_one({"_id": user_id}) is not None


async def get_ban_reason(user_id: int) -> str:
    data = banned_users.find_one({"_id": user_id})
    return data.get("reason", "No reason provided") if data else "No reason provided"


async def ban_user(user_id: int, reason: str):
    banned_users.update_one(
        {"_id": user_id},
        {"$set": {"reason": reason}},
        upsert=True
    )


async def unban_user(user_id: int):
    banned_users.delete_one({"_id": user_id})
    
# -------------------------------
# Admin Management
# -------------------------------
async def add_admin(user_id: int):
    """Add a user as admin."""
    admin_data.update_one({'_id': user_id}, {'$set': {'_id': user_id}}, upsert=True)

async def remove_admin(user_id: int):
    """Remove a user from admin list."""
    admin_data.delete_one({'_id': user_id})

async def list_admins() -> list:
    """Return a list of all admin user IDs."""
    return [doc['_id'] for doc in admin_data.find()]

async def is_admin(user_id: int) -> bool:
    """Check if a user is admin."""
    return admin_data.find_one({'_id': user_id}) is not None
