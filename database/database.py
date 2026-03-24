# TitanXBots - database.py

import pymongo
from config import DB_URI, DB_NAME, OWNER_ID

# -------------------------------
# DB CONNECTION
# -------------------------------
dbclient = pymongo.MongoClient(DB_URI)
database = dbclient[DB_NAME]

user_data = database['users']
banned_users = database['banned_users']
admins_collection = database['admins']

# -------------------------------
# USER MANAGEMENT
# -------------------------------
async def is_user_present(user_id: int) -> bool:
    return user_data.find_one({'_id': user_id}) is not None


async def add_user(user_id: int, first_name=None, username=None):
    user_data.update_one(
        {'_id': user_id},
        {'$set': {
            '_id': user_id,
            'first_name': first_name,
            'username': username
        }},
        upsert=True
    )


async def get_all_users():
    return [user['_id'] for user in user_data.find()]


async def delete_user(user_id: int):
    user_data.delete_one({'_id': user_id})


# -------------------------------
# BAN SYSTEM (FIXED 🔥)
# -------------------------------
async def is_user_banned(user_id: int) -> bool:
    data = banned_users.find_one({'_id': user_id})
    return data.get("is_banned", False) if data else False


async def get_ban_reason(user_id: int) -> str:
    data = banned_users.find_one({'_id': user_id})
    return data.get("reason", "No reason provided") if data else "No reason provided"


async def ban_user(user_id: int, reason: str = "No reason"):
    banned_users.update_one(
        {"_id": user_id},
        {"$set": {"is_banned": True, "reason": reason}},
        upsert=True
    )


async def unban_user(user_id: int):
    banned_users.update_one(
        {"_id": user_id},
        {"$set": {"is_banned": False, "reason": ""}}
    )


async def get_banned_users():
    return list(banned_users.find({"is_banned": True}))


# -------------------------------
# ADMIN SYSTEM
# -------------------------------
async def add_admin(user_id: int):
    admins_collection.update_one(
        {"_id": user_id},
        {"$set": {"is_admin": True}},
        upsert=True
    )


async def remove_admin(user_id: int):
    admins_collection.delete_one({"_id": user_id})


async def get_admins():
    return [admin["_id"] for admin in admins_collection.find()]


# -------------------------------
# ROLE CHECKS
# -------------------------------
async def is_owner(user_id: int) -> bool:
    return user_id == OWNER_ID


async def is_admin(user_id: int) -> bool:
    return (
        user_id == OWNER_ID or
        admins_collection.find_one({"_id": user_id}) is not None
    )
