
import logging
from pyrogram.types import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- In-memory storage for user settings ---
# In a real bot, you'd use a database (e.g., SQLite, PostgreSQL, MongoDB)
# Example structure: {user_id: {'protect_content': True/False}}
user_settings = {}

# --- Callback data constants ---
CALLBACK_PROTECT_ENABLE = "protect_enable"
CALLBACK_PROTECT_DISABLE = "protect_disable"
CALLBACK_BACK = "back_to_main_settings" # For the 'back' button

# --- Helper function to generate the message text and keyboard ---
def get_protect_content_message_and_keyboard(user_id: int) -> tuple[str, InlineKeyboardMarkup]:
    """Generates the text and inline keyboard for the Protect Content menu."""
    
    # Get current status for the user, default to False (disabled) if not found
    is_protect_content_enabled = user_settings.get(user_id, {}).get('protect_content', False)

    status_text = "Enabled âœ…" if is_protect_content_enabled else "Disabled âŒ"

    message_text = (
        "<b>Protect Content</b>\n"
        "Restrict other users from forwarding contents from your shareable link.\n\n"
        "<b>Available Mode's:</b>\n"
        "1) <b>Enable:</b> Forwarding is blocked. Once you create a link with this mode, the restriction "
        "remains even if you later disabled this feature.\n\n"
        "2) <b>Disable:</b> Forwarding restrictions depend on whether the \"no forward\" feature is "
        "currently enabled in the bot. If enabled, forwarding is restricted, This applies to "
        "all links, including those created before; if disabled, forwarding is allowed.\n\n"
        f"- status: {status_text}"
    )

    buttons = []
    if is_protect_content_enabled:
        # If enabled, show a "Disable" button
        buttons.append(InlineKeyboardButton("Disable âŒ", callback_data=CALLBACK_PROTECT_DISABLE))
    else:
        # If disabled, show an "Enable" button
        buttons.append(InlineKeyboardButton("Enable âœ…", callback_data=CALLBACK_PROTECT_ENABLE))

    keyboard = InlineKeyboardMarkup([
        buttons, # Row with Enable/Disable button
        [InlineKeyboardButton("â® back", callback_data=CALLBACK_BACK)] # Row with Back button
    ])

    return message_text, keyboard

# --- Command Handler for /settings or /protect_content ---
async def protect_content_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends the Protect Content settings message with inline keyboard."""
    user_id = update.effective_user.id
    
    message_text, keyboard = get_protect_content_message_and_keyboard(user_id)
    
    await update.message.reply_text(
        text=message_text,
        reply_markup=keyboard,
        parse_mode='HTML' # Use HTML for bold tags
    )
    logger.info(f"User {user_id} opened protect content settings.")

# --- Callback Handler for the 'Enable' button ---
async def handle_protect_enable_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles the 'Enable' button press."""
    query = update.callback_query
    user_id = query.from_user.id

    await query.answer() # Acknowledge the button press (removes loading spinner)

    # Ensure user_settings has an entry for this user
    if user_id not in user_settings:
        user_settings[user_id] = {}
    
    # Update the setting
    user_settings[user_id]['protect_content'] = True
    logger.info(f"User {user_id} enabled protect content.")

    # Generate new message and keyboard based on updated state
    message_text, keyboard = get_protect_content_message_and_keyboard(user_id)

    # Edit the existing message
    await query.edit_message_text(
        text=message_text,
        reply_markup=keyboard,
        parse_mode='HTML'
    )

# --- Callback Handler for the 'Disable' button ---
async def handle_protect_disable_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles the 'Disable' button press."""
    query = update.callback_query
    user_id = query.from_user.id

    await query.answer() # Acknowledge the button press

    # Ensure user_settings has an entry for this user
    if user_id not in user_settings:
        user_settings[user_id] = {}
        
    # Update the setting
    user_settings[user_id]['protect_content'] = False
    logger.info(f"User {user_id} disabled protect content.")

    # Generate new message and keyboard based on updated state
    message_text, keyboard = get_protect_content_message_and_keyboard(user_id)

    # Edit the existing message
    await query.edit_message_text(
        text=message_text,
        reply_markup=keyboard,
        parse_mode='HTML'
    )

# --- Callback Handler for the 'Back' button ---
async def handle_back_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles the 'Back' button press. In a real bot, this would lead to a parent menu."""
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer(text="Going back...", show_alert=False) # Acknowledge, optionally show a small toast

    logger.info(f"User {user_id} pressed back from protect content settings.")
    # For this example, we'll just acknowledge.
    # In a full bot, you would likely:
    # 1. Edit the message to show the *previous* settings menu.
    # 2. Or navigate to a different state in a ConversationHandler.
    # For now, the message will remain as the protect content menu.


def main() -> None:
    """Starts the bot."""
    # Replace "YOUR_BOT_TOKEN" with your actual bot token
    application = Application.builder().token("7701286571:AAHmZpW5TDrJSF61bWQ_GT0oE5zzjH86EKo").build()

    # Register command handlers
    application.add_handler(CommandHandler("settings", protect_content_command))
    application.add_handler(CommandHandler("protect_content", protect_content_command))

    # Register callback query handlers
    # The pattern uses a regex to match the exact callback_data constant
    application.add_handler(CallbackQueryHandler(handle_protect_enable_callback, pattern=f"^{CALLBACK_PROTECT_ENABLE}$"))
    application.add_handler(CallbackQueryHandler(handle_protect_disable_callback, pattern=f"^{CALLBACK_PROTECT_DISABLE}$"))
    application.add_handler(CallbackQueryHandler(handle_back_callback, pattern=f"^{CALLBACK_BACK}$"))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
