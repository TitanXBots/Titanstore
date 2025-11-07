#TitanXBots

import pymongo, os
from config import DB_URI, DB_NAME

dbclient = pymongo.MongoClient(DB_URI)
database = dbclient[DB_NAME]

admin_data = database['admins']


async def is_admin(user_id: int):
    """Check if user is admin"""
    return admin_data.find_one({'_id': user_id}) is not None


async def add_admin(user_id: int):
    """Add user as admin"""
    if not await is_admin(user_id):
        admin_data.insert_one({'_id': user_id})
        return True
    return False


async def remove_admin(user_id: int):
    """Remove admin"""
    admin_data.delete_one({'_id': user_id})
    return True


async def get_admins():
    """Return all admin IDs"""
    admins = []
    for doc in admin_data.find():
        admins.append(doc['_id'])
    return admins
