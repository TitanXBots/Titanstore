# database.py
import pymongo
from datetime import datetime
from config import DB_URI, DB_NAME, OWNER_ID, ADMINS

# -------------------------------
# Database setup
# -------------------------------
dbclient = pymongo.MongoClient(DB_URI)
database = dbclient[DB_NAME]

user_data = database['users']
banned_users = database['banned_users']
admins = database['admins']  # dynamic admins collection

# -------------------------------
# User management
# -------------------------------
async def present_user(user_id: int) -> bool:
    """Check if a user exists in the database."""
    return user_data.find_one({'_id': user_id}) is not None

async def add_user(user_id: int, first_name: str = "", username: str = ""):
    """Add a user to the database."""
    user_data.update_one(
        {'_id': user_id},
        {'$set': {
            '_id': user_id,
            'first_name': first_name,
            'username': username,
            'joined_at': datetime.utcnow()
        }},
        upsert=True
    )

async def full_userbase() -> list:
    """Return a list of all user IDs."""
    return [doc['_id'] for doc in user_data.find()]

async def del_user(user_id: int):
    """Delete a user from the database."""
    user_data.delete_one({'_id': user_id})

# -------------------------------
# Ban management
# -------------------------------
async def is_banned(user_id: int) -> bool:
    """Check if a user is banned."""
    return banned_users.find_one({'_id': user_id}) is not None

async def get_ban_reason(user_id: int) -> str:
    """Return the ban reason of a user."""
    data = banned_users.find_one({'_id': user_id})
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
# Owner and Admin checks
# -------------------------------
async def is_owner(user_id: int) -> bool:
    """Check if the user is the owner."""
    return user_id == OWNER_ID

async def is_admin(user_id: int) -> bool:
    """Check if the user is admin: OWNER_ID + config ADMINS + DB admins."""
    if user_id == OWNER_ID:
        return True
    if user_id in ADMINS:
        return True
    return admins.find_one({'_id': user_id}) is not None

# -------------------------------
# Dynamic Admin Management
# -------------------------------
async def add_admin(user_id: int):
    """Add a user to the admin collection."""
    admins.update_one(
        {"_id": user_id},
        {"$set": {"added_at": datetime.utcnow()}},
        upsert=True
    )

async def remove_admin(user_id: int):
    """Remove a user from the admin collection."""
    admins.delete_one({"_id": user_id})

async def admin_list() -> list:
    """Return all admins: OWNER_ID + config ADMINS + DB admins."""
    db_admins = [doc['_id'] for doc in admins.find()]
    return list(set([OWNER_ID] + ADMINS + db_admins))  # remove duplicates
