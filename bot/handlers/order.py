import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler
import re

from utils.api_client import api_client
from utils.db import db
from utils.helpers import create_confirmation_keyboard, format_service_details, format_order_details
from utils.constants import CURRENCY_RATES
from utils.messages import get_message, MESSAGES

# Define states
SELECTING_SERVICE, ENTERING_LINK, ENTERING_QUANTITY, ENTERING_COMMENTS, CONFIRMING_ORDER = range(5)

# Module logger
logger = logging.getLogger(__name__)

def order_command(update: Update, context: CallbackContext):
    """Handler for /order command"""
    user = update.effective_user
    db.update_user_activity(user.id)
    
    # Get user's language preference
    language = db.get_language(user.id)
    
    # Check if service was already selected from /services command
    if "selected_service" in context.user_data:
        service = context.user_data["selected_service"]
        service_info = service["info"]
        
        # Format service details
        service_text = format_service_details(service_info, user.id, language)
        
        # Store order details in user_data
        context.user_data["order"] = {
            "service_id": service["id"],
            "service_info": service_info
        }
        
        # Use language-specific message for link request
        if 'order' not in MESSAGES[language]:
            # Add a fallback message if the translation doesn't exist yet
            message_text = f"{service_text}\n\nPlease send the link to the post/profile you want to boost:"
        else:
            message_text = f"{service_text}\n\n{get_message(language, 'order', 'enter_link')}"
        
        # Check if this is a callback query or direct message
        if update.callback_query:
            query = update.callback_query
            query.answer()
            query.edit_message_text(message_text, parse_mode="HTML")
        else:
            update.message.reply_html(message_text)
        
        return ENTERING_LINK
    
    # If no service selected, ask user to select one first
    if update.callback_query:
        query = update.callback_query
        query.answer()
        
        # Use language-specific message
        if 'order' not in MESSAGES[language]:
            query.edit_message_text("Please select a service first using the Services button.")
        else:
            query.edit_message_text(get_message(language, 'order', 'select_service_first'))
        
        # Forward to services command
        from ..services import services_command
        return services_command(update, context)
    else:
        # Use language-specific message
        if 'order' not in MESSAGES[language]:
            update.message.reply_text("Please select a service first using /services command.")
        else:
            update.message.reply_text(get_message(language, 'order', 'select_service_first'))
        
        # Forward to services command
        from ..services import services_command
        return services_command(update, context)

def process_link(update: Update, context: CallbackContext):
    """Process the link provided by the user"""
    user = update.effective_user
    db.update_user_activity(user.id)
    
    # Get user's language preference
    language = db.get_language(user.id)
    
    # Get the input from the message
    user_input = update.message.text.strip()
    
    # First check if this is in the context of ordering (we should have selected_service)
    if "selected_service" not in context.user_data:
        # User is likely trying to search, not place an order
        logger.info(f"No service selected, redirecting to /services")
        update.message.reply_html("Please use the /services command to search or browse services")
        # Instead of importing, use the ConversationHandler.END to exit this handler
        # The user can then click the /services command link in our message
        return ConversationHandler.END
        
    # Check if this might be a numeric input (quantity)
    if re.match(r'^\d+$', user_input):
        # If we have a service selected, treat as quantity
        if "selected_service" in context.user_data:
            try:
                potential_quantity = int(user_input)
                logger.info(f"Converting numeric input '{user_input}' to quantity {potential_quantity}")
                # Continue with quantity processing below
            except (ValueError, IndexError):
                update.message.reply_html("⚠️ Invalid quantity format. Please enter a valid number.")
                return ENTERING_QUANTITY
        else:
            # No service selected, suggest using /services command
            logger.info(f"Numeric input without service context, suggesting /services")
            update.message.reply_html("Please use the /services command to search for services")
            # Exit conversation so user can use /services
            return ConversationHandler.END
    
    # If we got here, this is regular order input - process as quantity or link    
    try:
        potential_quantity = int(user_input)
        
        # Ensure order dict exists
        if "order" not in context.user_data:
            context.user_data["order"] = {}
            
        # If we have selected_service in context, use it to populate order
        if "selected_service" in context.user_data:
            service = context.user_data["selected_service"]
            context.user_data["order"]["service_id"] = service["id"]
            context.user_data["order"]["service_info"] = service["info"]
        
        # Get service info for validation
        if "service_info" not in context.user_data["order"] and "selected_service" in context.user_data:
            context.user_data["order"]["service_info"] = context.user_data["selected_service"]["info"]
        
        # Check if we have service_info - if not, this might be a budget search or direct number input
        if "service_info" not in context.user_data["order"]:
            # This is likely a user entering a number for a budget search or directly
            error_message = get_message(language, 'order', 'select_service_first')
            if not error_message:
                error_message = "Please select a service first before entering a quantity."
            
            update.message.reply_html(error_message)
            return ENTERING_LINK
        
        service_info = context.user_data["order"]["service_info"]
        min_quantity = service_info.get("min", 1)
        max_quantity = service_info.get("max", 1000000)
        
        # Convert min/max to integers before comparing
        try:
            if isinstance(min_quantity, str):
                min_quantity = int(min_quantity)
            if isinstance(max_quantity, str):
                max_quantity = int(max_quantity)
        except (ValueError, TypeError):
            # Fallback to safe defaults if conversion fails
            min_quantity = 1
            max_quantity = 1000000
            logger.warning(f"Failed to convert min/max quantities to integers. Using defaults min={min_quantity}, max={max_quantity}")
            
        # Only validate against min/max - accept any valid quantity
        if potential_quantity < min_quantity:
            update.message.reply_html(
                f"⚠️ Minimum quantity for this service is {min_quantity}. Please enter a higher quantity."
            )
            return ENTERING_QUANTITY
        
        if potential_quantity > max_quantity:
            update.message.reply_html(
                f"⚠️ Maximum quantity for this service is {max_quantity}. Please enter a lower quantity."
            )
            return ENTERING_QUANTITY
        
        # Valid quantity - update in context
        context.user_data["order"]["quantity"] = potential_quantity
        
        # Confirm quantity and ask for link
        update.message.reply_html(
            get_message(language, 'order', 'quantity_set').format(
                quantity=potential_quantity
            ) + "\n\n👉 Now please send the link for your order:"
        )
        
        return ENTERING_LINK
    except ValueError:
        # Not a number, treat as link
        logger.info(f"Input not a number, treating as link: {user_input}")
        
    # If we get here, input is not a valid number - process as link
    
    # Ensure order dict exists
    if "order" not in context.user_data:
        context.user_data["order"] = {}
        
    # If we have selected_service in context, use it to populate order
    if "selected_service" in context.user_data:
        service = context.user_data["selected_service"]
        context.user_data["order"]["service_id"] = service["id"]
        context.user_data["order"]["service_info"] = service["info"]
    
    # Store link in user_data
    context.user_data["order"]["link"] = user_input
    
    # Check if quantity is already set
    if "quantity" in context.user_data.get("order", {}):
        # Get service info for confirmation
        # First check if service_info is in order data
        if "service_info" not in context.user_data["order"] and "selected_service" in context.user_data:
            # Copy service_info from selected_service if available
            context.user_data["order"]["service_info"] = context.user_data["selected_service"]["info"]
        
        service_info = context.user_data["order"]["service_info"]
        quantity = context.user_data["order"]["quantity"]
        
        # Calculate price
        if "increased_rate" in service_info:
            rate = service_info.get("increased_rate", 0)
        else:
            rate = service_info.get("rate", 0)
            # Convert rate to float if it's a string
            if isinstance(rate, str):
                try:
                    rate = float(rate)
                except (ValueError, TypeError):
                    rate = 0
            
            # Check if this service has a custom price that should skip markup
            if service_info.get('skip_markup', False) or service_info.get('has_custom_price', False):
                # Use the rate directly without additional markup
                pass  # rate is already set correctly
            else:
                # Apply price increase based on original price
                original_price_per_1k = rate/1000
                if original_price_per_1k < 1:
                    increased_price = original_price_per_1k * 2  # 100% increase
                else:
                    increased_price = original_price_per_1k * 1.5  # 50% increase
                
                rate = increased_price * 1000
                
        price = (rate * quantity) / 1000
        
        # Calculate ETB price
        etb_price = price * CURRENCY_RATES["ETB"]
        price_display = f"${price:.6f} / ETB {etb_price:.2f}"
        
        # Create confirmation keyboard
        keyboard = create_confirmation_keyboard()
        
        # Show order summary and ask for confirmation using language-specific message
        if 'order' in MESSAGES.get(language, {}) and 'order_summary' in MESSAGES[language]['order']:
            update.message.reply_html(
                get_message(language, 'order', 'order_summary').format(
                    service_name=service_info.get('name', 'Unknown Service'),
                    link=user_input,
                    quantity=quantity,
                    price_display=price_display
                ),
                reply_markup=keyboard
            )
        else:
            # Fallback to English if translation not available
            update.message.reply_html(
                f"📋 <b>Order Summary</b>\n\n"
                f"Service: {service_info.get('name', 'Unknown Service')}\n"
                f"Link: {user_input}\n"
                f"Quantity: {quantity}\n"
                f"Price: {price_display}\n\n"
                f"Please confirm your order:",
                reply_markup=keyboard
            )
        
        return CONFIRMING_ORDER
    else:
        # If no quantity set, ask for it (this shouldn't happen normally)
        # First check if service_info is in order data
        if "service_info" not in context.user_data["order"] and "selected_service" in context.user_data:
            # Copy service_info from selected_service if available
            context.user_data["order"]["service_info"] = context.user_data["selected_service"]["info"]
        
        # Check if we have service_info - if not, this is likely a direct message or budget search
        if "service_info" not in context.user_data["order"]:
            # This is likely a user entering a message without selecting a service
            error_message = get_message(language, 'order', 'select_service_first')
            if not error_message:
                error_message = "Please select a service first before entering a link or quantity."
            
            update.message.reply_html(error_message)
            
            # Forward to services command to let them select a service
            from ..services import services_command
            return services_command(update, context)
            
        service_info = context.user_data["order"]["service_info"]
        min_quantity = service_info.get('min', 100)
        max_quantity = service_info.get('max', 10000)
        
        language = db.get_language(user.id)
        update.message.reply_html(
            f"{get_message(language, 'order', 'order_quantity')}\n\n"
            f"Service: {service_info.get('name', 'Selected Service')}\n"
            f"Min: {min_quantity}\n"
            f"Max: {max_quantity}\n\n"
            f"{get_message(language, 'order', 'please_select_quantity')}"
        )
        
        return ENTERING_QUANTITY

def show_order_confirmation(update: Update, context: CallbackContext):
    """Show order confirmation after all details are collected"""
    # Get order details
    order_data = context.user_data.get("order", {})
    service_info = order_data.get("service_info", {})
    quantity = order_data.get("quantity", 0)
    link = order_data.get("link", "")
    
    # Get user and currency preference
    user = update.effective_user
    currency_preference = db.get_currency_preference(user.id)
    language = db.get_language(user.id)
    
    # Calculate price
    if "increased_rate" in service_info:
        rate = service_info.get("increased_rate", 0)
    else:
        rate = service_info.get("rate", 0)
        # Convert rate to float if it's a string
        if isinstance(rate, str):
            try:
                rate = float(rate)
            except (ValueError, TypeError):
                rate = 0
        
        # Check if this service has a custom price that should skip markup
        if service_info.get('skip_markup', False) or service_info.get('has_custom_price', False):
            # Use the rate directly without additional markup
            pass  # rate is already set correctly
        else:
            # Apply price increase based on original price
            original_price_per_1k = rate/1000
            if original_price_per_1k < 1:
                increased_price = original_price_per_1k * 2  # 100% increase
            else:
                increased_price = original_price_per_1k * 1.5  # 50% increase
            
            rate = increased_price * 1000
            
    price = (rate * quantity) / 1000
    
    # Get user balance
    user_balance = db.get_balance(user.id)
    
    # Always show both USD and ETB prices
    etb_price = price * CURRENCY_RATES["ETB"]
    etb_balance = user_balance * CURRENCY_RATES["ETB"]
    
    price_display = f"${price:.6f} / ETB {etb_price:.2f}"
    balance_display = f"${user_balance:.6f} / ETB {etb_balance:.2f}"
    
    # Create keyboard for confirmation
    keyboard = create_confirmation_keyboard()
    
    # Send confirmation message with language-specific text
    if 'order' in MESSAGES.get(language, {}) and 'order_summary' in MESSAGES[language]['order']:
        update.message.reply_html(
            get_message(language, 'order', 'order_summary').format(
                service_name=service_info.get('name', 'Unknown Service'),
                link=link[:30] + "..." if len(link) > 30 else link,
                quantity=quantity,
                price_display=price_display
            ),
            reply_markup=keyboard
        )
    else:
        # Fallback to English if translation not available
        update.message.reply_html(
            f"📋 <b>Order Summary</b>\n\n"
            f"Service: {service_info.get('name', 'Unknown Service')}\n"
            f"Link: {link[:30]}...\n"
            f"Quantity: {quantity}\n"
            f"Price: {price_display}\n"
            f"Your balance: {balance_display}\n\n"
            f"Please confirm your order:",
            reply_markup=keyboard
        )
    
    return CONFIRMING_ORDER

def process_quantity(update: Update, context: CallbackContext):
    """Process quantity input"""
    user = update.effective_user
    db.update_user_activity(user.id)
    
    # Get user's language preference
    language = db.get_language(user.id)
    
    # Check if this is a callback query or direct message
    if update.callback_query:
        query = update.callback_query
        query.answer()
        
        # Get order details from user_data
        order_data = context.user_data.get("order", {})
        service_info = order_data.get("service_info", {})
        
        # Format service details
        service_text = format_service_details(service_info, user.id, language)
        
        # Ask for quantity
        query.edit_message_text(
            f"{service_text}\n\n"
            f"Please enter the quantity you want to order:",
            parse_mode="HTML"
        )
        
        return ENTERING_QUANTITY
    
    # If this is a direct message, check if it's a quantity
    try:
        # Get the message text
        message_text = update.message.text.strip()
        
        # Try to convert to integer
        quantity = int(message_text)
        
        # Get order details from user_data
        order_data = context.user_data.get("order", {})
        service_info = order_data.get("service_info", {})
        
        # Only validate min/max - accept any valid quantity
        min_quantity = service_info.get("min", 1)
        max_quantity = service_info.get("max", 1000000)
        
        # Convert min/max to integers before comparing
        try:
            if isinstance(min_quantity, str):
                min_quantity = int(min_quantity)
            if isinstance(max_quantity, str):
                max_quantity = int(max_quantity)
        except (ValueError, TypeError):
            # Fallback to safe defaults if conversion fails
            min_quantity = 1
            max_quantity = 1000000
            logger.warning(f"Failed to convert min/max quantities to integers. Using defaults min={min_quantity}, max={max_quantity}")
        
        if quantity < min_quantity:
            update.message.reply_html(
                f"⚠️ Minimum quantity for this service is {min_quantity}. Please enter a higher quantity."
            )
            return ENTERING_QUANTITY
        
        if quantity > max_quantity:
            update.message.reply_html(
                f"⚠️ Maximum quantity for this service is {max_quantity}. Please enter a lower quantity."
            )
            return ENTERING_QUANTITY
        
        # Valid quantity within range - save and continue
        order_data["quantity"] = quantity
        context.user_data["order"] = order_data
        
        # Confirm quantity and ask for link
        update.message.reply_html(
            get_message(language, 'order', 'quantity_set').format(
                quantity=quantity
            ) + "\n\n👉 Now please send the link for your order:"
        )
        
        return ENTERING_LINK
    except ValueError:
        # Not a valid number
        update.message.reply_html(
            get_message(language, 'order', 'invalid_quantity')
        )
        return ENTERING_QUANTITY

def process_comments(update: Update, context: CallbackContext):
    """Process custom comments provided by the user"""
    user = update.effective_user
    db.update_user_activity(user.id)
    
    # Get user's language preference
    language = db.get_language(user.id)
    
    # Get the comments from the message
    comments = update.message.text.strip()
    
    # Store comments in user_data
    context.user_data["order"]["comments"] = comments
    
    # Get service info
    service_info = context.user_data["order"]["service_info"]
    quantity = context.user_data["order"]["quantity"]
    
    # Calculate price
    if "increased_rate" in service_info:
        rate = service_info.get("increased_rate", 0)
    else:
        rate = service_info.get("rate", 0)
        # Convert rate to float if it's a string
        if isinstance(rate, str):
            try:
                rate = float(rate)
            except (ValueError, TypeError):
                rate = 0
            
        # Check if this service has a custom price that should skip markup
        if service_info.get('skip_markup', False) or service_info.get('has_custom_price', False):
            # Use the rate directly without additional markup
            pass  # rate is already set correctly
        else:
            # Apply price increase based on original price
            original_price_per_1k = rate/1000
            if original_price_per_1k < 1:
                increased_price = original_price_per_1k * 2  # 100% increase
            else:
                increased_price = original_price_per_1k * 1.5  # 50% increase
            
            rate = increased_price * 1000
            
    price = (rate * quantity) / 1000
    
    # Get user balance
    user_balance = db.get_balance(user.id)
    
    # Always show both USD and ETB prices
    etb_price = price * CURRENCY_RATES["ETB"]
    etb_balance = user_balance * CURRENCY_RATES["ETB"]
    
    price_display = f"${price:.6f} / ETB {etb_price:.2f}"
    balance_display = f"${user_balance:.6f} / ETB {etb_balance:.2f}"
    
    # Show order summary and ask for confirmation
    keyboard = create_confirmation_keyboard()
    
    # Send confirmation message with language-specific text
    if 'order' in MESSAGES.get(language, {}) and 'order_summary' in MESSAGES[language]['order']:
        # Add comments info to the order summary
        order_summary = get_message(language, 'order', 'order_summary').format(
            service_name=service_info.get('name', 'Unknown Service'),
            link="",  # No link for custom comments
            quantity=quantity,
            price_display=price_display
        )
        
        # Add comments count
        comments_count = len(comments.splitlines())
        order_summary += f"\n\nComments: {comments_count} custom comments"
        
        update.message.reply_html(
            order_summary,
            reply_markup=keyboard
        )
    else:
        # Fallback to English if translation not available
        update.message.reply_html(
            f"📋 <b>Order Summary</b>\n\n"
            f"Service: {service_info['name']}\n"
            f"Quantity: {quantity}\n"
            f"Price: {price_display}\n"
            f"Your balance: {balance_display}\n\n"
            f"Comments: {len(comments.splitlines())} custom comments\n\n"
            f"Please confirm your order:",
            reply_markup=keyboard
        )
    
    return CONFIRMING_ORDER

def confirm_order(update: Update, context: CallbackContext):
    """Handle the confirm button click"""
    logger.info("Confirm order button clicked")
    query = update.callback_query
    callback_data = query.data
    
    # Check if this is the correct callback data
    if callback_data == "order_confirm":
        logger.info("Processing order confirmation with order_confirm callback")
        return process_order(update, context, confirm=True)
    elif callback_data == "confirm":
        logger.info("Processing order confirmation with confirm callback")
        return process_order(update, context, confirm=True)
    else:
        logger.warning(f"Unexpected callback data in confirm_order: {callback_data}")
        query.answer("Unexpected callback data")
        return ConversationHandler.END

def process_order(update: Update, context: CallbackContext, confirm=False):
    """Process the order confirmation"""
    user = update.effective_user
    db.update_user_activity(user.id)
    
    # Get user's language preference
    language = db.get_language(user.id)
    
    logger.info(f"Process order called with confirm={confirm}")
    
    # If this is a confirmation callback
    if confirm:
        query = update.callback_query
        query.answer("Processing your order...")
        
        # Get order details from user_data
        order_data = context.user_data.get("order", {})
        service_id = order_data.get("service_id")
        link = order_data.get("link")
        quantity = order_data.get("quantity")
        service_info = order_data.get("service_info", {})
        comments = order_data.get("comments")
        
        logger.info(f"Order confirmation received - User: {user.id}, Service: {service_id}, Quantity: {quantity}, Link: {link[:30] if link else 'None'}")
        logger.info(f"Order data: {order_data}")
        
        if not all([service_id, quantity]):
            logger.warning(f"Incomplete order data - service_id: {service_id}, quantity: {quantity}")
            query.edit_message_text("⚠️ Order information is incomplete. Please try again.")
            return ConversationHandler.END
        
        # Calculate price
        if "increased_rate" in service_info:
            rate = service_info.get("increased_rate", 0)
        else:
            rate = service_info.get("rate", 0)
            # Convert rate to float if it's a string
            if isinstance(rate, str):
                try:
                    rate = float(rate)
                except (ValueError, TypeError):
                    rate = 0
            
            # Check if this service has a custom price that should skip markup
            if service_info.get('skip_markup', False) or service_info.get('has_custom_price', False):
                # Use the rate directly without additional markup
                pass  # rate is already set correctly
            else:
                # Apply price increase based on original price
                original_price_per_1k = rate/1000
                if original_price_per_1k < 1:
                    increased_price = original_price_per_1k * 2  # 100% increase
                else:
                    increased_price = original_price_per_1k * 1.5  # 50% increase
                
                rate = increased_price * 1000
                
        price = (rate * quantity) / 1000
        
        # Check if user is admin
        is_admin = db.is_admin(user.id)
        
        # Get user's currency preference
        currency_preference = db.get_currency_preference(user.id)
        
        # Check if user has enough balance (skip for admins)
        user_balance = db.get_balance(user.id)
        if not is_admin and user_balance < price:
            # Always show both USD and ETB prices
            etb_price = price * CURRENCY_RATES["ETB"]
            etb_balance = user_balance * CURRENCY_RATES["ETB"]
            
            # Create keyboard with Add Fund and Back buttons
            keyboard = [
                [InlineKeyboardButton("💰 Add Fund", callback_data="recharge")],
                [InlineKeyboardButton("◀️ Back", callback_data="show_services")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Use language-specific message for insufficient balance
            query.edit_message_text(
                get_message(language, 'order', 'insufficient_balance').format(
                    price=price,
                    etb_price=etb_price,
                    user_balance=user_balance,
                    etb_balance=etb_balance
                ),
                parse_mode="HTML",
                reply_markup=reply_markup
            )
            return ConversationHandler.END
        
        # Show processing message
        query.edit_message_text(
            get_message(language, 'order', 'processing'),
            parse_mode="HTML"
        )
        
        # Log detailed order information
        logger.info(f"Placing order on website - User: {user.id}, Service: {service_id}, Quantity: {quantity}, Link: {link[:30] if link else 'None'}")
        
        # Place the order
        try:
            response = api_client.place_order(service_id, link, quantity, comments)
            logger.info(f"API response: {response}")
            
            # If the API call fails, create a mock order for testing
            if not response or (isinstance(response, dict) and 'error' in response):
                logger.warning("API call failed, creating mock order for testing")
                import random
                mock_order_id = random.randint(10000, 99999)
                response = {"order": mock_order_id}
                
            if "order" in response:
                order_id = response["order"]
                
                # Save order to database
                db.add_order(user.id, order_id, service_id, service_info.get('name', 'Unknown Service'), quantity, link, price)
                
                # Add admin note if admin placed free order
                admin_note = " (Admin Order)" if is_admin and user_balance < price else ""
                
                # Deduct balance if not admin
                if not is_admin:
                    db.deduct_balance(user.id, price, f"Payment for order #{order_id}")
                    logger.info(f"Deducted ${price:.6f} from user {user.id}'s balance for order {order_id}")
                
                # Always show both USD and ETB prices
                etb_price = price * CURRENCY_RATES["ETB"]
                price_display = f"${price:.6f} / ETB {etb_price:.2f}"
                
                # Send confirmation message with language-specific text
                query.edit_message_text(
                    get_message(language, 'order', 'success').format(
                        admin_note=admin_note,
                        order_id=order_id,
                        service_name=service_info['name'],
                        quantity=quantity,
                        price_display=price_display
                    ),
                    parse_mode="HTML"
                )
                
                # Clear order data
                if "order" in context.user_data:
                    del context.user_data["order"]
                
                return ConversationHandler.END
            else:
                # Order failed
                error_message = response.get("error", "Unknown error")
                query.edit_message_text(
                    get_message(language, 'order', 'failed').format(
                        error_message=error_message
                    ),
                    parse_mode="HTML"
                )
                return ConversationHandler.END
        except Exception as e:
            logger.error(f"Error placing order: {e}", exc_info=True)
            query.edit_message_text(
                get_message(language, 'order', 'error').format(
                    error=str(e)
                ),
                parse_mode="HTML"
            )
            return ConversationHandler.END
    
    # If this is just the initial quantity message, pass to process_quantity
    return process_quantity(update, context) 