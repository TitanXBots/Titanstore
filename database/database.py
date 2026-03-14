# database.py
import pymongo
from config import DB_URI, DB_NAME, OWNER_ID, ADMINS

# -------------------------------
# Database setup
# -------------------------------
dbclient = pymongo.MongoClient(DB_URI)
database = dbclient[DB_NAME]

user_data = database['users']
banned_users = database['banned_users']
admins_collection = database['admins']

# Ensure owner is always an admin
admins_collection.update_one({'_id': OWNER_ID}, {'$set': {'role': 'owner'}}, upsert=True)

# -------------------------------
# User management
# -------------------------------
async def present_user(user_id: int) -> bool:
    """Check if a user exists in the database."""
    return bool(user_data.find_one({'_id': user_id}))

async def add_user(user_id: int):
    """Add a user to the database."""
    user_data.update_one({'_id': user_id}, {'$set': {'_id': user_id}}, upsert=True)

async def full_userbase() -> list:
    """Return a list of all user IDs."""
    return [doc['_id'] for doc in user_data.find()]

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
# Owner and Admin check
# -------------------------------
async def is_owner(user_id: int) -> bool:
    """Check if the user is the owner."""
    return user_id == OWNER_ID

async def is_admin(user_id: int) -> bool:
    """Check if the user is an admin (Owner is automatically admin)."""
    if user_id == OWNER_ID:
        return True
    return admins_collection.find_one({'_id': user_id}) is not None

# -------------------------------
# Admin management
# -------------------------------
async def add_admin(user_id: int) -> bool:
    """Add a user as admin. Returns False if already admin."""
    if await is_admin(user_id):
        return False
    admins_collection.update_one({'_id': user_id}, {'$set': {'role': 'admin'}}, upsert=True)
    return True

async def remove_admin(user_id: int) -> bool:
    """Remove a user from admins. Returns False if trying to remove owner."""
    if user_id == OWNER_ID:
        return False
    admins_collection.delete_one({'_id': user_id})
    return True

async def list_admins() -> list:
    """Return a list of admin IDs."""
    return [doc['_id'] for doc in admins_collection.find()]
