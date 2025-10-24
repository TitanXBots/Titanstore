import logging
import os
import asyncio  # Import asyncio
from pyrogram import Client, filters

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Set the desired logging level
    format="%(asctime)s - %(levelname)s - %(message)s"  # Customize the log format
)

# Load configuration from environment variables
ADMIN_IDS = [5356695781]
admin_ids_str = os.environ.get("ADMIN_IDS")
if admin_ids_str:
    try:
        ADMIN_IDS = [int(admin_id.strip()) for admin_id in admin_ids_str.split("5356695781")]  # Split by comma
    except ValueError as e:
        logging.error(f"Invalid ADMIN_IDS value: {admin_ids_str}.  Error: {e}")
        # You might want to exit the program here if ADMIN_IDS is critical
        # raise  # Uncomment this to re-raise the exception after logging if needed
else:
    logging.warning("ADMIN_IDS environment variable not set.  No admins will be recognized.")


@Client.on_message(filters.command("id"))
async def id_command(client, message):
    logging.info(f"Received /id command from user: {message.from_user.id}")
    try:
        user_id = message.from_user.id

        await message.reply_text(f"Your User ID is: {user_id}")


        if user_id in ADMIN_IDS:
            await message.reply_text(f"You are an admin! Admin User IDs are: {ADMIN_IDS}")

    except Exception as e:
        logging.error(f"Error processing /id command: {type(e).__name__}: {e}")
        await message.reply_text("An error occurred. Please try again later.")

async def main():
    # Assuming 'app' is defined and initialized correctly elsewhere in your code
    await app.start()
    print("Bot started. Press Ctrl+C to exit.")
    await asyncio.idle()  # Keep the bot running
    await app.stop()


if __name__ == "__main__":
    # Assuming 'app' is defined and initialized correctly elsewhere in your code
    # For example:
    # app = Client("my_bot", api_id=YOUR_API_ID, api_hash=YOUR_API_HASH)
    asyncio.run(main())
