# database.py

import pymongo
from config import DB_URI, DB_NAME, OWNER_ID

# -------------------------------
# Database connection
# -------------------------------
dbclient = pymongo.MongoClient(DB_URI)
database = dbclient[DB_NAME]

# Collections
user_data = database['users']
banned_users = database['banned_users']
admin_data = database['admins']  # Dynamic admin collection

# -------------------------------
# User management
# -------------------------------
async def present_user(user_id: int) -> bool:
    """Check if a user exists in the database."""
    found = user_data.find_one({'_id': user_id})
    return bool(found)

async def add_user(user_id: int):
    """Add a user to the database."""
    user_data.update_one({'_id': user_id}, {'$set': {'_id': user_id}}, upsert=True)

async def full_userbase() -> list:
    """Return a list of all user IDs."""
    users = user_data.find()
    return [doc['_id'] for doc in users]

async def del_user(user_id: int):
    """Delete a user from the database."""
    user_data.delete_one({'_id': user_id})

# -------------------------------
# Ban and Unban management
# -------------------------------
async def is_banned(user_id: int) -> bool:
    """Check if a user is banned."""
    return banned_users.find_one({"_id": user_id}) is not None

async def get_ban_reason(user_id: int) -> str:
    """Return the ban reason of a user."""
    data = banned_users.find_one({"_id": user_id})
    return data.get("reason", "No reason provided") if data else "No reason provided"

async def ban_user(user_id: int, reason: str):
    """Ban a user with a reason."""
    banned_users.update_one(
        {"_id": user_id},
        {"$set": {"reason": reason}},
        upsert=True
    )

async def unban_user(user_id: int):
    """Unban a user."""
    banned_users.delete_one({"_id": user_id})

async def banned_users_list() -> list:
    """Return a list of all banned users."""
    return list(banned_users.find())

# -------------------------------
# Admin management
# -------------------------------
async def add_admin(user_id: int):
    """Add a user as an admin."""
    admin_data.update_one({'_id': user_id}, {'$set': {'_id': user_id}}, upsert=True)

async def remove_admin(user_id: int):
    """Remove a user from admin."""
    admin_data.delete_one({'_id': user_id})

async def get_all_admins() -> list:
    """Return a list of all admin IDs (Owner is included automatically)."""
    admins = [OWNER_ID]  # Owner is always admin
    db_admins = admin_data.find()
    admins.extend(doc['_id'] for doc in db_admins)
    return admins

async def is_admin(user_id: int) -> bool:
    """Check if a user is an admin (Owner is always admin)."""
    if user_id == OWNER_ID:
        return True
    found = admin_data.find_one({'_id': user_id})
    return bool(found)

# -------------------------------
# Owner check
# -------------------------------
async def is_owner(user_id: int) -> bool:
    """Check if the user is the owner."""
    return user_id == OWNER_ID
