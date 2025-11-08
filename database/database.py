#TitanXBots

import pymongo, os
from config import DB_URI, DB_NAME

dbclient = pymongo.MongoClient(DB_URI)
database = dbclient[DB_NAME]

user_data = database['users']
banned_users = database['banned_users']

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
# Ban system
# -------------------------------
async def ban_user(user_id: int, reason: str = "No reason provided"):
    """Ban a user with an optional reason."""
    banned_users.update_one(
        {'_id': user_id},
        {'$set': {'reason': reason}},
        upsert=True
    )

async def unban_user(user_id: int):
    """Unban a user."""
    banned_users.delete_one({'_id': user_id})

async def is_banned(user_id: int):
    """Check if user is banned."""
    return banned_users.find_one({'_id': user_id}) is not None

async def get_ban_reason(user_id: int):
    """Get ban reason."""
    user = banned_users.find_one({'_id': user_id})
    return user['reason'] if user else None

#TitanXBots
