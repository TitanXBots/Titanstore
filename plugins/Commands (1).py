import logging
import asyncio
from pyrogram import Client, filters
from config import ADMINS  # ✅ Import ADMINS from config.py

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Initialize bot client

@Client.on_message(filters.command("id"))
async def id_command(client, message):
    logging.info(f"Received /id command from user: {message.from_user.id}")
    try:
        user_id = message.from_user.id
        await message.reply_text(f"Your User ID is: `{user_id}`")

        if user_id in ADMINS:
            await message.reply_text(f"✅ You are an admin!\nAdmin User IDs: {ADMINS}")
        else:
            await message.reply_text("❌ You are not an admin.")

    except Exception as e:
        logging.error(f"Error processing /id command: {type(e).__name__}: {e}")
        await message.reply_text("An error occurred. Please try again later.")

async def main():
    await app.start()
    print("✅ Bot started. Press Ctrl+C to exit.")
    await asyncio.get_running_loop().create_future()  # Keeps the bot running
    await app.stop()

if __name__ == "__main__":
    asyncio.run(main())
