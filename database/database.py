# database.py - TitanXBots Database Management

import pymongo
from config import DB_URI, DB_NAME, OWNER_ID

# -------------------------------
# MongoDB Connection
# -------------------------------
dbclient = pymongo.MongoClient(DB_URI)
database = dbclient[DB_NAME]

# Collections
user_data = database['users']
banned_users = database['banned_users']
admins_collection = database['admins']

# Ensure OWNER_ID is always admin
if not admins_collection.find_one({"user_id": OWNER_ID}):
    admins_collection.insert_one({"user_id": OWNER_ID})

# -------------------------------
# User Management
# -------------------------------
def present_user(user_id: int) -> bool:
    """Check if a user exists in the users collection."""
    return user_data.find_one({"user_id": user_id}) is not None

def add_user(user_id: int, username: str = None) -> bool:
    """Add a new user to the users collection."""
    if present_user(user_id):
        return False
    user_data.insert_one({"user_id": user_id, "username": username})
    return True

def remove_user(user_id: int) -> bool:
    """Remove a user from the users collection."""
    result = user_data.delete_one({"user_id": user_id})
    return result.deleted_count > 0

# -------------------------------
# Banned Users Management
# -------------------------------
def is_banned(user_id: int) -> bool:
    """Check if a user is banned."""
    return banned_users.find_one({"user_id": user_id}) is not None

def ban_user(user_id: int, reason: str = None) -> bool:
    """Ban a user."""
    if is_banned(user_id):
        return False
    banned_users.insert_one({"user_id": user_id, "reason": reason})
    return True

def unban_user(user_id: int) -> bool:
    """Unban a user."""
    result = banned_users.delete_one({"user_id": user_id})
    return result.deleted_count > 0

# -------------------------------
# Admin Management
# -------------------------------
def add_admin(user_id: int) -> bool:
    """Add a new admin. Returns True if added, False if already exists."""
    if admins_collection.find_one({"user_id": user_id}):
        return False
    admins_collection.insert_one({"user_id": user_id})
    return True

def remove_admin(user_id: int) -> bool:
    """Remove an admin. Returns True if removed, False if not found or OWNER_ID."""
    if user_id == OWNER_ID:
        return False  # Owner cannot be removed
    result = admins_collection.delete_one({"user_id": user_id})
    return result.deleted_count > 0

def get_admins() -> list:
    """Return a list of all admin user IDs."""
    return [admin['user_id'] for admin in admins_collection.find()]

def is_admin(user_id: int) -> bool:
    """Check if a user is an admin."""
    return admins_collection.find_one({"user_id": user_id}) is not None
