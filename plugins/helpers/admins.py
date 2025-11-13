#TitanXBots/helpers/admins.py
from config import ADMINS, OWNER_ID
from database import list_admins

async def is_full_admin(user_id: int) -> bool:
    """Check if a user is owner or admin (from config or DB)."""
    if user_id == OWNER_ID:
        return True
    db_admins = await list_admins()
    return user_id in db_admins or user_id in ADMINS
