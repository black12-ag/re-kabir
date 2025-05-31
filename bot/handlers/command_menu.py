from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import CallbackContext, CommandHandler, MessageHandler, Filters
import logging
from utils.db import db
from utils.helpers import is_admin
from utils.messages import get_message

# Module logger
logger = logging.getLogger(__name__)

def get_command_keyboard(user_id):
    """Generate a command keyboard without sending any message"""
    # Check if user is admin
    is_user_admin = is_admin(user_id)
    
    # Create a keyboard with command buttons in a grid layout (2 per row)
    # Using only the commands without translated names
    keyboard = [
        [KeyboardButton("/start"), KeyboardButton("/services")],
        [KeyboardButton("/recharge"), KeyboardButton("/balance")],
        [KeyboardButton("/status"), KeyboardButton("/referrals")],
        [KeyboardButton("/help"), KeyboardButton("/support")]
    ]
    
    # Add admin commands if user is admin
    if is_user_admin:
        keyboard.append([KeyboardButton("/admin"), KeyboardButton("/adminhelp")])
    
    # Create and return the keyboard markup
    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=False  # Make it persistent
    )

def show_command_menu(update: Update, context: CallbackContext) -> None:
    """Show a persistent keyboard with common commands"""
    user = update.effective_user
    
    # Get the keyboard
    reply_markup = get_command_keyboard(user.id)
    
    # Apply the keyboard with a minimal message
    try:
        # Only show the "Commands:" message if this isn't immediately after a welcome message
        if not context.user_data.get('welcome_shown', False):
            # Use "Commands:" as the message text
            update.message.reply_text(
                "Commands:",
                reply_markup=reply_markup
            )
        else:
            # Just set the keyboard without sending another message
            update.message.reply_markup = reply_markup
            # Reset the welcome_shown flag since we've handled it
            context.user_data['welcome_shown'] = False
            logger.info(f"Applied command menu without message (welcome already shown) for user {user.id}")
            
        context.user_data['command_menu_active'] = True
    except Exception as e:
        logger.error(f"Error showing command menu: {e}")
    
    logger.info(f"Showing command menu for user {user.id}")

def hide_command_menu(update: Update, context: CallbackContext) -> None:
    """Hide the persistent keyboard"""
    try:
        update.message.reply_text(
            "Menu hidden.",
            reply_markup=ReplyKeyboardRemove()
        )
        context.user_data['command_menu_active'] = False
        logger.info(f"Hiding command menu for user {update.effective_user.id}")
    except Exception as e:
        logger.error(f"Error hiding command menu: {e}")

def toggle_command_menu(update: Update, context: CallbackContext) -> None:
    """Toggle the command menu on/off"""
    user_id = update.effective_user.id
    
    # Check if the user has the menu active (stored in user_data)
    menu_active = context.user_data.get('command_menu_active', False)
    
    if menu_active:
        # Hide the menu
        hide_command_menu(update, context)
    else:
        # Show the menu
        show_command_menu(update, context)

def get_command_menu_handlers():
    """Return the handlers for the command menu"""
    return [
        CommandHandler('menu', toggle_command_menu),
        CommandHandler('showmenu', show_command_menu),
        CommandHandler('hidemenu', hide_command_menu)
    ]