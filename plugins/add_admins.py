# add_admins.py
import pymongo
from config import DB_URI, DB_NAME

# Connect to MongoDB
client = pymongo.MongoClient(DB_URI)
db = client[DB_NAME]
admin_collection = db['admins']

# List of admin Telegram user IDs
admins_to_add = [
    5356695781,  # Replace with your Telegram ID
    # Add more IDs as needed
]

for admin_id in admins_to_add:
    admin_collection.update_one(
        {'_id': admin_id},
        {'$set': {'_id': admin_id}},
        upsert=True
    )
    print(f"✅ Added admin: {admin_id}")

print("All admins added successfully!")
