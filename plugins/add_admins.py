# add_admins.py

import asyncio
from database.database import Seishiro

# List of admin Telegram IDs
admins_to_add = [
    5356695781,  # your ID
]


async def add_admins():

    for admin_id in admins_to_add:
        await Seishiro.add_admin(admin_id)
        print(f"✅ Added admin: {admin_id}")

    print("🎉 All admins added successfully!")


asyncio.run(add_admins())
