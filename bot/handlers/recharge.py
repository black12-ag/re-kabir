import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler, CommandHandler, CallbackQueryHandler, MessageHandler, Filters

from utils.db import db
from utils.helpers import is_admin
from utils.constants import CURRENCY_RATES
from utils.messages import get_message

logger = logging.getLogger(__name__)

# States
AMOUNT = 1
RECEIPT = 2

# Admin contact and ID
ADMIN_USERNAME = "@muay011"
# Get the first admin ID for direct messaging
admin_ids_str = os.getenv("ADMIN_USER_ID", "0")
ADMIN_ID = int(admin_ids_str.split(",")[0]) if admin_ids_str else 0
# Get all admin IDs as a list for multiple notifications
ADMIN_IDS = [int(id.strip()) for id in admin_ids_str.split(",")] if admin_ids_str else []

# Wise Contact Information
WISE_CONTACT_INFO = ""

# Currency exchange rates (USD to other currencies)
CURRENCY_RATES = {
    "ETB": 155.5,  # 1 USD = 56.5 ETB (Ethiopian Birr)
    "EUR": 0.925,  # 1 USD = 0.92 EUR
    "GBP": 0.80,  # 1 USD = 0.78 GBP
    "AUD": 1.75,  # 1 USD = 1.52 AUD
    "AED": 3.695,  # 1 USD = 3.67 AED
    "CAD": 1.46,  # 1 USD = 1.37 CAD
}

# Payment details
PAYMENT_METHODS = {
    "cbe": {
        "bank": "🏦 CBE (Commercial Bank of Ethiopia)",
        "account": "1000388630209",
        "name": "Munir Ayub Mohammed"
    },
    "awash": {
        "bank": "🏦 Awash Bank",
        "account": "01425722099900",
        "name": "Munir Ayub Mohammed"
    },
    "abyssinia": {
        "bank": "🏦 Bank of Abyssinia",
        "account": "98216006",
        "name": "Munir Ayub"
    },
    "dashen": {
        "bank": "🏦 Dashen Bank",
        "account": "2944341676911",
        "name": "Munir Ayub Mohammed"
    },
    "amole": {
        "bank": "🏦 Amole (Dashen Bank)",
        "account": "0907806267",
        "name": "Munir Ayub Mohammed"
    },
    "ebirr": {
        "bank": "📱 E-Birr",
        "account": "0907806267",
        "name": "Munir Ayub Mohammed"
    },
    "telebirr": {
        "bank": "📱 Telebirr",
        "account": "0907806267",
        "name": "Munir Ayub Mohammed"
    }
}

# International payment details
INTERNATIONAL_PAYMENT_METHODS = {
    "paypal": {
        "method": "💸 PayPal",
        "details": """Email: muay01111@gmail.com
Phone: +251 90 780 6267""",
        "name": "Munir Ayub Mohammed"
    },
    "skrill": {
        "method": "💰 Skrill",
        "details": """Email: munirayub011@gmail.com
Phone: +251 90 780 6267""",
        "name": "Munir Ayub Mohammed"
    },
    "dukascopy": {
        "method": "🏦 Dukascopy Bank",
        "details": """Customer number: 1472225
Email: munirayub011@gmail.com
Phone: +251 90 780 6267""",
        "name": "Munir Ayub Mohammed"
    }
}

# Cryptocurrency payment details
CRYPTO_PAYMENT_METHODS = {
    "binance": {
        "method": "💰 Binance ID",
        "uid": "392268780",
        "name": "Munir Ayub Mohammed"
    },
    "okx": {
        "method": "💰 OKX UID",
        "uid": "581498229339357572",
        "name": "Munir Ayub Mohammed"
    },
    "kucoin": {
        "method": "💰 KuCoin UID",
        "uid": "125798256",
        "name": "Munir Ayub Mohammed"
    },
    "gate": {
        "method": "💰 Gate.io UID",
        "uid": "7698214",
        "name": "Munir Ayub Mohammed"
    }
}

def recharge_command(update: Update, context: CallbackContext):
    """Handler for /recharge command"""
    user = update.effective_user
    db.update_user_activity(user.id)
    
    # Get user's language preference
    language = db.get_language(user.id)
    logger.info(f"User {user.id} language preference: {language}")
    
    message = (
        f"{get_message(language, 'recharge', 'title')}\n\n"
        f"{get_message(language, 'recharge', 'select_payment_method')}"
    )
    
    # Create keyboard with payment method options
    keyboard = [
        [InlineKeyboardButton("💸 PayPal", callback_data="method_paypal")],
        [InlineKeyboardButton("💰 Skrill", callback_data="method_skrill")],
        [InlineKeyboardButton("🇪🇹 " + get_message(language, 'recharge', 'eth_banks'), callback_data="method_eth")],
        [InlineKeyboardButton(get_message(language, 'recharge', 'intl_options'), callback_data="method_intl")],
        [InlineKeyboardButton(get_message(language, 'recharge', 'crypto'), callback_data="method_crypto")],
        [InlineKeyboardButton(get_message(language, 'recharge', 'cancel'), callback_data="method_cancel")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Check if this is a callback query or direct command
    if update.callback_query:
        query = update.callback_query
        query.answer()
        query.edit_message_text(
            text=message,
            reply_markup=reply_markup,
            parse_mode="HTML"
        )
    else:
        # This is a direct command
        update.message.reply_html(message, reply_markup=reply_markup)
    
    return ConversationHandler.END

def handle_method_selection(update: Update, context: CallbackContext):
    """Handle payment method selection"""
    query = update.callback_query
    user = update.effective_user
    data = query.data.split('_')[1]
    
    # Get user's language preference
    language = db.get_language(user.id)
    logger.info(f"User {user.id} language preference: {language}")
    
    if data == "cancel":
        query.edit_message_text(
            get_message(language, 'recharge', 'cancelled')
        )
        return ConversationHandler.END
    
    # For 'wise', redirect to PayPal for now (until Wise is activated)
    if data == "wise":
        data = "paypal"
    
    # Store selected method in context
    context.user_data['selected_method'] = data
    
    # Show amount options based on payment method
    if data == "eth":
        # For Ethiopian banks, show amounts in ETB
        show_eth_amount_options(update, context)
    elif data in ["paypal", "skrill", "wise"]:
        # For PayPal, Skrill, and Wise, show USD amounts directly
        show_usd_amount_options(update, context)
    else:
        # For other methods, show amounts in USD
        show_usd_amount_options(update, context)
    
    return ConversationHandler.END

def show_eth_amount_options(update: Update, context: CallbackContext):
    """Show amount options in ETB for Ethiopian banks"""
    query = update.callback_query
    
    # Use ETB-specific amounts
    etb_amounts = [100, 200, 500, 1000, 3000, 5000, 10000, 20000]
    
    # Calculate approximate USD equivalents
    usd_equivalents = [round(etb / CURRENCY_RATES["ETB"], 2) for etb in etb_amounts]
    
    message = (
        "💳 <b>Recharge Account - 🇪🇹 Ethiopian Banks</b>\n\n"
        "Please select the amount you want to recharge:\n\n"
        "Choose from preset amounts or click 'Custom Amount' to enter your own."
    )
    
    # Create keyboard with preset amounts in ETB and custom amount option
    keyboard = [
        [
            InlineKeyboardButton(f"ETB {etb_amounts[0]} (≈${usd_equivalents[0]})", callback_data=f"recharge_eth_{usd_equivalents[0]}"),
            InlineKeyboardButton(f"ETB {etb_amounts[1]} (≈${usd_equivalents[1]})", callback_data=f"recharge_eth_{usd_equivalents[1]}")
        ],
        [
            InlineKeyboardButton(f"ETB {etb_amounts[2]} (≈${usd_equivalents[2]})", callback_data=f"recharge_eth_{usd_equivalents[2]}"),
            InlineKeyboardButton(f"ETB {etb_amounts[3]} (≈${usd_equivalents[3]})", callback_data=f"recharge_eth_{usd_equivalents[3]}")
        ],
        [
            InlineKeyboardButton(f"ETB {etb_amounts[4]} (≈${usd_equivalents[4]})", callback_data=f"recharge_eth_{usd_equivalents[4]}"),
            InlineKeyboardButton(f"ETB {etb_amounts[5]} (≈${usd_equivalents[5]})", callback_data=f"recharge_eth_{usd_equivalents[5]}")
        ],
        [
            InlineKeyboardButton(f"ETB {etb_amounts[6]} (≈${usd_equivalents[6]})", callback_data=f"recharge_eth_{usd_equivalents[6]}"),
            InlineKeyboardButton(f"ETB {etb_amounts[7]} (≈${usd_equivalents[7]})", callback_data=f"recharge_eth_{usd_equivalents[7]}")
        ],
        [InlineKeyboardButton("💰 Custom Amount", callback_data="recharge_eth_custom")],
        [InlineKeyboardButton("🔙 Back", callback_data="back_to_methods")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(message, reply_markup=reply_markup, parse_mode="HTML")

def show_usd_amount_options(update: Update, context: CallbackContext):
    """Show amount options in USD for international payments"""
    query = update.callback_query
    user = update.effective_user
    method = context.user_data.get('selected_method', 'intl')
    
    # Get user's language preference
    language = db.get_language(user.id)
    logger.info(f"User {user.id} language preference: {language}")
    
    method_titles = {
        "wise": "PayPal (International)",  # Redirect Wise to PayPal
        "paypal": "PayPal",
        "skrill": "Skrill",
        "intl": "International Options",
        "crypto": "Cryptocurrency"
    }
    
    title = method_titles.get(method, "Recharge")
    
    message = (
        f"{get_message(language, 'recharge', 'title')} - {title}\n\n"
        f"{get_message(language, 'recharge', 'select_amount')}"
    )
    
    # Create keyboard with preset amounts in USD and custom amount option
    keyboard = [
        [
            InlineKeyboardButton("$5", callback_data=f"recharge_{method}_5"),
            InlineKeyboardButton("$10", callback_data=f"recharge_{method}_10"),
            InlineKeyboardButton("$20", callback_data=f"recharge_{method}_20")
        ],
        [
            InlineKeyboardButton("$50", callback_data=f"recharge_{method}_50"),
            InlineKeyboardButton("$100", callback_data=f"recharge_{method}_100"),
            InlineKeyboardButton("$200", callback_data=f"recharge_{method}_200")
        ],
        [
            InlineKeyboardButton("$500", callback_data=f"recharge_{method}_500"),
            InlineKeyboardButton("$1000", callback_data=f"recharge_{method}_1000")
        ],
        [InlineKeyboardButton(get_message(language, 'recharge', 'custom_amount'), callback_data=f"recharge_{method}_custom")],
        [InlineKeyboardButton(get_message(language, 'recharge', 'back'), callback_data="back_to_methods")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(message, reply_markup=reply_markup, parse_mode="HTML")

def handle_back_to_methods(update: Update, context: CallbackContext):
    """Handle back button to return to payment methods"""
    query = update.callback_query
    user = update.effective_user
    
    # Get user's language preference
    language = db.get_language(user.id)
    logger.info(f"User {user.id} language preference: {language}")
    
    message = (
        f"{get_message(language, 'recharge', 'title')}\n\n"
        f"{get_message(language, 'recharge', 'select_payment_method')}"
    )
    
    # Create keyboard with payment method options
    keyboard = [
        [InlineKeyboardButton("💸 PayPal", callback_data="method_paypal")],
        [InlineKeyboardButton("💰 Skrill", callback_data="method_skrill")],
        [InlineKeyboardButton("🇪🇹 " + get_message(language, 'recharge', 'eth_banks'), callback_data="method_eth")],
        [InlineKeyboardButton(get_message(language, 'recharge', 'intl_options'), callback_data="method_intl")],
        [InlineKeyboardButton(get_message(language, 'recharge', 'crypto'), callback_data="method_crypto")],
        [InlineKeyboardButton(get_message(language, 'recharge', 'cancel'), callback_data="method_cancel")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(message, reply_markup=reply_markup, parse_mode="HTML")
    return ConversationHandler.END

def handle_recharge_callback(update: Update, context: CallbackContext):
    """Handle recharge amount selection"""
    query = update.callback_query
    user = update.effective_user
    
    # Get user's language preference
    language = db.get_language(user.id)
    logger.info(f"User {user.id} language preference: {language}")
    
    # Reset any leftover order conversation state
    context.user_data.pop('service_id', None)
    context.user_data.pop('current_service', None)
    context.user_data.pop('order_link', None)
    context.user_data.pop('order_quantity', None)
    
    # Extract method and amount from callback data
    data = query.data.split('_')
    
    # Check if we have enough elements in the data list
    if len(data) < 3:
        # Handle the case where there's no amount_type (like "recharge_account")
        if data[0] == "recharge" and data[1] == "account":
            # Redirect to the recharge command
            return recharge_command(update, context)
        else:
            # Log the unexpected callback data
            logger.warning(f"Unexpected callback data format: {query.data}")
            query.answer("Invalid selection. Please try again.")
            return ConversationHandler.END
    
    # If we have enough elements, proceed as before
    method = data[1]
    amount_type = data[2]
    
    # For 'wise', redirect to PayPal for now (until Wise is activated)
    if method == "wise":
        method = "paypal"
    
    # Ensure we store selected method
    context.user_data['selected_method'] = method
    # Mark this as a recharge conversation to avoid confusion with order conversation
    context.user_data['conversation_type'] = 'recharge'
    
    if amount_type == "custom":
        # Handle custom amount entry
        if method == "eth":
            query.edit_message_text(
                get_message(language, 'recharge', 'custom_amount_etb'),
                parse_mode="HTML"
            )
            context.user_data['custom_amount_type'] = 'eth'
        else:
            query.edit_message_text(
                get_message(language, 'recharge', 'custom_amount_usd'),
                parse_mode="HTML"
            )
            context.user_data['custom_amount_type'] = 'usd'
        return AMOUNT
    
    # Handle preset amount
    amount = float(amount_type)
    
    # Process the amount based on the selected method
    if method == "wise":
        # For Wise, redirect to PayPal
        handle_paypal_direct(update, context, amount)
    elif method == "paypal":
        handle_paypal_direct(update, context, amount)
    elif method == "skrill":
        handle_skrill_direct(update, context, amount)
    elif method == "eth":
        show_bank_options(update, context, amount)
    elif method == "intl":
        show_international_options(update, context, amount)
    elif method == "crypto":
        show_crypto_options(update, context, amount)
    else:
        # Fallback to payment methods selection
        show_payment_methods(update, context, amount)
    
    return ConversationHandler.END

def handle_custom_amount(update: Update, context: CallbackContext):
    """Handle custom recharge amount"""
    user = update.effective_user
    
    # Get user's language preference
    language = db.get_language(user.id)
    logger.info(f"User {user.id} language preference: {language}")
    
    # Verify this is a recharge conversation, not an order
    if context.user_data.get('conversation_type') != 'recharge':
        context.user_data['conversation_type'] = 'recharge'
        logger.warning(f"User {user.id} entered custom amount but conversation type was not set to recharge")
    
    try:
        amount_type = context.user_data.get('custom_amount_type', 'usd')
        method = context.user_data.get('selected_method', 'intl')
        
        amount = float(update.message.text.strip())
        
        # Validate amount based on currency and payment method
        if amount_type == 'eth':
            # For ETB, minimum amount is 100
            if amount < 100:
                update.message.reply_html(
                    f"⚠️ The minimum amount for Ethiopian banks is <b>ETB 100</b>. Please enter a larger amount."
                )
                return AMOUNT
        else:
            # For USD and international methods (Wise, crypto), enforce a $10 minimum
            if method in ["wise", "intl", "crypto"] and amount < 10:
                update.message.reply_html(
                    f"⚠️ The minimum amount for international payments is <b>$10</b>. Please enter a larger amount."
                )
                return AMOUNT
            # For other USD methods, minimum amount is 1
            elif amount < 1:
                update.message.reply_html(
                    get_message(language, 'recharge', 'minimum_amount_usd')
                )
                return AMOUNT
        
        # Clear any order-related data that might be causing confusion
        context.user_data.pop('service_id', None)
        context.user_data.pop('current_service', None)
        context.user_data.pop('order_link', None)
        context.user_data.pop('order_quantity', None)
        
        if amount_type == 'eth':
            # Convert ETB to USD for internal processing
            usd_amount = amount / CURRENCY_RATES["ETB"]
            show_bank_options(update, context, usd_amount, original_etb=amount)
        else:
            # Handle USD amount based on selected method
            if method == "paypal":
                # For text message input, use reply_html instead of edit_message_text
                handle_paypal_direct_message(update, context, amount)
            elif method == "skrill":
                # For text message input, use reply_html instead of edit_message_text
                handle_skrill_direct_message(update, context, amount)
            elif method == "intl":
                # For text message input, use reply_html instead of edit_message_text
                show_international_options_message(update, context, amount)
            elif method == "crypto":
                # For text message input, use reply_html instead of edit_message_text
                show_crypto_options_message(update, context, amount)
            else:
                # Fallback to payment methods selection
                show_payment_methods(update, context, amount)
        
        return ConversationHandler.END
        
    except ValueError:
        currency = "ETB" if context.user_data.get('custom_amount_type') == 'eth' else "$"
        update.message.reply_html(
            get_message(language, 'recharge', 'invalid_amount').format(currency=currency)
        )
        return AMOUNT

def show_bank_options(update: Update, context: CallbackContext, amount: float, original_etb=None):
    """Show available bank options"""
    # Calculate ETB amount if not provided
    etb_amount = original_etb if original_etb is not None else amount * CURRENCY_RATES["ETB"]
    
    # Format ETB amount with commas for better readability
    formatted_etb = f"{etb_amount:,.0f}"
    
    message = (
        f"🏦 <b>Select 🇪🇹 Ethiopian Bank</b>\n\n"
        f"<b>Amount to pay:</b> <code>ETB {formatted_etb}</code> (≈${amount:.2f})\n\n"
        f"Please choose your preferred bank:"
    )
    
    # Create keyboard with bank options
    keyboard = [
        [InlineKeyboardButton("🏦 CBE (Commercial Bank of Ethiopia)", callback_data=f"bank_cbe_{amount}")],
        [InlineKeyboardButton("🏦 Awash Bank", callback_data=f"bank_awash_{amount}")],
        [InlineKeyboardButton("🏦 Bank of Abyssinia", callback_data=f"bank_abyssinia_{amount}")],
        [InlineKeyboardButton("🏦 Dashen Bank", callback_data=f"bank_dashen_{amount}")],
        [InlineKeyboardButton("🏦 Amole (Dashen Bank)", callback_data=f"bank_amole_{amount}")],
        [InlineKeyboardButton("📱 E-Birr", callback_data=f"bank_ebirr_{amount}")],
        [InlineKeyboardButton("📱 Telebirr", callback_data=f"bank_telebirr_{amount}")],
        [InlineKeyboardButton("🔙 Back", callback_data="method_eth")],
        [InlineKeyboardButton("❌ Cancel", callback_data="method_cancel")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        update.callback_query.edit_message_text(
            message,
            reply_markup=reply_markup,
            parse_mode="HTML"
        )
    else:
        update.message.reply_html(message, reply_markup=reply_markup)

def show_payment_methods(update: Update, context: CallbackContext, amount: float):
    """Show available payment methods"""
    message = (
        f"💳 <b>Select Payment Method</b>\n\n"
        f"Amount to recharge: <code>${amount:.2f}</code>\n\n"
        f"Please choose your preferred payment method:"
    )
    
    keyboard = [
        [InlineKeyboardButton("💸 PayPal", callback_data=f"intl_paypal_{amount}")],
        [InlineKeyboardButton("🏦 Ethiopian Banks", callback_data=f"pay_eth_{amount}")],
        [InlineKeyboardButton("🌍 Other International Options", callback_data=f"pay_intl_{amount}")],
        [InlineKeyboardButton("₿ Cryptocurrency", callback_data=f"pay_crypto_{amount}")],
        [InlineKeyboardButton("❌ Cancel", callback_data="pay_cancel")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        update.callback_query.edit_message_text(
            message,
            reply_markup=reply_markup,
            parse_mode="HTML"
        )
    else:
        update.message.reply_html(message, reply_markup=reply_markup)

def show_international_options(update: Update, context: CallbackContext, amount: float):
    """Show available international payment options"""
    message = (
        f"🌍 <b>International Payment Options</b>\n\n"
        f"Amount to pay: <code>${amount:.2f}</code>\n\n"
        f"Please choose your preferred payment method:"
    )
    
    # Create keyboard with international payment options
    keyboard = [
        [InlineKeyboardButton("💸 PayPal", callback_data=f"intl_paypal_{amount}")],
        [InlineKeyboardButton("💰 Skrill", callback_data=f"intl_skrill_{amount}")],
        [InlineKeyboardButton("🇺🇸 USD", callback_data=f"intl_usd_{amount}")],
        [InlineKeyboardButton("🇪🇺 EUR", callback_data=f"intl_eur_{amount}")],
        [InlineKeyboardButton("🇬🇧 GBP", callback_data=f"intl_gbp_{amount}")],
        [InlineKeyboardButton("🇦🇺 AUD", callback_data=f"intl_aud_{amount}")],
        [InlineKeyboardButton("🇦🇪 AED", callback_data=f"intl_aed_{amount}")],
        [InlineKeyboardButton("🇨🇦 CAD", callback_data=f"intl_cad_{amount}")],
        [InlineKeyboardButton("🏦 Dukascopy Bank", callback_data=f"intl_dukascopy_{amount}")],
        [InlineKeyboardButton("💬 Contact Admin Directly", url=f"https://t.me/{ADMIN_USERNAME.replace('@', '')}")],
        [InlineKeyboardButton("🔙 Back", callback_data=f"pay_back_{amount}")],
        [InlineKeyboardButton("❌ Cancel", callback_data="pay_cancel")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Check if this is a callback query or direct message
    if update.callback_query:
        update.callback_query.edit_message_text(
            message,
            reply_markup=reply_markup,
            parse_mode="HTML"
        )
    else:
        update.message.reply_html(
            message,
            reply_markup=reply_markup
        )

def show_crypto_options(update: Update, context: CallbackContext, amount: float):
    """Show available cryptocurrency payment options"""
    message = (
        f"₿ <b>Cryptocurrency Payment Options</b>\n\n"
        f"Amount to pay: <code>${amount:.2f}</code>\n\n"
        f"Please choose your preferred option:"
    )
    
    # Create simplified crypto options
    keyboard = [
        [InlineKeyboardButton("💰 Binance ID", callback_data=f"crypto_binance_{amount}")],
        [InlineKeyboardButton("💰 OKX UID", callback_data=f"crypto_okx_{amount}")],
        [InlineKeyboardButton("💰 KuCoin UID", callback_data=f"crypto_kucoin_{amount}")],
        [InlineKeyboardButton("💰 Gate.io UID", callback_data=f"crypto_gate_{amount}")],
        [InlineKeyboardButton("🔙 Back", callback_data=f"pay_back_{amount}")],
        [InlineKeyboardButton("❌ Cancel", callback_data="pay_cancel")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Check if this is a callback query or direct message
    if update.callback_query:
        update.callback_query.edit_message_text(
            message,
            reply_markup=reply_markup,
            parse_mode="HTML"
        )
    else:
        update.message.reply_html(
            message,
            reply_markup=reply_markup
        )

def handle_payment_method(update: Update, context: CallbackContext):
    """Handle payment method selection"""
    query = update.callback_query
    user = update.effective_user
    data = query.data.split('_')
    
    # Get user's language preference
    language = db.get_language(user.id)
    logger.info(f"User {user.id} language preference: {language}")
    
    if data[1] == "cancel":
        query.edit_message_text(
            get_message(language, 'recharge', 'cancelled')
        )
        return ConversationHandler.END
        
    if data[1] == "back":
        # Go back to payment methods selection
        amount = float(data[2])
        show_payment_methods(update, context, amount)
        return ConversationHandler.END
        
    method = data[1]
    amount = float(data[2])
    
    if method == "eth":
        # Show bank selection options
        show_bank_options(update, context, amount)
        return ConversationHandler.END
    elif method == "intl":
        # Show international payment options
        show_international_options(update, context, amount)
        return ConversationHandler.END
    elif method == "crypto":
        # Show cryptocurrency options
        show_crypto_options(update, context, amount)
        return ConversationHandler.END

def handle_paypal_direct(update: Update, context: CallbackContext, amount: float):
    """Handle direct PayPal payment"""
    # Store payment info in context for later use
    context.user_data['payment_info'] = {
        'amount': amount,
        'amount_local': amount,
        'currency': 'USD',
        'bank': "PayPal Direct Payment",
        'account': "Direct payment via PayPal"
    }
    
    # Get PayPal payment details
    paypal_info = INTERNATIONAL_PAYMENT_METHODS["paypal"]
    
    # Format the details in a cleaner way
    formatted_details = (
        "Email: <code>muay01111@gmail.com</code>\n"
        "Phone: +251 90 780 6267"
    )
    
    message = (
        f"💸 <b>PayPal Direct Payment Details</b>\n\n"
        f"<b>Amount to pay:</b> <code>${amount:.2f}</code>\n\n"
        f"<b>Account Details:</b>\n"
        f"{formatted_details}\n\n"
        f"<b>Payment Instructions:</b>\n"
        f"1. Log in to your PayPal account\n"
        f"2. Send the exact amount shown above\n"
        f"3. Take a screenshot of the payment confirmation\n\n"
        f"After payment, click 'I've Paid' and send the screenshot when prompted."
    )
    
    # Add "I've Paid" and "Back" buttons
    keyboard = [
        [InlineKeyboardButton("✅ I've Paid", callback_data=f"paid_paypal_direct_{amount}")],
        [InlineKeyboardButton("🔙 Back to Options", callback_data=f"pay_intl_{amount}")],
        [InlineKeyboardButton("❌ Cancel", callback_data="pay_cancel")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Check if this is a callback query or direct message
    if update.callback_query:
        update.callback_query.edit_message_text(message, reply_markup=reply_markup, parse_mode="HTML")
    else:
        update.message.reply_html(message, reply_markup=reply_markup)
    
    return ConversationHandler.END

def handle_crypto_selection(update: Update, context: CallbackContext):
    """Handle cryptocurrency selection"""
    query = update.callback_query
    data = query.data.split('_')
    crypto_code = data[1]
    amount = float(data[2])
    
    # Get crypto details
    crypto_info = CRYPTO_PAYMENT_METHODS.get(crypto_code)
    if not crypto_info:
        query.answer("Invalid exchange option")
        return ConversationHandler.END
    
    # Store payment info in context for later use
    context.user_data['payment_info'] = {
        'amount': amount,
        'amount_local': amount,
        'currency': 'USD',
        'bank': crypto_info['method'],
        'account': crypto_info['uid']
    }
    
    # Show only the selected exchange UID
    message = (
        f"💰 <b>{crypto_info['method']}</b>\n\n"
        f"<b>Amount to pay:</b> <code>${amount:.2f}</code>\n\n"
        f"<b>{crypto_info['method']}:</b> <code>{crypto_info['uid']}</code>\n\n"
        f"After payment, click 'I've Paid' and send the screenshot when prompted."
    )
    
    # Add "I've Paid" and "Back" buttons
    keyboard = [
        [InlineKeyboardButton("✅ I've Paid", callback_data=f"paid_crypto_{crypto_code}_{amount}")],
        [InlineKeyboardButton("🔙 Back to Options", callback_data=f"pay_crypto_{amount}")],
        [InlineKeyboardButton("❌ Cancel", callback_data="pay_cancel")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(message, reply_markup=reply_markup, parse_mode="HTML")
    return ConversationHandler.END

def handle_paid_confirmation(update: Update, context: CallbackContext):
    """Handle 'I've Paid' button click"""
    query = update.callback_query
    data = query.data.split('_')
    
    # Handle different payment formats
    if len(data) == 3:  # Standard format: paid_bankcode_amount
        payment_type = "local"
        bank_code = data[1]
        amount = float(data[2])
    elif len(data) == 4:  # International/Crypto/Direct format: paid_intl/crypto/paypal/skrill_methodcode_amount
        payment_type = data[1]  # "intl", "crypto", "paypal", "skrill"
        bank_code = data[2]  # payment method code
        amount = float(data[3])
    else:
        query.answer("Invalid payment data")
        return ConversationHandler.END
    
    message = (
        "📸 <b>Payment Confirmation</b>\n\n"
        "Please send a photo of your payment receipt or transaction confirmation.\n\n"
        "Make sure the following details are clearly visible:\n"
        "- Transaction Date\n"
        "- Amount\n"
        "- Account/Wallet Address\n"
        "- Transaction ID/Reference"
    )
    
    query.edit_message_text(message, parse_mode="HTML")
    
    # Set state to wait for receipt
    context.user_data['receipt_state'] = {
        'payment_type': payment_type,
        'bank_code': bank_code,
        'amount': amount
    }
    return RECEIPT

def handle_receipt_photo(update: Update, context: CallbackContext):
    """Handle receipt photo"""
    user = update.message.from_user
    photo = update.message.photo[-1]  # Get the largest photo
    
    if 'payment_info' not in context.user_data:
        update.message.reply_text(
            "❌ There was an error processing your payment. Please try again using the /recharge command."
        )
        return ConversationHandler.END
    
    payment_info = context.user_data['payment_info']
    amount = payment_info.get('amount', 0)
    
    # Get currency preference
    currency_preference = db.get_currency_preference(user.id)
    
    # Create verification buttons (verify or reject)
    keyboard = [
        [
            InlineKeyboardButton("✅ Verify", callback_data=f"verify_{user.id}_{amount}"),
            InlineKeyboardButton("❌ Reject", callback_data=f"reject_{user.id}_{amount}")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Notify user
    update.message.reply_text(
        "📸 Thank you for sending your payment receipt!\n\n"
        "Your payment is being verified by our administrators. "
        "This usually takes a few minutes to a few hours.\n\n"
        "You will be notified once your payment is verified."
    )
    
    # Prepare admin message
    admin_message = (
        f"💳 <b>New Payment Receipt</b>\n\n"
        f"User: <a href='tg://user?id={user.id}'>{user.first_name}</a>\n"
        f"User ID: <code>{user.id}</code>\n"
        f"Username: @{user.username or 'none'}\n\n"
        f"Amount: <b>${amount:.2f}</b>\n"
        f"Payment Method: {payment_info.get('bank', 'N/A')}\n"
        f"Account: <code>{payment_info.get('account', 'N/A')}</code>\n\n"
        f"Please verify or reject this payment."
    )
    
    # Send to all admins instead of just the first one
    for admin_id in ADMIN_IDS:
        try:
            context.bot.send_photo(
                chat_id=admin_id,  # Send to each admin
                photo=photo.file_id,
                caption=admin_message,
                parse_mode="HTML",
                reply_markup=reply_markup
            )
            logger.info(f"Sent payment verification to admin {admin_id}")
        except Exception as e:
            logger.error(f"Failed to send payment verification to admin {admin_id}: {e}")
    
    # Clear payment info from context
    context.user_data.pop('payment_info', None)
    context.user_data.pop('receipt_state', None)
    
    return ConversationHandler.END

def handle_verification(update: Update, context: CallbackContext):
    """Handle admin's verification decision"""
    query = update.callback_query
    
    # Only admin can verify payments
    if not is_admin(query.from_user.id):
        query.answer("You are not authorized to perform this action.")
        return ConversationHandler.END
    
    # Extract data from callback
    data = query.data.split('_')
    action = data[0]  # 'verify' or 'reject'
    user_id = int(data[1])
    amount = float(data[2])
    
    # Get user's currency preference
    currency_preference = db.get_currency_preference(user_id)
    
    if action == "verify":
        # Add balance to user's account
        db.add_balance(user_id, amount, "Payment verification")
        
        # Default to ETB for currency preference if not specified in callback data
        # This is for backward compatibility with existing buttons
        if len(data) > 3 and data[3] == "etb":
            db.update_currency_preference(user_id, "ETB")
            currency_preference = "ETB"
        
        # Notify all admins that the payment was verified
        verification_message = f"✅ Payment Verified\n\n" \
                               f"User ID: {user_id}\n" \
                               f"Amount: ${amount:.2f}\n" \
                               f"Verified by: {query.from_user.first_name} (ID: {query.from_user.id})"
                               
        # Update message for the admin who verified
        query.edit_message_caption(caption=verification_message)
        
        # Notify other admins about the verification
        for admin_id in ADMIN_IDS:
            # Skip the admin who already verified (they already got the updated message)
            if admin_id != query.from_user.id:
                try:
                    context.bot.send_message(
                        chat_id=admin_id,
                        text=verification_message,
                        parse_mode="HTML"
                    )
                except Exception as e:
                    logger.error(f"Failed to notify admin {admin_id} about verification: {e}")
        
        # Prepare notification based on currency preference
        if currency_preference == 'ETB':
            etb_amount = amount * CURRENCY_RATES["ETB"]
            notification = (
                f"💰 <b>Payment Verified!</b>\n\n"
                f"Your payment of <b>${amount:.2f}</b> (ETB {etb_amount:.2f}) has been verified.\n"
                f"Your balance has been updated.\n\n"
                f"Thank you for using our service!"
            )
        else:
            notification = (
                f"💰 <b>Payment Verified!</b>\n\n"
                f"Your payment of <b>${amount:.2f}</b> has been verified.\n"
                f"Your balance has been updated.\n\n"
                f"Thank you for using our service!"
            )
        
        # Notify user
        try:
            context.bot.send_message(
                chat_id=user_id,
                text=notification,
                parse_mode="HTML"
            )
        except Exception as e:
            logger.error(f"Failed to notify user {user_id} about payment verification: {e}")
    
    elif action == "reject":
        # Notify all admins that the payment was rejected
        rejection_message = f"❌ Payment Rejected\n\n" \
                           f"User ID: {user_id}\n" \
                           f"Amount: ${amount:.2f}\n" \
                           f"Rejected by: {query.from_user.first_name} (ID: {query.from_user.id})"
                           
        # Update message for the admin who rejected
        query.edit_message_caption(caption=rejection_message)
        
        # Notify other admins about the rejection
        for admin_id in ADMIN_IDS:
            # Skip the admin who already rejected (they already got the updated message)
            if admin_id != query.from_user.id:
                try:
                    context.bot.send_message(
                        chat_id=admin_id,
                        text=rejection_message,
                        parse_mode="HTML"
                    )
                except Exception as e:
                    logger.error(f"Failed to notify admin {admin_id} about rejection: {e}")
        
        # Notify user
        try:
            context.bot.send_message(
                chat_id=user_id,
                text=(
                    f"❌ <b>Payment Rejected</b>\n\n"
                    f"Your payment of <b>${amount:.2f}</b> could not be verified.\n"
                    f"Please contact support for assistance."
                ),
                parse_mode="HTML"
            )
        except Exception as e:
            logger.error(f"Failed to notify user {user_id} about payment rejection: {e}")
    
    return ConversationHandler.END

def handle_bank_selection(update: Update, context: CallbackContext):
    """Handle bank selection"""
    query = update.callback_query
    data = query.data.split('_')
    bank_code = data[1]
    amount = float(data[2])
    
    # Calculate ETB amount
    etb_amount = amount * CURRENCY_RATES["ETB"]
    
    # Format ETB amount with commas for better readability
    formatted_etb = f"{etb_amount:,.0f}"
    
    bank_info = PAYMENT_METHODS[bank_code]
    
    # Store payment info in context for later use
    context.user_data['payment_info'] = {
        'amount': amount,
        'amount_local': etb_amount,
        'currency': 'ETB',
        'bank': bank_info['bank'],
        'account': bank_info['account'],
        'is_ethiopian_bank': True  # Flag to identify Ethiopian bank payments
    }
    
    message = (
        f"🏦 <b>{bank_info['bank']} Payment Details</b>\n\n"
        f"<b>Amount to pay:</b> <code>ETB {formatted_etb}</code> (≈${amount:.2f})\n\n"
        f"<b>Account Details:</b>\n"
        f"Account Number: <code>{bank_info['account']}</code>\n"
        f"Account Name: {bank_info['name']}\n\n"
        f"<b>Payment Instructions:</b>\n"
        f"1. Log in to your bank account or mobile banking app\n"
        f"2. Make a transfer of <b>ETB {formatted_etb}</b> using the details above\n"
        f"3. Take a screenshot of the payment confirmation\n\n"
        f"After payment, click 'I've Paid' and send the screenshot when prompted."
    )
    
    # Add "I've Paid" and "Back" buttons
    keyboard = [
        [InlineKeyboardButton("✅ I've Paid", callback_data=f"paid_{bank_code}_{amount}")],
        [InlineKeyboardButton("🔙 Back to Banks", callback_data="method_eth")],
        [InlineKeyboardButton("❌ Cancel", callback_data="method_cancel")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(message, reply_markup=reply_markup, parse_mode="HTML")
    return ConversationHandler.END

def handle_international_selection(update: Update, context: CallbackContext):
    """Handle international payment method selection"""
    query = update.callback_query
    data = query.data.split('_')
    payment_code = data[1]
    
    # Handle direct Wise payment - redirect to PayPal
    if payment_code == "wise" and data[2] == "direct":
        amount = float(data[3])
        return handle_paypal_direct(update, context, amount)
    
    # Handle direct PayPal payment
    if payment_code == "paypal":
        amount = float(data[2])
        return handle_paypal_direct(update, context, amount)
    
    # Handle direct Skrill payment
    if payment_code == "skrill":
        amount = float(data[2])
        return handle_skrill_direct(update, context, amount)
    
    # Normal flow for currency-specific payments
    amount = float(data[2])
    
    # Handle Currencies
    if payment_code in ["usd", "eur", "gbp", "aud", "aed", "cad"]:
        # Store payment info in context for later use
        context.user_data['payment_info'] = {
            'amount': amount,
            'currency': payment_code.upper(),
            'bank': f"International Transfer - {payment_code.upper()}",
        }
        
        # Define currency details
        currency_details = {
            "usd": {
                "title": "Us Dollar",
                "flag": "🇺🇸",
                "iban": "CH6408843147222521010",
                "currency": "USD",
                "intermediary_bank": "BANKING CIRCLE",
                "intermediary_address": "S.A., LUXEMBOURG",
                "intermediary_swift": "BCIRLULLXXX"
            },
            "eur": {
                "title": "Euro",
                "flag": "🇪🇺",
                "iban": "CH8508843147222521020",
                "currency": "EUR",
                "intermediary_bank": "SWISS EURO CLEARING BANK GMBH",
                "intermediary_address": "Frankfurt am Main, Germany",
                "intermediary_swift": "SECGDEFFXXX"
            },
            "gbp": {
                "title": "British Pound",
                "flag": "🇬🇧",
                "iban": "CH3808843147222521090",
                "currency": "GBP",
                "intermediary_bank": "BANK CIC LTD",
                "intermediary_address": "Basle, Switzerland",
                "intermediary_swift": "CIALCHBBXXX"
            },
            "aud": {
                "title": "Australian Dollar",
                "flag": "🇦🇺",
                "iban": "CH7208843147222521060",
                "currency": "AUD",
                "intermediary_bank": "BANK CIC LTD",
                "intermediary_address": "Basle, Switzerland",
                "intermediary_swift": "CIALCHBBXXX"
            },
            "aed": {
                "title": "AED",
                "flag": "🇦🇪",
                "iban": "CH9308843147222521070",
                "currency": "AED",
                "intermediary_bank": "BANKING CIRCLE",
                "intermediary_address": "S.A., LUXEMBOURG",
                "intermediary_swift": "BCIRLULLXXX"
            },
            "cad": {
                "title": "Canadian Dollar",
                "flag": "🇨🇦",
                "iban": "CH1708843147222521080",
                "currency": "CAD",
                "intermediary_bank": "BANK CIC LTD",
                "intermediary_address": "Basle, Switzerland",
                "intermediary_swift": "CIALCHBBXXX"
            }
        }
        
        details = currency_details.get(payment_code)
        
        message = (
            f"{details['flag']} <b>{details['title']}</b>\n\n"
            f"<b>Amount to pay:</b> <code>${amount:.2f}</code>\n\n"
            f"<b>Beneficiary</b>\n"
            f"Full name: Munir Ayub Mohammed\n"
            f"Address: Jogol, 752,, 3200, Harar, Ethiopia\n"
            f"IBAN: <code>{details['iban']}</code>\n"
            f"Currency: {details['currency']}\n\n"
            f"<b>Beneficiary Bank Details</b>\n"
            f"Bank Name: Dukascopy Bank SA\n"
            f"Bank Address: Route de Pré-Bois 20, 1215 Geneva, Switzerland\n"
            f"BIC/SWIFT: <code>DUBACHGG</code>\n\n"
            f"<b>Intermediary Bank Details</b>\n"
            f"Bank Name: {details['intermediary_bank']}\n"
            f"Bank Address: {details['intermediary_address']}\n"
            f"BIC/SWIFT: <code>{details['intermediary_swift']}</code>\n\n"
            f"<b>Payment Instructions:</b>\n"
            f"1. Log in to your bank account\n"
            f"2. Make a transfer using the details above\n"
            f"3. Take a screenshot of the payment confirmation\n\n"
            f"After payment, click 'I've Paid' and send the screenshot when prompted."
        )
        
        # Add "I've Paid" and "Back" buttons
        keyboard = [
            [InlineKeyboardButton("✅ I've Paid", callback_data=f"paid_intl_{payment_code}_{amount}")],
            [InlineKeyboardButton("🔙 Back to Options", callback_data=f"pay_intl_{amount}")],
            [InlineKeyboardButton("❌ Cancel", callback_data="method_cancel")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(message, reply_markup=reply_markup, parse_mode="HTML")
        
        # Notify admin about the currency selection
        admin_message = (
            f"🌐 <b>New Currency Payment Request</b>\n\n"
            f"User: <a href='tg://user?id={query.from_user.id}'>{query.from_user.first_name}</a>\n"
            f"User ID: <code>{query.from_user.id}</code>\n"
            f"Username: @{query.from_user.username or 'none'}\n\n"
            f"Requested Currency: {details['flag']} {details['currency']}\n"
            f"Amount: <b>${amount:.2f}</b>\n\n"
            f"Please contact the user if needed."
        )
        
        # Send to all admins
        for admin_id in ADMIN_IDS:
            try:
                context.bot.send_message(
                    chat_id=admin_id,
                    text=admin_message,
                    parse_mode="HTML"
                )
                logger.info(f"Sent currency selection notification to admin {admin_id}")
            except Exception as e:
                logger.error(f"Failed to send currency notification to admin {admin_id}: {e}")
        
        return ConversationHandler.END
    
    # Handle Dukascopy
    elif payment_code == "dukascopy":
        payment_info = INTERNATIONAL_PAYMENT_METHODS["dukascopy"]
        
        # Store payment info in context for later use
        context.user_data['payment_info'] = {
            'amount': amount,
            'bank': payment_info['method'],
            'account': payment_info['details']
        }
        
        method_name = payment_info['method']
        
        message = (
            f"🏦 🏦 <b>Dukascopy Bank Payment Details</b>\n\n"
            f"<b>Amount to pay:</b> <code>${amount:.2f}</code>\n\n"
            f"<b>Account Details:</b>\n"
            f"Customer number: <code>1472225</code>\n"
            f"Email: munirayub011@gmail.com\n"
            f"Phone: +251 90 780 6267\n\n"
            f"<b>Payment Instructions:</b>\n"
            f"1. Log in to your Dukascopy account\n"
            f"2. Make a transfer using the details above\n"
            f"3. Take a screenshot of the payment confirmation\n\n"
            f"After payment, click 'I've Paid' and send the screenshot when prompted."
        )
    else:
        query.answer("Invalid payment method")
        return ConversationHandler.END
    
    # Add "I've Paid" and "Back" buttons
    keyboard = [
        [InlineKeyboardButton("✅ I've Paid", callback_data=f"paid_intl_{payment_code}_{amount}")],
        [InlineKeyboardButton("🔙 Back to Options", callback_data="method_intl")],
        [InlineKeyboardButton("❌ Cancel", callback_data="method_cancel")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(message, reply_markup=reply_markup, parse_mode="HTML")
    return ConversationHandler.END

def show_international_options_message(update: Update, context: CallbackContext, amount: float):
    """Show available international payment options - for direct message input"""
    message = (
        f"🌍 <b>International Payment Options</b>\n\n"
        f"Amount to pay: <code>${amount:.2f}</code>\n\n"
        f"Please choose your preferred payment method:"
    )
    
    # Create keyboard with international payment options
    keyboard = [
        [InlineKeyboardButton("💸 PayPal", callback_data=f"intl_paypal_{amount}")],
        [InlineKeyboardButton("💰 Skrill", callback_data=f"intl_skrill_{amount}")],
        [InlineKeyboardButton("🇺🇸 USD", callback_data=f"intl_usd_{amount}")],
        [InlineKeyboardButton("🇪🇺 EUR", callback_data=f"intl_eur_{amount}")],
        [InlineKeyboardButton("🇬🇧 GBP", callback_data=f"intl_gbp_{amount}")],
        [InlineKeyboardButton("🇦🇺 AUD", callback_data=f"intl_aud_{amount}")],
        [InlineKeyboardButton("🇦🇪 AED", callback_data=f"intl_aed_{amount}")],
        [InlineKeyboardButton("🇨🇦 CAD", callback_data=f"intl_cad_{amount}")],
        [InlineKeyboardButton("🏦 Dukascopy Bank", callback_data=f"intl_dukascopy_{amount}")],
        [InlineKeyboardButton("💬 Contact Admin Directly", url=f"https://t.me/{ADMIN_USERNAME.replace('@', '')}")],
        [InlineKeyboardButton("🔙 Back", callback_data=f"pay_back_{amount}")],
        [InlineKeyboardButton("❌ Cancel", callback_data="pay_cancel")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_html(
        message,
        reply_markup=reply_markup
    )

def show_crypto_options_message(update: Update, context: CallbackContext, amount: float):
    """Show available cryptocurrency payment options - for direct message input"""
    message = (
        f"₿ <b>Cryptocurrency Payment Options</b>\n\n"
        f"Amount to pay: <code>${amount:.2f}</code>\n\n"
        f"Please choose your preferred option:"
    )
    
    # Create simplified crypto options
    keyboard = [
        [InlineKeyboardButton("💰 Binance ID", callback_data=f"crypto_binance_{amount}")],
        [InlineKeyboardButton("💰 OKX UID", callback_data=f"crypto_okx_{amount}")],
        [InlineKeyboardButton("💰 KuCoin UID", callback_data=f"crypto_kucoin_{amount}")],
        [InlineKeyboardButton("💰 Gate.io UID", callback_data=f"crypto_gate_{amount}")],
        [InlineKeyboardButton("🔙 Back", callback_data=f"pay_back_{amount}")],
        [InlineKeyboardButton("❌ Cancel", callback_data="pay_cancel")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_html(
        message,
        reply_markup=reply_markup
    )

def handle_paypal_direct(update: Update, context: CallbackContext, amount: float):
    """Handle direct PayPal payment"""
    # Get PayPal payment details
    payment_info = INTERNATIONAL_PAYMENT_METHODS["paypal"]
    
    # Extract email from details
    email = payment_info['details'].split('\n')[0].replace('Email: ', '')
    
    # Store payment info in context for later use
    context.user_data['payment_info'] = {
        'amount': amount,
        'amount_local': amount,
        'currency': 'USD',
        'bank': payment_info['method'],
        'account': email
    }
    
    # Format the details
    formatted_details = payment_info['details']
    
    message = (
        f"💸 <b>PayPal Payment Details</b>\n\n"
        f"<b>Amount to pay:</b> <code>${amount:.2f}</code>\n\n"
        f"<b>Account Details:</b>\n"
        f"{formatted_details}\n\n"
        f"<b>Payment Instructions:</b>\n"
        f"1. Log in to your PayPal account\n"
        f"2. Send the exact amount shown above\n"
        f"3. Add your Telegram ID in the note/message\n"
        f"4. Take a screenshot of the payment confirmation\n\n"
        f"After payment, click 'I've Paid' and send the screenshot when prompted."
    )
    
    # Add "I've Paid" and "Back" buttons
    keyboard = [
        [InlineKeyboardButton("✅ I've Paid", callback_data=f"paid_paypal_direct_{amount}")],
        [InlineKeyboardButton("🔙 Back to Options", callback_data=f"pay_intl_{amount}")],
        [InlineKeyboardButton("❌ Cancel", callback_data="pay_cancel")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Check if this is a callback query or direct message
    if update.callback_query:
        update.callback_query.edit_message_text(message, reply_markup=reply_markup, parse_mode="HTML")
    else:
        update.message.reply_html(message, reply_markup=reply_markup)
    
    return ConversationHandler.END

def handle_skrill_direct(update: Update, context: CallbackContext, amount: float):
    """Handle direct Skrill payment"""
    # Get Skrill payment details
    payment_info = INTERNATIONAL_PAYMENT_METHODS["skrill"]
    
    # Extract email from details
    email = payment_info['details'].split('\n')[0].replace('Email: ', '')
    
    # Store payment info in context for later use
    context.user_data['payment_info'] = {
        'amount': amount,
        'amount_local': amount,
        'currency': 'USD',
        'bank': payment_info['method'],
        'account': email
    }
    
    formatted_details = payment_info['details']
    
    message = (
        f"💰 <b>Skrill Payment Details</b>\n\n"
        f"<b>Amount to pay:</b> <code>${amount:.2f}</code>\n\n"
        f"<b>Account Details:</b>\n"
        f"{formatted_details}\n\n"
        f"<b>Payment Instructions:</b>\n"
        f"1. Log in to your Skrill account\n"
        f"2. Send the exact amount shown above\n"
        f"3. Add your Telegram ID in the message\n"
        f"4. Take a screenshot of the payment confirmation\n\n"
        f"After payment, click 'I've Paid' and send the screenshot when prompted."
    )
    
    # Add "I've Paid" and "Back" buttons
    keyboard = [
        [InlineKeyboardButton("✅ I've Paid", callback_data=f"paid_skrill_direct_{amount}")],
        [InlineKeyboardButton("🔙 Back to Options", callback_data=f"pay_intl_{amount}")],
        [InlineKeyboardButton("❌ Cancel", callback_data="pay_cancel")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Check if this is a callback query or direct message
    if update.callback_query:
        update.callback_query.edit_message_text(message, reply_markup=reply_markup, parse_mode="HTML")
    else:
        update.message.reply_html(message, reply_markup=reply_markup)
    
    return ConversationHandler.END

def cleanup_recharge_data(update, context):
    """Clean up recharge-related data when conversation ends"""
    # Clear all data related to recharge
    context.user_data.pop('custom_amount_type', None)
    context.user_data.pop('selected_method', None)
    context.user_data.pop('conversation_type', None)
    context.user_data.pop('service_id', None)  # Also clear any order-related data
    context.user_data.pop('current_service', None)
    context.user_data.pop('order_link', None)
    context.user_data.pop('order_quantity', None)
    
    return ConversationHandler.END

# Create conversation handler
recharge_conv_handler = ConversationHandler(
    entry_points=[
        CommandHandler('recharge', recharge_command),
        CallbackQueryHandler(handle_method_selection, pattern=r'^method_'),
        CallbackQueryHandler(handle_back_to_methods, pattern=r'^back_to_methods$'),
        CallbackQueryHandler(handle_recharge_callback, pattern=r'^recharge_'),
        CallbackQueryHandler(handle_payment_method, pattern=r'^pay_'),
        CallbackQueryHandler(handle_bank_selection, pattern=r'^bank_'),
        CallbackQueryHandler(handle_international_selection, pattern=r'^intl_'),
        CallbackQueryHandler(handle_crypto_selection, pattern=r'^crypto_'),
        CallbackQueryHandler(handle_paid_confirmation, pattern=r'^paid_'),
        CallbackQueryHandler(handle_verification, pattern=r'^verify_|^reject_')
    ],
    states={
        AMOUNT: [MessageHandler(Filters.text & ~Filters.command, handle_custom_amount)],
        RECEIPT: [MessageHandler(Filters.photo & ~Filters.command, handle_receipt_photo)]
    },
    fallbacks=[CommandHandler('cancel', cleanup_recharge_data)],
    allow_reentry=True
)

# No need for separate callback handlers since they're included in the conversation handler 