import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler
from telegram.error import BadRequest

from utils.api_client import api_client
from utils.db import db
from utils.helpers import format_order_details
from utils.constants import CURRENCY_RATES, ORDER_STATUS_EMOJIS, CURRENCY_SYMBOLS
from utils.messages import get_message

# Module logger
logger = logging.getLogger(__name__)

# Define states
STATUS_WAITING_FOR_ID = 0

def status_command(update: Update, context: CallbackContext):
    """Handler for /status command"""
    user = update.effective_user
    db.update_user_activity(user.id)
    
    # Get user's language preference
    language = db.get_language(user.id)
    logger.info(f"User {user.id} language preference: {language}")
    
    # Check if this is a callback query
    if update.callback_query:
        query = update.callback_query
        query.answer()
        
        # If this is the "show_order_ids" callback, display the list of order IDs
        if query.data == "show_order_ids":
            # Get user's orders from database
            orders = db.get_user_orders(user.id, limit=20)
            
            # Get user's total spending
            total_spending = db.get_user_total_spending(user.id)
            
            # Get user's currency preference
            currency_preference = db.get_user_currency_preference(user.id)
            currency_symbol = CURRENCY_SYMBOLS.get(currency_preference, "$")
            
            # Calculate ETB equivalent (always show USD and ETB)
            etb_rate = CURRENCY_RATES.get("ETB", 158.5)
            etb_spending = total_spending * etb_rate if currency_preference == "USD" else total_spending
            usd_spending = total_spending if currency_preference == "USD" else total_spending / etb_rate
            
            if not orders:
                # Create back button
                keyboard = [[InlineKeyboardButton(get_message(language, 'status', 'back_to_main'), callback_data="back_to_main")]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                query.edit_message_text(
                    get_message(language, 'status', 'no_orders'),
                    reply_markup=reply_markup
                )
                return ConversationHandler.END
            
            # Create message with order IDs list
            message = f"<b>💰 Total Spending:</b>\n"
            message += f"USD: ${usd_spending:.2f}\n"
            message += f"ETB: Br{etb_spending:.2f}\n\n"
            message += get_message(language, 'status', 'your_order_ids') + "\n\n"
            
            for order in orders:
                service_name = order.get('service_name', 'Unknown Service')
                # Truncate service name if too long
                if len(service_name) > 25:
                    service_name = service_name[:22] + "..."
                
                # Add status if available
                status = order.get('status', 'pending')
                status_emoji = "⏳" if status.lower() == "pending" else "✅" if status.lower() == "completed" else "🔄"
                
                # Format the order line
                message += f"{status_emoji} <code>{order['id']}</code> - {service_name}\n"
            
            # Create back button
            keyboard = [
                [InlineKeyboardButton(get_message(language, 'status', 'back'), callback_data="check_status")],
                [InlineKeyboardButton(get_message(language, 'status', 'back_to_main'), callback_data="back_to_main")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            query.edit_message_text(
                message,
                reply_markup=reply_markup,
                parse_mode="HTML"
            )
            return STATUS_WAITING_FOR_ID
        
        # Regular status command
        # Create keyboard with options
        keyboard = [
            [InlineKeyboardButton(get_message(language, 'status', 'show_order_ids'), callback_data="show_order_ids")],
            [InlineKeyboardButton(get_message(language, 'status', 'back_to_main'), callback_data="back_to_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Ask for order ID
        query.edit_message_text(
            f"{get_message(language, 'status', 'title')}\n\n"
            f"{get_message(language, 'status', 'enter_order_id')}",
            reply_markup=reply_markup,
            parse_mode="HTML"
        )
        return STATUS_WAITING_FOR_ID
    else:
        # Check if an order ID was provided
        if context.args and len(context.args) > 0:
            # Get status of specific order
            order_id = context.args[0]
            check_specific_order(update, context, order_id)
            return ConversationHandler.END
        else:
            # Create keyboard with options
            keyboard = [
                [InlineKeyboardButton(get_message(language, 'status', 'show_order_ids'), callback_data="show_order_ids")],
                [InlineKeyboardButton(get_message(language, 'status', 'back_to_main'), callback_data="back_to_main")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Ask for order ID
            update.message.reply_html(
                f"{get_message(language, 'status', 'title')}\n\n"
                f"{get_message(language, 'status', 'enter_order_id')}",
                reply_markup=reply_markup
            )
            return STATUS_WAITING_FOR_ID
    
    return

def check_specific_order(update: Update, context: CallbackContext, order_id):
    """Check status of a specific order"""
    user = update.effective_user
    
    # Get user's language preference
    language = db.get_language(user.id)
    logger.info(f"User {user.id} language preference: {language}")
    
    try:
        # Get order status from API
        response = api_client.get_order_status(order_id)
        
        # Get order details from database
        order_details = db.get_order_by_id(order_id)
        
        # If order exists in API but not in our database, save it
        if response and not isinstance(response, list) and not response.get("error"):
            if not order_details:
                # Save this order to the database for future reference
                service_name = response.get('service', 'Unknown Service')
                quantity = response.get('quantity', 0)
                link = response.get('link', '')
                
                # Use the bot_price if available, otherwise use charge with markup
                if 'bot_price' in response:
                    price = float(response['bot_price'])
                else:
                    # Apply 50% markup to the charge
                    price = float(response.get('charge', 0)) * 1.5
                
                # Add order to database
                db.add_order(user.id, order_id, '', service_name, quantity, link, price)
                
                # Refresh order details
                order_details = db.get_order_by_id(order_id)
            
            # Format the response
            status_message = (
                f"{get_message(language, 'status', 'order_status')}\n\n"
                f"{get_message(language, 'status', 'order_id').format(order_id=order_id)}\n"
            )
            
            # Add service name if available from database or API
            service_name = order_details.get('service_name', 'Unknown') if order_details else response.get('service', 'Unknown Service')
            status_message += f"{get_message(language, 'status', 'service').format(service_name=service_name)}\n"
            
            # Add quantity if available
            quantity = order_details.get('quantity', 'Unknown') if order_details else response.get('quantity', 'Unknown')
            status_message += f"{get_message(language, 'status', 'quantity').format(quantity=quantity)}\n"
            
            # Add status
            status = response.get('status', 'Unknown')
            status_message += f"{get_message(language, 'status', 'status').format(status=status)}\n"
            
            # Add price information
            # First priority: Use the price from our database (bot price)
            if order_details and 'price' in order_details:
                bot_price = order_details['price']
                etb_bot_price = bot_price * CURRENCY_RATES.get("ETB", 55)
                status_message += f"{get_message(language, 'status', 'price').format(price=bot_price, etb_price=etb_bot_price)}\n"
            # Second priority: Use bot_price from API response
            elif 'bot_price' in response:
                bot_price = float(response['bot_price'])
                etb_bot_price = bot_price * CURRENCY_RATES.get("ETB", 55)
                status_message += f"{get_message(language, 'status', 'price').format(price=bot_price, etb_price=etb_bot_price)}\n"
            # Last resort: Use charge from API with markup
            elif "charge" in response:
                original_charge = float(response['charge'])
                bot_charge = original_charge * 1.5  # Apply 50% markup
                etb_charge = bot_charge * CURRENCY_RATES.get("ETB", 55)
                status_message += f"{get_message(language, 'status', 'price').format(price=bot_charge, etb_price=etb_charge)}\n"
            
            if "start_count" in response:
                start_count = response['start_count']
                status_message += f"{get_message(language, 'status', 'start_count').format(start_count=start_count)}\n"
            
            if "remains" in response:
                remains = response['remains']
                status_message += f"{get_message(language, 'status', 'remains').format(remains=remains)}\n"
            
            # Create refresh button
            keyboard = [
                [InlineKeyboardButton(get_message(language, 'status', 'refresh'), callback_data=f"refresh_status_{order_id}")],
                [InlineKeyboardButton(get_message(language, 'status', 'back_to_main'), callback_data="back_to_main")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Send or edit message based on update type
            if update.callback_query:
                try:
                    update.callback_query.edit_message_text(
                        status_message,
                        reply_markup=reply_markup,
                        parse_mode="HTML"
                    )
                except Exception as e:
                    # Handle "Message is not modified" error
                    if "message is not modified" in str(e).lower():
                        update.callback_query.answer(get_message(language, 'status', 'status_up_to_date'))
                    else:
                        # For other errors, log and show a notification
                        logger.error(f"Error updating message: {e}")
                        update.callback_query.answer(get_message(language, 'status', 'error_updating'))
            else:
                update.message.reply_html(
                    status_message,
                    reply_markup=reply_markup
                )
            return True
        else:
            # Order not found or error
            error_message = response.get("error", get_message(language, 'status', 'order_not_found'))
            
            # Create back button
            keyboard = [[InlineKeyboardButton(get_message(language, 'status', 'back_to_main'), callback_data="back_to_main")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            if update.callback_query:
                try:
                    update.callback_query.edit_message_text(
                        f"⚠️ {error_message}",
                        reply_markup=reply_markup
                    )
                except Exception as e:
                    # Handle "Message is not modified" error
                    if "message is not modified" in str(e).lower():
                        update.callback_query.answer(get_message(language, 'status', 'status_up_to_date'))
                    else:
                        logger.error(f"Error updating message: {e}")
                        update.callback_query.answer(get_message(language, 'status', 'error_updating'))
            else:
                update.message.reply_html(
                    f"⚠️ {error_message}",
                    reply_markup=reply_markup
                )
            return False
    
    except Exception as e:
        logger.error(f"Error checking order status: {e}")
        error_msg = get_message(language, 'status', 'error_checking').format(error=str(e))
        
        # Create back button
        keyboard = [[InlineKeyboardButton(get_message(language, 'status', 'back_to_main'), callback_data="back_to_main")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if update.callback_query:
            update.callback_query.edit_message_text(
                error_msg,
                reply_markup=reply_markup
            )
        else:
            update.message.reply_html(
                error_msg,
                reply_markup=reply_markup
            )
        return False

def show_recent_orders(update: Update, context: CallbackContext):
    """Show user's recent orders"""
    user = update.effective_user
    
    # Get user's orders from database
    orders = db.get_user_orders(user.id, limit=5)
    
    # Get user's total spending
    total_spending = db.get_user_total_spending(user.id)
    
    # Get user's currency preference
    currency_preference = db.get_user_currency_preference(user.id)
    currency_symbol = CURRENCY_SYMBOLS.get(currency_preference, "$")
    
    # Calculate ETB equivalent (always show USD and ETB)
    etb_rate = CURRENCY_RATES.get("ETB", 158.5)
    etb_spending = total_spending * etb_rate if currency_preference == "USD" else total_spending
    usd_spending = total_spending if currency_preference == "USD" else total_spending / etb_rate
    
    if not orders:
        update.message.reply_text(
            "You don't have any orders yet. Use /services to browse available services and place an order."
        )
        return
    
    # Create message with orders list
    message = f"<b>💰 Total Spending:</b>\n"
    message += f"USD: ${usd_spending:.2f}\n"
    message += f"ETB: Br{etb_spending:.2f}\n\n"
    message += "<b>📋 Your Recent Orders</b>\n\n"
    
    for order in orders:
        # Get service info if available
        service_info = None
        if "service_id" in order:
            services = api_client.get_services()
            for service in services:
                if service.get("service") == order["service_id"]:
                    service_info = service
                    break
        
        # Format order details (don't include the link)
        order_text = (
            f"🔢 <b>Order #<code>{order['id']}</code></b>\n"
            f"📊 Service: {service_info['name'] if service_info else 'Unknown'}\n"
            f"📊 Quantity: {order.get('quantity', 'Unknown')}\n"
            f"💰 Price: {currency_symbol}{order.get('price', 0):.2f}\n"
            f"🕒 Date: {order.get('created_at', 'Unknown')[:10]}"
        )
        message += f"{order_text}\n\n"
    
    # Add list of order IDs for easy copying
    message += "<b>Order IDs for quick copy:</b>\n"
    for order in orders:
        message += f"<code>{order['id']}</code>\n"
    
    message += "\nTo check a specific order, use /status <order_id>"
    
    # Create refresh button
    keyboard = [[InlineKeyboardButton("🔄 Refresh", callback_data="refresh_status")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    update.message.reply_html(message, reply_markup=reply_markup)

def show_recent_orders_callback(update: Update, context: CallbackContext):
    """Show user's recent orders via callback"""
    query = update.callback_query
    user = update.effective_user
    
    # Get user's orders from database
    orders = db.get_user_orders(user.id, limit=5)
    
    # Get user's total spending
    total_spending = db.get_user_total_spending(user.id)
    
    # Get user's currency preference
    currency_preference = db.get_user_currency_preference(user.id)
    currency_symbol = CURRENCY_SYMBOLS.get(currency_preference, "$")
    
    # Calculate ETB equivalent (always show USD and ETB)
    etb_rate = CURRENCY_RATES.get("ETB", 158.5)
    etb_spending = total_spending * etb_rate if currency_preference == "USD" else total_spending
    usd_spending = total_spending if currency_preference == "USD" else total_spending / etb_rate
    
    if not orders:
        query.edit_message_text(
            "You don't have any orders yet. Use /services to browse available services and place an order."
        )
        return
    
    # Create message with orders list
    message = f"<b>💰 Total Spending:</b>\n"
    message += f"USD: ${usd_spending:.2f}\n"
    message += f"ETB: Br{etb_spending:.2f}\n\n"
    message += "<b>📋 Your Recent Orders</b>\n\n"
    
    for order in orders:
        # Get service info if available
        service_info = None
        if "service_id" in order:
            services = api_client.get_services()
            for service in services:
                if service.get("service") == order["service_id"]:
                    service_info = service
                    break
        
        # Format order details (don't include the link)
        order_text = (
            f"🔢 <b>Order #<code>{order['id']}</code></b>\n"
            f"📊 Service: {service_info['name'] if service_info else 'Unknown'}\n"
            f"📊 Quantity: {order.get('quantity', 'Unknown')}\n"
            f"💰 Price: {currency_symbol}{order.get('price', 0):.2f}\n"
            f"🕒 Date: {order.get('created_at', 'Unknown')[:10]}"
        )
        message += f"{order_text}\n\n"
    
    # Add list of order IDs for easy copying
    message += "<b>Order IDs for quick copy:</b>\n"
    for order in orders:
        message += f"<code>{order['id']}</code>\n"
    
    message += "\nTo check a specific order, use /status <order_id>"
    
    # Create refresh button
    keyboard = [[InlineKeyboardButton("🔄 Refresh", callback_data="refresh_status")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    query.edit_message_text(message, reply_markup=reply_markup, parse_mode="HTML")

def refresh_status_callback(update: Update, context: CallbackContext):
    """Handle refresh status button"""
    query = update.callback_query
    
    # Get the order ID from the callback data
    order_id = query.data.split('_')[2]
    
    # Get user's language preference
    user = update.effective_user
    language = db.get_language(user.id)
    logger.info(f"User {user.id} language preference: {language}")
    
    # Answer the callback query
    query.answer(get_message(language, 'status', 'refreshed'))
    
    # Check the order status
    check_specific_order(update, context, order_id)
    
    return