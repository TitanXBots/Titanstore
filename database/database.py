#TitanXBots




import pymongo, os
from config import DB_URI, DB_NAME


dbclient = pymongo.MongoClient(DB_URI)
database = dbclient[DB_NAME]


user_data = database['users']

admin_data = database['admins']




async def present_user(user_id : int):
    found = user_data.find_one({'_id': user_id})
    if found:
        return True
    else:
        return False

async def add_user(user_id: int):
    user_data.insert_one({'_id': user_id})
    return

async def full_userbase():
    user_docs = user_data.find()
    user_ids = []
    for doc in user_docs:
        user_ids.append(doc['_id'])
        
    return user_ids

async def del_user(user_id: int):
    user_data.delete_one({'_id': user_id})
    return

#---------New one -------------
#------------------------------
#TitanXBots


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
    async for doc in admin_data.find():
        admins.append(doc['_id'])
    return admins
