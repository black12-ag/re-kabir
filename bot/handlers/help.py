from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
import os
from utils.db import db
from utils.messages import get_message
from utils.helpers import is_admin
import logging

# Set up logger
logger = logging.getLogger(__name__)

def help_command(update: Update, context: CallbackContext) -> None:
    """Show help information and contact details."""
    user_id = update.effective_user.id
    language = db.get_language(user_id)
    
    # Get admin username from environment variable
    admin_username = os.getenv("ADMIN_USERNAME", "admin")
    
    # Ensure the admin username doesn't start with @
    if admin_username.startswith('@'):
        admin_username = admin_username[1:]
    
    # Get help text from messages
    help_text = (
        f"{get_message(language, 'help', 'title')}\n\n"
        f"<b>Available commands:</b>\n"
        f"/start - Start the bot\n"
        f"/services - Browse available services\n"
        f"/order - Place a new order\n"
        f"/balance - Check your balance\n"
        f"/status - Check order status\n"
        f"/referrals - View your referrals\n"
        f"/support - Contact customer support\n"
        f"/tutorial - View interactive tutorials\n"
        f"/help - Show this help message\n"
    )
    
    # Add admin help option if user is admin
    if is_admin(user_id):
        help_text += f"/adminhelp - Show admin commands\n"
    
    help_text += (
        f"\n{get_message(language, 'help', 'description')}\n"
        f"If you need assistance, you can contact our support team directly through the bot."
    )
    
    # Create keyboard with support button
    keyboard = [
        [InlineKeyboardButton("📚 View Tutorials", callback_data="tutorial")],
        [InlineKeyboardButton(get_message(language, 'help', 'contact_support'), url=f"https://t.me/{admin_username}")],
        [InlineKeyboardButton(get_message(language, 'help', 'back_to_menu'), callback_data="back_to_main")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Handle both callback queries and direct messages
    if update.callback_query:
        update.callback_query.answer()
        update.callback_query.edit_message_text(
            text=help_text,
            reply_markup=reply_markup,
            parse_mode="HTML"
        )
    else:
        update.message.reply_text(
            text=help_text,
            reply_markup=reply_markup,
            parse_mode="HTML"
        )
        
    return

def admin_help_command(update: Update, context: CallbackContext) -> None:
    """Show all available admin commands."""
    user_id = update.effective_user.id
    
    # Check if user is admin
    if not is_admin(user_id):
        update.message.reply_text("❌ You don't have permission to use this command.")
        return
    
    # Create a comprehensive list of admin commands
    admin_help_text = (
        "🔧 <b>ADMIN COMMANDS</b>\n\n"
        "<b>Main Commands:</b>\n"
        "/admin - Open the admin panel with all options\n"
        "/adminhelp - Show this help message\n\n"
        
        "<b>Welcome Message:</b>\n"
        "/setwelcome [text] - Set a new welcome message\n"
        "/setwelcomem - Set welcome message media (photo/video)\n\n"
        
        "<b>User Management:</b>\n"
        "/addbalance [user_id] [amount] - Add balance to a user\n"
        "/removebalance [user_id] [amount] - Remove balance from a user\n\n"
        
        "<b>System Settings:</b>\n"
        "/setbonus [amount] - Set the new user bonus amount\n"
        "/togglebonus - Enable/disable new user bonus\n"
        "/setcurrency [rate] - Set currency exchange rate\n"
        "/setprice [service_id] [price] - Set custom price for a service\n"
        "/resetprice [service_id] - Reset service price to default\n\n"
        
        "<b>Communication:</b>\n"
        "/broadcast - Send a message to all users\n"
        "/broadcast_photo - Send a photo to all users\n"
        "/broadcast_video - Send a video to all users\n\n"
        
        "<b>Referrals:</b>\n"
        "/referrals [user_id] - View referrals for a specific user\n"
        "/approvebonus [bonus_id] - Approve a referral bonus\n"
        "/rejectbonus [bonus_id] - Reject a referral bonus\n"
        "/setreferralthreshold [count] - Set the referral threshold\n"
        "/setreferralbonus [amount] - Set the referral bonus amount in ETB\n\n"
        
        "Use the /admin command to access all these features through the admin panel interface."
    )
    
    # Create keyboard with back button
    keyboard = [
        [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="back_to_main")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Send the admin help message
    update.message.reply_html(
        text=admin_help_text,
        reply_markup=reply_markup
    )
    
    logger.info(f"Admin help shown to user {user_id}")
    return