import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
import telegram

from utils.api_client import api_client
from utils.db import db
from utils.helpers import is_admin
from utils.constants import CURRENCY_RATES

logger = logging.getLogger(__name__)

def account_command(update: Update, context: CallbackContext):
    """Handler for /account command"""
    user = update.effective_user
    db.update_user_activity(user.id)
    
    try:
        # Get local balance from database
        local_balance = db.get_balance(user.id)
        
        # Get user's currency preference
        currency_preference = db.get_currency_preference(user.id)
        
        # Get recent transactions
        transactions = db.get_transactions(user.id, limit=5)
        
        # Check if user is admin
        admin = is_admin(user.id)
        
        # Create message
        message = f"👤 <b>Account Information</b>\n\n"
        
        if admin:
            # For admins, show both website and local balance
            try:
                balance_info = api_client.get_balance()
                website_balance = float(balance_info.get('balance', 0))
                currency = balance_info.get('currency', 'USD')
                message += f"💰 Website Balance: <code>${website_balance:.2f}</code> {currency}\n"
            except Exception as e:
                logger.error(f"Error fetching website balance: {e}")
                message += "💰 Website Balance: <i>Error fetching</i>\n"
        
        # Show local balance based on currency preference
        if currency_preference == 'ETB':
            # Convert USD balance to ETB
            etb_balance = local_balance * CURRENCY_RATES["ETB"]
            formatted_etb = f"{etb_balance:,.0f}"
            message += f"💰 Bot Balance: <code>ETB {formatted_etb}</code> (≈${local_balance:.2f})\n\n"
        else:
            message += f"💰 Bot Balance: <code>${local_balance:.2f}</code>\n\n"
        
        # Add recent transactions if any
        if transactions:
            message += "<b>Recent Transactions:</b>\n"
            for tx in transactions:
                symbol = "+" if tx['type'] == 'credit' else "-"
                
                # Format transaction amount based on currency preference
                if currency_preference == 'ETB':
                    etb_amount = abs(tx['amount']) * CURRENCY_RATES["ETB"]
                    formatted_etb = f"{etb_amount:,.0f}"
                    message += (
                        f"{'💵' if tx['type'] == 'credit' else '🔄'} "
                        f"{symbol}ETB {formatted_etb} (≈${abs(tx['amount']):.2f}) - {tx['description']}\n"
                        f"📅 {tx['created_at'][:10]}\n\n"
                    )
                else:
                    message += (
                        f"{'💵' if tx['type'] == 'credit' else '🔄'} "
                        f"{symbol}${abs(tx['amount']):.2f} - {tx['description']}\n"
                        f"📅 {tx['created_at'][:10]}\n\n"
                    )
        
        message += "To add balance, use /recharge command."
        
        # Create keyboard with refresh and recharge buttons
        keyboard = [
            [InlineKeyboardButton("🔄 Refresh", callback_data="refresh_account")],
            [InlineKeyboardButton("💰 Recharge", callback_data="recharge_account")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        update.message.reply_html(message, reply_markup=reply_markup)
        
    except Exception as e:
        logger.error(f"Error in account command: {e}")
        update.message.reply_text(
            "❌ An error occurred while fetching your account information. Please try again later."
        )

def refresh_account_callback(update: Update, context: CallbackContext):
    """Handle refresh account button"""
    query = update.callback_query
    
    try:
        # Get user info
        user = update.effective_user
        
        # Get local balance from database
        local_balance = db.get_balance(user.id)
        
        # Get user's currency preference
        currency_preference = db.get_currency_preference(user.id)
        
        # Get recent transactions
        transactions = db.get_transactions(user.id, limit=5)
        
        # Check if user is admin
        admin = is_admin(user.id)
        
        # Create message
        message = f"👤 <b>Account Information</b>\n\n"
        
        if admin:
            # For admins, show both website and local balance
            try:
                balance_info = api_client.get_balance()
                website_balance = float(balance_info.get('balance', 0))
                currency = balance_info.get('currency', 'USD')
                message += f"💰 Website Balance: <code>${website_balance:.2f}</code> {currency}\n"
            except Exception as e:
                logger.error(f"Error fetching website balance: {e}")
                message += "💰 Website Balance: <i>Error fetching</i>\n"
        
        # Show local balance based on currency preference
        if currency_preference == 'ETB':
            # Convert USD balance to ETB
            etb_balance = local_balance * CURRENCY_RATES["ETB"]
            formatted_etb = f"{etb_balance:,.0f}"
            message += f"💰 Bot Balance: <code>ETB {formatted_etb}</code> (≈${local_balance:.2f})\n\n"
        else:
            message += f"💰 Bot Balance: <code>${local_balance:.2f}</code>\n\n"
        
        # Add recent transactions if any
        if transactions:
            message += "<b>Recent Transactions:</b>\n"
            for tx in transactions:
                symbol = "+" if tx['type'] == 'credit' else "-"
                
                # Format transaction amount based on currency preference
                if currency_preference == 'ETB':
                    etb_amount = abs(tx['amount']) * CURRENCY_RATES["ETB"]
                    formatted_etb = f"{etb_amount:,.0f}"
                    message += (
                        f"{'💵' if tx['type'] == 'credit' else '🔄'} "
                        f"{symbol}ETB {formatted_etb} (≈${abs(tx['amount']):.2f}) - {tx['description']}\n"
                        f"📅 {tx['created_at'][:10]}\n\n"
                    )
                else:
                    message += (
                        f"{'💵' if tx['type'] == 'credit' else '🔄'} "
                        f"{symbol}${abs(tx['amount']):.2f} - {tx['description']}\n"
                        f"📅 {tx['created_at'][:10]}\n\n"
                    )
        
        message += "To add balance, use /recharge command."
        
        # Create keyboard with refresh and recharge buttons
        keyboard = [
            [InlineKeyboardButton("🔄 Refresh", callback_data="refresh_account")],
            [InlineKeyboardButton("💰 Recharge", callback_data="recharge_account")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        query.edit_message_text(message, reply_markup=reply_markup, parse_mode="HTML")
        
    except Exception as e:
        logger.error(f"Error in refresh account: {e}")
        query.edit_message_text(
            "❌ An error occurred while refreshing your account information. Please try again later."
        )
    
    return 