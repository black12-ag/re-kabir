import os
import sys
import logging
import time
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Updater, CommandHandler, CallbackQueryHandler, MessageHandler, 
    Filters, ConversationHandler, CallbackContext
)

# Import handlers
from handlers.start import start_command, language_conv_handler, referrals_command, check_referrals_callback
from handlers.services import (
    services_command, service_callback, category_callback, platform_callback,
    SELECTING_PLATFORM, SELECTING_CATEGORY, SELECTING_SERVICE, SEARCHING_SERVICES,
    process_search_term
)
from handlers.order import (
    order_command, process_link, process_quantity, process_comments, process_order, confirm_order,
    ENTERING_LINK, ENTERING_QUANTITY, ENTERING_COMMENTS, CONFIRMING_ORDER
)
from handlers.balance import balance_command, refresh_balance_callback
from handlers.admin import (
    admin_command, admin_menu_callback, broadcast_message, broadcast_confirm,
    handle_user_id_input, handle_balance_amount, confirm_add_balance, cancel_command,
    handle_remove_balance_options, confirm_remove_balance, 
    ADMIN_MENU, BROADCASTING, VIEWING_STATS, ADDING_BALANCE, REMOVING_BALANCE, ENTERING_USER_ID, 
    ENTERING_BALANCE_AMOUNT, ENTERING_REFERRAL_SETTINGS, REMOVING_BALANCE_OPTIONS,
    admin_conv_handler, handle_referral_settings_input, set_welcome_command, set_welcome_media_command,
    set_referral_bonus_amount_command
)
from handlers.help import help_command, admin_help_command
from handlers.status import status_command, refresh_status_callback
from handlers.account import account_command, refresh_account_callback
from handlers.recharge import recharge_conv_handler, recharge_command
from handlers.support import support_command, support_conv_handler, admin_reply_conv_handler
from handlers.command_menu import get_command_menu_handlers, show_command_menu, hide_command_menu, toggle_command_menu
from utils.messages import get_message
from utils.db import db
from utils.constants import CURRENCY_RATES
import handlers.tutorial as tutorial_handlers
from handlers.refunds import setup_refund_checker  # Add this import

# Load environment variables
load_dotenv()

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Define states for status conversation
STATUS_WAITING_FOR_ID = 0

def debug_callback(update, context):
    """Fallback handler for debugging"""
    query = update.callback_query
    
    if query:
        callback_data = query.data
        logger.debug(f"Received callback: {callback_data}")
        
        # Handle tutorial callbacks that may have escaped the conversation handler
        if (callback_data.startswith("tutorial_edit_") or 
            callback_data.startswith("tutorial_media_") or
            callback_data.startswith("tutorial_admin_edit_") or
            callback_data.startswith("tutorial_add_media_") or
            callback_data.startswith("tutorial_delete_media_") or
            callback_data.startswith("tutorial_delete_media_item_") or
            callback_data.startswith("tutorial_publish_media_")):
            
            logger.info(f"Handling tutorial callback in fallback handler: {callback_data}")
            try:
                # Handle different types of tutorial callbacks
                
                if callback_data.startswith("tutorial_edit_"):
                    return tutorial_handlers.admin_edit_text(update, context)
                
                elif callback_data.startswith("tutorial_media_photo_") or \
                     callback_data.startswith("tutorial_media_video_") or \
                     callback_data.startswith("tutorial_media_document_") or \
                     callback_data.startswith("tutorial_media_voice_"):
                    return tutorial_handlers.admin_select_media_type(update, context)
                
                elif callback_data.startswith("tutorial_media_"):
                    return tutorial_handlers.admin_select_media_type(update, context)
                
                elif callback_data.startswith("tutorial_admin_edit_"):
                    return tutorial_handlers.admin_edit_tutorial(update, context)
                
                elif callback_data.startswith("tutorial_add_media_"):
                    return tutorial_handlers.admin_add_media(update, context)
                
                elif callback_data.startswith("tutorial_delete_media_item_"):
                    return tutorial_handlers.admin_delete_media_item(update, context)
                
                elif callback_data.startswith("tutorial_delete_media_"):
                    return tutorial_handlers.admin_delete_media(update, context)
                
                elif callback_data.startswith("tutorial_publish_media_"):
                    return tutorial_handlers.admin_publish_media(update, context)
                
            except Exception as e:
                logger.error(f"Error handling tutorial callback in fallback: {e}", exc_info=True)
                query.answer("Error processing tutorial action")
                return
        
        # Handle category callbacks that may have escaped the conversation handler
        if callback_data.startswith("cat_") or callback_data.startswith("category_"):
            logger.info(f"Handling category callback in fallback handler: {callback_data}")
            try:
                # Import required functions
                from handlers.services import category_callback, _get_services, SELECTING_SERVICE
                
                # Call the proper handler
                return category_callback(update, context)
            except Exception as e:
                logger.error(f"Error handling category in fallback: {e}", exc_info=True)
                query.answer("Error processing category")
                query.edit_message_text("There was an error processing your category selection. Please try again.")
                return
        
        # Handle platform callbacks that may have escaped
        if callback_data.startswith("plt_") or callback_data.startswith("platform_") or callback_data == "back_to_platforms":
            logger.info(f"Handling platform callback in fallback handler: {callback_data}")
            try:
                # Import required functions
                from handlers.services import platform_callback, services_command
                
                if callback_data == "back_to_platforms":
                    return services_command(update, context)
                else:
                    # Call the proper handler
                    return platform_callback(update, context)
            except Exception as e:
                logger.error(f"Error handling platform in fallback: {e}", exc_info=True)
                query.answer("Error processing platform")
                query.edit_message_text("There was an error processing your platform selection. Please try again.")
                return
        
        # Handle back to categories callback
        if callback_data == "back_to_categories":
            logger.info(f"Handling back to categories callback in fallback handler: {callback_data}")
            try:
                # Import required functions
                from handlers.services import platform_callback
                
                # Get the current platform from user data
                current_platform = context.user_data.get("current_platform", None)
                if current_platform:
                    # Create a synthetic callback with the platform ID
                    query.data = f"platform_{current_platform}"
                    return platform_callback(update, context)
                else:
                    # If no platform is stored, go back to services menu
                    from handlers.services import services_command
                    return services_command(update, context)
            except Exception as e:
                logger.error(f"Error handling back to categories: {e}", exc_info=True)
                query.answer("Error returning to categories")
                query.edit_message_text("There was an error returning to categories. Please try again.")
                return
        
        # Handle page navigation callbacks
        if callback_data.startswith("page_"):
            logger.info(f"Handling page navigation in fallback handler: {callback_data}")
            try:
                # Import required functions
                from handlers.services import service_callback
                
                # Call the service callback handler
                return service_callback(update, context)
            except Exception as e:
                logger.error(f"Error handling page navigation: {e}", exc_info=True)
                query.answer("Error navigating pages")
                query.edit_message_text("There was an error navigating between pages. Please try again.")
                return
        
        # Handle search-related callbacks
        if callback_data in ["search_services", "view_search_results"]:
            logger.info(f"Handling search callback in fallback handler: {callback_data}")
            try:
                # Import required functions
                from handlers.services import service_callback
                
                # Call the service callback handler
                return service_callback(update, context)
            except Exception as e:
                logger.error(f"Error handling search callback: {e}", exc_info=True)
                query.answer("Error with search")
                query.edit_message_text("There was an error with the search function. Please try again.")
                return
        
        # Handle confirm order button
        if callback_data == "confirm_order":
            try:
                # Get order data
                if "order" not in context.user_data:
                    query.answer("Order data not found")
                    query.edit_message_text("Error: Order data not found. Please try again.")
                    return
                
                order_data = context.user_data["order"]
                
                # Check if service_info is in order_data, if not, try to get it from selected_service
                if "service_info" not in order_data and "selected_service" in context.user_data:
                    order_data["service_info"] = context.user_data["selected_service"]["info"]
                    
                service_info = order_data.get("service_info", context.user_data.get("selected_service", {}).get("info", {}))
                service_id = order_data.get("service_id", context.user_data.get("selected_service", {}).get("id", "unknown"))
                quantity = order_data.get("quantity", 0)
                link = order_data.get("link", "No link provided")
                
                # Calculate cost - Handle string rate properly
                rate = service_info.get("rate", 0)
                try:
                    if isinstance(rate, str):
                        rate = float(rate)
                    cost = (rate / 1000) * quantity
                except (ValueError, TypeError):
                    cost = 0
                
                # Get service name for display
                service_name = service_info.get("name", "Unknown Service")
                
                # Show processing message
                query.edit_message_text(
                    f"⏳ <b>Processing Order...</b>\n\n"
                    f"Submitting order to service provider...",
                    parse_mode="HTML"
                )
                
                # Place order with API
                from utils.api_client import api_client
                
                # Log detailed order information for debugging
                logger.info(f"Placing order with API - Service ID: {service_id}, Quantity: {quantity}, Link: {link}")
                
                # Make the real API call to place the order
                response = api_client.place_order(service_id, link, quantity)
                logger.info(f"API order response: {response}")
                
                if response and isinstance(response, dict) and ('order' in response or 'id' in response):
                    # Get order ID from response
                    order_id = response.get('order', response.get('id', 'Unknown'))
                    
                    # Store order in user data for reference
                    if "orders" not in context.user_data:
                        context.user_data["orders"] = []
                        
                    context.user_data["orders"].append({
                        "order_id": order_id,
                        "service_id": service_id,
                        "service_name": service_name,
                        "link": link,
                        "quantity": quantity,
                        "cost": cost,
                        "timestamp": int(time.time())
                    })
                    
                    # Display success message
                    query.edit_message_text(
                        f"✅ <b>Order Successfully Placed!</b>\n\n"
                        f"<b>Order ID:</b> <code>{order_id}</code>\n"
                        f"<b>Service:</b> {service_name}\n"
                        f"<b>Link/Username:</b> {link}\n"
                        f"<b>Quantity:</b> {quantity}\n"
                        f"<b>Total Cost:</b> ${cost:.2f}\n\n"
                        f"You can check the status of your order with /status command.",
                        parse_mode="HTML"
                    )
                    
                    # Clear order state
                    context.user_data.pop("order_state", None)
                    return
                else:
                    error_msg = response.get("error", "Unknown error") if response else "Failed to connect to service"
                    query.edit_message_text(
                        f"❌ <b>Order Failed</b>\n\n"
                        f"There was an error placing your order: {error_msg}\n\n"
                        f"Please try again later or contact support.",
                        parse_mode="HTML"
                    )
                    
                    # Clear order state
                    context.user_data.pop("order_state", None)
                    return
            except Exception as e:
                logger.error(f"Error confirming order: {e}", exc_info=True)
                query.answer("Error confirming order")
                query.edit_message_text(f"Error confirming order: {str(e)}", parse_mode="HTML")
                return
        
        # Handle cancel order button
        if callback_data == "cancel_order":
            query.answer("Order canceled")
            query.edit_message_text("Order has been canceled.")
            # Clear order state
            context.user_data.pop("order_state", None)
            return
        
        # Handle service selection callbacks
        if callback_data.startswith("service_") or callback_data.startswith("quick_"):
            try:
                # Get service ID
                service_id = callback_data.split("_")[1]
                logger.info(f"Processing service ID: {service_id}")
                
                # Get services
                from handlers.services import _get_services
                services = _get_services()
                
                # Find service by ID
                service_info = None
                for service in services:
                    if str(service.get("service")) == service_id:
                        service_info = service
                        break
                
                if service_info:
                    # Store service info in user_data properly for both flows
                    context.user_data["selected_service"] = {
                        "id": service_id,
                        "info": service_info
                    }
                    # Also store in order for compatibility with order flow
                    if "order" not in context.user_data:
                        context.user_data["order"] = {}
                    context.user_data["order"]["service_id"] = service_id
                    context.user_data["order"]["service_info"] = service_info
                    
                    # Format service details for min/max display
                    service_name = service_info.get('name', 'Unknown Service')
                    min_quantity_display = service_info.get('min', 100)
                    max_quantity_display = service_info.get('max', 10000)
                    
                    # Convert min/max to integers for button generation
                    min_qty = min_quantity_display
                    max_qty = max_quantity_display
                    if isinstance(min_qty, str):
                        min_qty = int(min_qty)
                    if isinstance(max_qty, str):
                        max_qty = int(max_qty)

                    # Generate quantity options (starting from min, doubling until reaching max)
                    quantity_options = []
                    current_qty = min_qty
                    while current_qty <= max_qty:
                        quantity_options.append(current_qty)
                        current_qty *= 2
                        if len(quantity_options) >= 8:  # Limit to 8 buttons to avoid too many
                            break

                    # Add the max as the last option if it's not already included
                    if quantity_options[-1] < max_qty and len(quantity_options) < 8:
                        quantity_options.append(max_qty)

                    # Create quantity selection buttons
                    buttons = []
                    for i in range(0, len(quantity_options), 2):  # Create rows with 2 buttons each
                        row = []
                        # Calculate price for this quantity
                        qty1 = quantity_options[i]
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
                                
                        price1 = (rate * qty1) / 1000
                        etb_price1 = price1 * CURRENCY_RATES["ETB"]
                        
                        # Format USD price with 4 decimal places for small amounts
                        if price1 < 1:
                            price_format1 = f"${price1:.4f}"
                        else:
                            price_format1 = f"${price1:.2f}"
                        
                        # Add first button with price - ETB first, then USD in parentheses
                        row.append(InlineKeyboardButton(f"{qty1} (ETB {etb_price1:.0f}/{price_format1})", callback_data=f"qty_{qty1}"))
                        
                        # Add second button if available
                        if i + 1 < len(quantity_options):
                            qty2 = quantity_options[i+1]
                            price2 = (rate * qty2) / 1000
                            etb_price2 = price2 * CURRENCY_RATES["ETB"]
                            
                            # Format USD price with 4 decimal places for small amounts
                            if price2 < 1:
                                price_format2 = f"${price2:.4f}"
                            else:
                                price_format2 = f"${price2:.2f}"
                            
                            row.append(InlineKeyboardButton(f"{qty2} (ETB {etb_price2:.0f}/{price_format2})", callback_data=f"qty_{qty2}"))
                        
                        buttons.append(row)
                    
                    # Add a "Custom" button for custom quantity input
                    buttons.append([InlineKeyboardButton("Custom Amount", callback_data="qty_custom")])

                    quantity_keyboard = InlineKeyboardMarkup(buttons)

                    # Get user language
                    user_id = query.from_user.id
                    language = db.get_language(user_id)

                    # SKIP PROCESSING MESSAGE AND ASK FOR QUANTITY DIRECTLY WITH BUTTONS
                    query.edit_message_text(
                        f"{get_message(language, 'order', 'order_quantity')}\n\n"
                        f"<b>Service:</b> {service_name}\n"
                        f"<b>Min:</b> {min_quantity_display}\n"
                        f"<b>Max:</b> {max_quantity_display}\n\n"
                        f"{get_message(language, 'order', 'please_select_quantity')}",
                        parse_mode="HTML",
                        reply_markup=quantity_keyboard
                    )
                    
                    # No need to set state for text-based quantity collection
                    # State will be handled by quantity button callback
                    return
                else:
                    query.answer("Service not found!")
                    query.edit_message_text(f"⚠️ Service with ID {service_id} not found.")
                    return
            except Exception as e:
                logger.error(f"Error in debug_callback processing service: {e}")
                query.answer("Error processing service")
                query.edit_message_text(f"Error: {str(e)}")
                return
        
        # Handle quantity buttons
        if callback_data.startswith("qty_"):
            try:
                # Check if this is the custom quantity option
                if callback_data == "qty_custom":
                    # Get service info
                    service_info = context.user_data.get("selected_service", {}).get("info", {})
                    service_name = service_info.get("name", "Unknown Service")
                    min_qty = service_info.get("min", 1)
                    max_qty = service_info.get("max", 1000000)
                    
                    # Get user language
                    user_id = query.from_user.id
                    language = db.get_language(user_id)
                    
                    # Prompt user to enter a custom quantity
                    query.edit_message_text(
                        f"{get_message(language, 'order', 'order_quantity')}\n\n"
                        f"<b>Service:</b> {service_name}\n"
                        f"<b>Min:</b> {min_qty}\n"
                        f"<b>Max:</b> {max_qty}\n\n"
                        f"Please enter your desired quantity:",
                        parse_mode="HTML"
                    )
                    
                    # Update state to wait for custom quantity
                    context.user_data["order_state"] = "waiting_for_custom_quantity"
                    return
                
                # Extract quantity from callback data
                quantity = int(callback_data.split("_")[1])
                logger.info(f"Selected quantity: {quantity}")
                
                # Get service info
                service_info = context.user_data.get("selected_service", {}).get("info", {})
                service_name = service_info.get("name", "Unknown Service")
                
                # Save the quantity to order context
                if "order" not in context.user_data:
                    context.user_data["order"] = {}
                context.user_data["order"]["quantity"] = quantity
                
                # Store service info properly for compatibility with order handlers
                context.user_data["order"]["service_info"] = service_info
                
                # Get user language
                user_id = query.from_user.id
                language = db.get_language(user_id)
                
                # Show confirmation and ask for link/username
                query.edit_message_text(
                    get_message(language, 'order', 'quantity_set').format(quantity=quantity) + 
                    "\n\n👉 Now please send the link for your order:",
                    parse_mode="HTML"
                )
                
                # Update state to wait for link
                context.user_data["order_state"] = "waiting_for_link"
                return
            except Exception as e:
                logger.error(f"Error processing quantity selection: {e}")
                query.answer("Error processing quantity")
                query.edit_message_text("There was an error processing your quantity selection. Please try again.")
                return
        
        # Handle confirm button if not caught by conversation handler
        if callback_data == "confirm" or callback_data == "order_confirm":
            logger.info(f"Handling order confirmation in debug_callback: {callback_data}")
            try:
                from handlers.order import confirm_order
                return confirm_order(update, context)
            except Exception as e:
                logger.error(f"Error handling order confirmation: {e}", exc_info=True)
                query.answer("Error processing order")
                query.edit_message_text(
                    f"❌ <b>Order Failed</b>\n\n"
                    f"An unexpected error occurred: {str(e)}\n\n"
                    f"Please try again later or contact support.",
                    parse_mode="HTML"
                )
                return
        
        # Handle tutorial admin callbacks
        if callback_data.startswith("tutorial_admin_edit_"):
            logger.info(f"Handling tutorial admin edit callback in fallback handler: {callback_data}")
            try:
                # Import required function
                from handlers.tutorial import admin_edit_tutorial
                return admin_edit_tutorial(update, context)
            except Exception as e:
                logger.error(f"Error handling tutorial admin edit: {e}", exc_info=True)
                query.answer("Error processing tutorial admin action")
                return
        
        # Default handler for other callbacks - Try looking up the handler
        logger.warning(f"Unhandled callback data: {callback_data}")
        query.answer(f"Unhandled action: {callback_data}")
        return
    
    # For text messages - IMPORTANT FOR NEW FLOW
    if update.message:
        message_text = update.message.text
        logger.debug(f"Received message: {message_text}")
        
        # Handle order states for text messages
        order_state = context.user_data.get("order_state", None)
        
        # CHANGED ORDER: Handle quantity input FIRST
        if order_state == "waiting_for_quantity":
            try:
                # Parse quantity
                quantity = int(message_text.strip())
                
                # Get service info
                service_info = context.user_data.get("selected_service", {}).get("info", {})
                service_name = service_info.get("name", "Unknown Service")
                
                # Only validate min/max - accept any valid quantity
                min_qty = service_info.get("min", 1) 
                max_qty = service_info.get("max", 1000000)
                
                # Convert min/max to integers before comparing
                try:
                    if isinstance(min_qty, str):
                        min_qty = int(min_qty)
                    if isinstance(max_qty, str):
                        max_qty = int(max_qty)
                except (ValueError, TypeError):
                    # Fallback to safe defaults if conversion fails
                    min_qty = 1
                    max_qty = 1000000
                    logger.warning(f"Failed to convert min/max quantities to integers. Using defaults min={min_qty}, max={max_qty}")
                
                if quantity < min_qty:
                    update.message.reply_html(
                        f"⚠️ Minimum quantity for this service is {min_qty}. Please enter a higher quantity."
                    )
                    return
                
                if quantity > max_qty:
                    update.message.reply_html(
                        f"⚠️ Maximum quantity for this service is {max_qty}. Please enter a lower quantity."
                    )
                    return
                
                # Valid quantity within range - save and continue
                if "order" not in context.user_data:
                    context.user_data["order"] = {}
                context.user_data["order"]["quantity"] = quantity
                
                # Store service info properly for compatibility with order handlers
                context.user_data["order"]["service_info"] = service_info
                
                # Get user language
                user_id = update.message.from_user.id
                language = db.get_language(user_id)
                
                # Show confirmation of quantity AND explicitly ask for link
                update.message.reply_html(
                    f"{get_message(language, 'order', 'quantity_set').format(quantity=quantity)}\n\n"
                    f"👉 Now please send the link for your order:"
                )
                
                # Update state to wait for link
                context.user_data["order_state"] = "waiting_for_link"
                return
            except ValueError:
                # Handle invalid quantity input
                update.message.reply_html(
                    "⚠️ Please enter a valid number for quantity."
                )
                return
        
        # Handle custom quantity input
        elif order_state == "waiting_for_custom_quantity":
            try:
                # Parse quantity
                quantity = int(message_text.strip())
                
                # Get service info
                service_info = context.user_data.get("selected_service", {}).get("info", {})
                service_name = service_info.get("name", "Unknown Service")
                
                # Only validate min/max - accept any valid quantity
                min_qty = service_info.get("min", 1)
                max_qty = service_info.get("max", 1000000)
                
                # Convert min/max to integers before comparing
                try:
                    if isinstance(min_qty, str):
                        min_qty = int(min_qty)
                    if isinstance(max_qty, str):
                        max_qty = int(max_qty)
                except (ValueError, TypeError):
                    # Fallback to safe defaults if conversion fails
                    min_qty = 1
                    max_qty = 1000000
                    logger.warning(f"Failed to convert min/max quantities to integers. Using defaults min={min_qty}, max={max_qty}")
                
                if quantity < min_qty:
                    update.message.reply_html(
                        f"⚠️ Minimum quantity for this service is {min_qty}. Please enter a higher quantity."
                    )
                    return
                
                if quantity > max_qty:
                    update.message.reply_html(
                        f"⚠️ Maximum quantity for this service is {max_qty}. Please enter a lower quantity."
                    )
                    return
                
                # Valid quantity within range - save and continue
                if "order" not in context.user_data:
                    context.user_data["order"] = {}
                context.user_data["order"]["quantity"] = quantity
                
                # Store service info properly for compatibility with order handlers
                context.user_data["order"]["service_info"] = service_info
                
                # Get user language
                user_id = update.message.from_user.id
                language = db.get_language(user_id)
                
                # Show confirmation of quantity AND explicitly ask for link
                update.message.reply_html(
                    f"{get_message(language, 'order', 'quantity_set').format(quantity=quantity)}\n\n"
                    f"👉 Now please send the link for your order:"
                )
                
                # Update state to wait for link
                context.user_data["order_state"] = "waiting_for_link"
                return
            except ValueError:
                # Handle invalid quantity input
                update.message.reply_html(
                    "⚠️ Please enter a valid number for quantity."
                )
                return
        
        # FLOW STEP 3: Handle link input
        elif order_state == "waiting_for_link":
            # Get user input
            user_input = message_text.strip()
            
            # ENHANCED: Always check first if input is a numeric value
            try:
                potential_quantity = int(user_input)
                # Numeric input detected - always treat as quantity if within min/max range
                
                # Get service info
                service_info = context.user_data.get("selected_service", {}).get("info", {})
                min_qty = service_info.get("min", 1)
                max_qty = service_info.get("max", 1000000)
                
                # Convert min/max to integers before comparing
                try:
                    if isinstance(min_qty, str):
                        min_qty = int(min_qty)
                    if isinstance(max_qty, str):
                        max_qty = int(max_qty)
                except (ValueError, TypeError):
                    # Fallback to safe defaults if conversion fails
                    min_qty = 1
                    max_qty = 1000000
                    logger.warning(f"Failed to convert min/max quantities to integers. Using defaults min={min_qty}, max={max_qty}")
                
                # Only validate against min/max and accept any quantity within range
                if potential_quantity < min_qty:
                    update.message.reply_html(
                        f"⚠️ Minimum quantity for this service is {min_qty}. Please enter a higher quantity."
                    )
                    return
                
                if potential_quantity > max_qty:
                    update.message.reply_html(
                        f"⚠️ Maximum quantity for this service is {max_qty}. Please enter a lower quantity."
                    )
                    return
                
                # Valid quantity within range - save and continue
                if "order" not in context.user_data:
                    context.user_data["order"] = {}
                context.user_data["order"]["quantity"] = potential_quantity
                
                # Get user language
                user_id = update.message.from_user.id
                language = db.get_language(user_id)
                
                # Show confirmation of quantity and ask for link explicitly
                update.message.reply_html(
                    f"{get_message(language, 'order', 'quantity_set').format(quantity=potential_quantity)}\n\n"
                    f"👉 Now please send the link for your order:"
                )
                return
            except ValueError:
                # Not a number, continue with link processing
                logger.info(f"Input not a number, treating as link: {user_input}")
            
            # If we get here, the input is not a number - process as link
            # Save the input in the link field
            if "order" not in context.user_data:
                context.user_data["order"] = {}
            context.user_data["order"]["link"] = user_input
            
            # Get service info for confirmation
            service_info = context.user_data.get("selected_service", {}).get("info", {})
            service_name = service_info.get("name", "Unknown Service")
            
            # Make sure service_info is also in the order data
            if service_info:
                context.user_data["order"]["service_info"] = service_info
            
            quantity = context.user_data["order"].get("quantity", 0)
            
            # Calculate cost
            rate = service_info.get("rate", 0)
            try:
                if isinstance(rate, str):
                    rate = float(rate)
                cost = (rate / 1000) * quantity
            except (ValueError, TypeError):
                cost = 0
            
            # Create confirm order button
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ Confirm Order", callback_data="confirm_order")],
                [InlineKeyboardButton("❌ Cancel", callback_data="cancel_order")]
            ])
            
            # Show order summary and ask for confirmation
            update.message.reply_html(
                f"<b>Order Summary:</b>\n\n"
                f"<b>Service:</b> {service_name}\n"
                f"<b>Link/Username:</b> {user_input}\n"
                f"<b>Quantity:</b> {quantity}\n"
                f"<b>Total Cost:</b> ${cost:.2f}\n\n"
                f"<b>Confirm your order?</b>",
                reply_markup=keyboard
            )
            
            # Update state
            context.user_data["order_state"] = "confirming_order"
            return
        
        # Default handler for other messages
        update.message.reply_text(f"Received: {message_text}")
    else:
        logger.warning("Received update without message or callback query")

def handle_order_id(update: Update, context: CallbackContext):
    """Handle order ID input"""
    user = update.effective_user
    order_id = update.message.text.strip()
    
    # Import check_specific_order function and api_client
    from handlers.status import check_specific_order
    from utils.api_client import api_client
    from utils.db import db
    
    # Try to get order status from API first
    try:
        response = api_client.get_order_status(order_id)
        
        if response and not isinstance(response, list) and not response.get("error"):
            # If order exists, check the order status
            success = check_specific_order(update, context, order_id)
            if success:
                return ConversationHandler.END
        
        # If order doesn't exist or there was an error
        error_message = response.get("error", "Order not found or not accessible") if response else "Could not connect to service provider"
        
        # Get user's orders from database
        orders = db.get_user_orders(user.id, limit=20)
        
        # Create a list of order IDs if there are any orders
        order_ids_text = ""
        if orders:
            order_ids_text = "\n\n<b>Your recent order IDs:</b>\n"
            for order in orders:
                service_name = order.get('service_name', 'Unknown Service')
                # Truncate service name if too long
                if len(service_name) > 25:
                    service_name = service_name[:22] + "..."
                order_ids_text += f"<code>{order['id']}</code> - {service_name}\n"
        
        # Create keyboard with options
        keyboard = [
            [InlineKeyboardButton("📋 Show My Order IDs", callback_data="show_order_ids")],
            [InlineKeyboardButton("◀️ Back to Main Menu", callback_data="back_to_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Send error message with order IDs
        update.message.reply_html(
            f"⚠️ {error_message}\n\n"
            f"Please enter a valid order ID or click a button below:{order_ids_text}",
            reply_markup=reply_markup
        )
        return STATUS_WAITING_FOR_ID
    except Exception as e:
        logger.error(f"Error handling order ID: {e}")
        
        # Create keyboard with options
        keyboard = [
            [InlineKeyboardButton("📋 Show My Order IDs", callback_data="show_order_ids")],
            [InlineKeyboardButton("◀️ Back to Main Menu", callback_data="back_to_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Send error message
        update.message.reply_html(
            f"⚠️ An error occurred: {str(e)}\n\n"
            f"Please try again later or click a button below:",
            reply_markup=reply_markup
        )
        return STATUS_WAITING_FOR_ID

def do_nothing_callback(update: Update, context: CallbackContext):
    """Handler for do_nothing callback - just answers the callback query"""
    query = update.callback_query
    query.answer()
    return

def my_orders_command(update: Update, context: CallbackContext):
    """Handler for /my_orders command"""
    # Redirect to status command which shows orders
    return status_command(update, context)

def check_order_command(update: Update, context: CallbackContext):
    """Handler for /check_order command"""
    # Redirect to status command which allows checking specific orders
    return status_command(update, context)

def upload_receipt_command(update: Update, context: CallbackContext):
    """Handler for /upload_receipt command"""
    # Redirect to recharge command which handles receipts
    return recharge_command(update, context)

def more_command(update: Update, context: CallbackContext):
    """Handler for /more command"""
    user = update.effective_user
    language = db.get_language(user.id)
    
    # Create keyboard with additional options
    keyboard = [
        [
            InlineKeyboardButton("📚 Tutorials", callback_data="tutorial"),
            InlineKeyboardButton("❓ Help", callback_data="help")
        ],
        [
            InlineKeyboardButton("💬 Support", callback_data="support"),
            InlineKeyboardButton("👤 Account", callback_data="show_account")
        ],
        [InlineKeyboardButton("◀️ Back to Main Menu", callback_data="back_to_main")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Send message with more options
    if update.message:
        update.message.reply_html(
            "<b>More Options</b>\n\nSelect an option from the menu below:",
            reply_markup=reply_markup
        )
    else:
        query = update.callback_query
        query.answer()
        query.edit_message_text(
            "<b>More Options</b>\n\nSelect an option from the menu below:",
            reply_markup=reply_markup,
            parse_mode="HTML"
        )
    
    return ConversationHandler.END

def customer_service_command(update: Update, context: CallbackContext):
    """Handler for /customer_service command"""
    # Redirect to support command
    return support_command(update, context)

def main():
    """Start the bot"""
    # Get the token from environment variables
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN not set in environment variables")
        return
    
    logger.info(f"Starting bot with token: {token[:5]}...")
    
    # Create the Updater and pass it the bot's token
    updater = Updater(token=token, use_context=True)
    
    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher
    
    # Add command handlers
    dispatcher.add_handler(CommandHandler("start", start_command))
    
    # Add language selection handler
    dispatcher.add_handler(language_conv_handler)
    
    # Add other command handlers
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("adminhelp", admin_help_command))
    dispatcher.add_handler(CommandHandler("balance", balance_command))
    dispatcher.add_handler(CommandHandler("account", account_command))
    dispatcher.add_handler(CommandHandler("support", support_command))
    
    # Add new menu command handlers
    dispatcher.add_handler(CommandHandler("my_orders", my_orders_command))
    dispatcher.add_handler(CommandHandler("check_order", check_order_command))
    dispatcher.add_handler(CommandHandler("upload_receipt", upload_receipt_command))
    dispatcher.add_handler(CommandHandler("more", more_command))
    dispatcher.add_handler(CommandHandler("customer_service", customer_service_command))
    
    # Add command menu handlers
    for handler in get_command_menu_handlers():
        dispatcher.add_handler(handler)
    
    # Add status conversation handler
    status_conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("status", status_command),
            CallbackQueryHandler(status_command, pattern=r"^check_status$"),
            CallbackQueryHandler(status_command, pattern=r"^show_order_ids$")
        ],
        states={
            STATUS_WAITING_FOR_ID: [
                MessageHandler(Filters.text & ~Filters.command, handle_order_id),
                CallbackQueryHandler(status_command, pattern=r"^show_order_ids$"),
                CallbackQueryHandler(status_command, pattern=r"^check_status$"),
                CallbackQueryHandler(start_command, pattern=r"^back_to_main$")
            ]
        },
        fallbacks=[
            CommandHandler("start", start_command),
            CallbackQueryHandler(start_command, pattern=r"^cancel$"),
            CallbackQueryHandler(start_command, pattern=r"^back_to_main$")
        ],
        allow_reentry=True
    )
    dispatcher.add_handler(status_conv_handler)
    
    # Add refresh status callback handler
    dispatcher.add_handler(CallbackQueryHandler(refresh_status_callback, pattern=r"^refresh_status"))
    
    # Add admin conversation handler
    dispatcher.add_handler(admin_conv_handler)
    dispatcher.add_handler(CommandHandler("setwelcome", set_welcome_command))
    dispatcher.add_handler(CommandHandler("setwelcomem", set_welcome_media_command))
    dispatcher.add_handler(CommandHandler("setreferralbonus", set_referral_bonus_amount_command))
    dispatcher.add_handler(CallbackQueryHandler(broadcast_confirm, pattern=r"^broadcast_confirm$"))
    dispatcher.add_handler(CallbackQueryHandler(broadcast_confirm, pattern=r"^broadcast_cancel$"))
    
    # Add balance management handlers
    dispatcher.add_handler(CallbackQueryHandler(confirm_add_balance, pattern=r"^confirm_add_balance$"))
    dispatcher.add_handler(CallbackQueryHandler(confirm_remove_balance, pattern=r"^confirm_remove_"))
    dispatcher.add_handler(CallbackQueryHandler(admin_menu_callback, pattern=r"^cancel_add_balance$"))
    dispatcher.add_handler(CallbackQueryHandler(admin_menu_callback, pattern=r"^cancel_remove_balance$"))
    
    # Add admin stats detail view handlers
    dispatcher.add_handler(CallbackQueryHandler(admin_menu_callback, pattern=r"^admin_view_all_users$"))
    dispatcher.add_handler(CallbackQueryHandler(admin_menu_callback, pattern=r"^admin_view_active_users$"))
    dispatcher.add_handler(CallbackQueryHandler(admin_menu_callback, pattern=r"^admin_view_all_orders$"))
    dispatcher.add_handler(CallbackQueryHandler(admin_menu_callback, pattern=r"^admin_view_recent_orders$"))
    dispatcher.add_handler(CallbackQueryHandler(admin_menu_callback, pattern=r"^admin_users_page_\d+$"))
    dispatcher.add_handler(CallbackQueryHandler(admin_menu_callback, pattern=r"^admin_active_users_page_\d+$"))
    dispatcher.add_handler(CallbackQueryHandler(admin_menu_callback, pattern=r"^admin_orders_page_\d+$"))
    dispatcher.add_handler(CallbackQueryHandler(admin_menu_callback, pattern=r"^admin_recent_orders_page_\d+$"))
    
    # Add conversation handler for ordering
    order_conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("services", services_command),
            CommandHandler("order", order_command),
            CallbackQueryHandler(services_command, pattern=r"^show_services$"),
            CallbackQueryHandler(order_command, pattern=r"^place_order$"),
        ],
        states={
            SELECTING_PLATFORM: [
                CallbackQueryHandler(platform_callback, pattern=r"^plt_"),
                CallbackQueryHandler(platform_callback, pattern=r"^platform_"),
                CallbackQueryHandler(start_command, pattern=r"^back_to_main$"),
                CallbackQueryHandler(service_callback, pattern=r"^search_services$")
            ],
            SELECTING_CATEGORY: [
                CallbackQueryHandler(category_callback, pattern=r"^cat_"),
                CallbackQueryHandler(category_callback, pattern=r"^category_"),
                CallbackQueryHandler(platform_callback, pattern=r"^back_to_platforms$"),
                CallbackQueryHandler(start_command, pattern=r"^back_to_main$"),
                CallbackQueryHandler(service_callback, pattern=r"^search_services$")
            ],
            SELECTING_SERVICE: [
                CallbackQueryHandler(service_callback),  # Handle all callbacks in this state
                CallbackQueryHandler(category_callback, pattern=r"^back_to_categories$"),
                CallbackQueryHandler(service_callback, pattern=r"^page_\d+$")
            ],
            SEARCHING_SERVICES: [
                MessageHandler(Filters.text & ~Filters.command, process_search_term),
                CallbackQueryHandler(category_callback, pattern=r"^back_to_categories$")
            ],
            ENTERING_LINK: [
                MessageHandler(Filters.text & ~Filters.command, process_link)
            ],
            ENTERING_QUANTITY: [
                MessageHandler(Filters.text & ~Filters.command, process_quantity)
            ],
            ENTERING_COMMENTS: [
                MessageHandler(Filters.text & ~Filters.command, process_comments)
            ],
            CONFIRMING_ORDER: [
                CallbackQueryHandler(confirm_order, pattern=r"^order_confirm$"),
                CallbackQueryHandler(confirm_order, pattern=r"^confirm$"),
                CallbackQueryHandler(lambda update, context: start_command(update, context), pattern=r"^order_cancel$"),
                CallbackQueryHandler(lambda update, context: start_command(update, context), pattern=r"^cancel$")
            ],
        },
        fallbacks=[
            CommandHandler("start", start_command),
            CallbackQueryHandler(start_command, pattern=r"^cancel$")
        ],
        allow_reentry=True
    )
    dispatcher.add_handler(order_conv_handler)
    
    # Add callback query handlers for other main menu items
    dispatcher.add_handler(CallbackQueryHandler(balance_command, pattern=r"^show_balance$"))
    dispatcher.add_handler(CallbackQueryHandler(refresh_balance_callback, pattern=r"^refresh_balance$"))
    dispatcher.add_handler(CallbackQueryHandler(help_command, pattern=r"^help$"))
    dispatcher.add_handler(CallbackQueryHandler(account_command, pattern=r"^account$"))
    dispatcher.add_handler(CallbackQueryHandler(refresh_account_callback, pattern=r"^refresh_account$"))
    dispatcher.add_handler(CallbackQueryHandler(support_command, pattern=r"^support$"))
    
    # Add referrals command handler
    dispatcher.add_handler(CommandHandler("referrals", referrals_command))
    dispatcher.add_handler(CallbackQueryHandler(referrals_command, pattern=r"^referrals$"))
    dispatcher.add_handler(CallbackQueryHandler(check_referrals_callback, pattern=r"^check_referrals$"))
    dispatcher.add_handler(CallbackQueryHandler(check_referrals_callback, pattern=r"^ref_page_\d+$"))
    dispatcher.add_handler(CallbackQueryHandler(do_nothing_callback, pattern=r"^do_nothing$"))
    
    # Add admin referral pagination handler
    dispatcher.add_handler(CallbackQueryHandler(admin_menu_callback, pattern=r"^ref_admin_page_\d+_\d+$"))
    
    # Add support conversation handlers
    dispatcher.add_handler(support_conv_handler)
    dispatcher.add_handler(admin_reply_conv_handler)
    
    # Add recharge handlers
    dispatcher.add_handler(recharge_conv_handler)
    dispatcher.add_handler(CallbackQueryHandler(recharge_command, pattern=r"^recharge$"))
    
    # Add language change handler
    dispatcher.add_handler(CallbackQueryHandler(start_command, pattern=r"^change_language$"))
    dispatcher.add_handler(CallbackQueryHandler(start_command, pattern=r"^back_to_main$"))
    
    # Add tutorial handlers
    dispatcher.add_handler(CommandHandler("tutorial", tutorial_handlers.tutorial_command))
    dispatcher.add_handler(CallbackQueryHandler(tutorial_handlers.show_tutorial_menu, pattern=r"^tutorial$"))
    dispatcher.add_handler(CallbackQueryHandler(tutorial_handlers.show_tutorial, pattern=r"^tutorial_\w+$"))
    
    # Add handler to show command menu when user sends a photo, video, document, or voice message
    dispatcher.add_handler(MessageHandler(
        Filters.photo | Filters.video | Filters.document | Filters.voice,
        lambda update, context: show_command_menu(update, context)
    ))
    
    # Add a handler to ensure the command menu is shown for all users
    # This will be called for any message that isn't handled by other handlers
    dispatcher.add_handler(MessageHandler(
        Filters.all & ~Filters.update.edited_message,
        lambda update, context: ensure_command_menu(update, context)
    ), group=999)  # Use a high group number to make this run last
    
    # Debug handler for unhandled callbacks - logs and processes them
    dispatcher.add_handler(CallbackQueryHandler(debug_callback))
    
    # Set up refund checker
    setup_refund_checker(dispatcher)
    
    # Start the Bot
    updater.start_polling()
    logger.info("Bot started and polling for updates")
    
    # Run the bot until you press Ctrl-C
    updater.idle()
    
    logger.info("Bot stopped")

def ensure_command_menu(update: Update, context: CallbackContext) -> None:
    """Ensure the command menu is shown for all users"""
    # Only process if this is a message
    if not update.message:
        return
    
    user = update.effective_user
    
    # Check if the user already has the command menu active
    if not context.user_data.get('command_menu_active', False):
        try:
            # Import here to avoid circular imports
            from handlers.command_menu import show_command_menu
            # Make sure we have a valid message to reply to
            if hasattr(update, 'message') and update.message is not None:
                # Show the command menu
                show_command_menu(update, context)
                # Mark that the command menu has been shown
                context.user_data['command_menu_active'] = True
                logger.info(f"Command menu shown for user {user.id} via ensure_command_menu")
        except Exception as e:
            logger.error(f"Error ensuring command menu: {e}")
    
    # Let the message be processed by other handlers
    return

# Add webhook support for Railway.app and other platforms
def webhook_main(port=8080):
    """Run bot in webhook mode instead of polling"""
    from telegram.ext import Updater
    from telegram.ext.dispatcher import Dispatcher
    from telegram import Bot, Update
    from flask import Flask, request
    import json
    
    # Get environment variables
    TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    APP_URL = os.getenv('APP_URL')
    
    if not TOKEN or not APP_URL:
        logger.error("TELEGRAM_BOT_TOKEN and APP_URL environment variables must be set")
        sys.exit(1)
    
    # Initialize bot and dispatcher
    bot = Bot(token=TOKEN)
    dispatcher = Dispatcher(bot, None, workers=0)
    
    # Setup handlers just like in main()
    # Start handler
    dispatcher.add_handler(language_conv_handler)
    dispatcher.add_handler(CommandHandler("start", start_command))
    dispatcher.add_handler(CommandHandler("referrals", referrals_command))
    dispatcher.add_handler(CallbackQueryHandler(check_referrals_callback, pattern="^check_referrals$"))
    
    # Services handler
    services_conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("services", services_command),
            CallbackQueryHandler(service_callback, pattern=r"^service_"),
            CallbackQueryHandler(category_callback, pattern=r"^cat_"),
            CallbackQueryHandler(platform_callback, pattern=r"^plt_"),
        ],
        states={
            SELECTING_PLATFORM: [
                CallbackQueryHandler(platform_callback, pattern=r"^plt_"),
            ],
            SELECTING_CATEGORY: [
                CallbackQueryHandler(category_callback, pattern=r"^cat_"),
                CallbackQueryHandler(platform_callback, pattern=r"^back_to_platforms$"),
            ],
            SELECTING_SERVICE: [
                CallbackQueryHandler(service_callback, pattern=r"^service_"),
                CallbackQueryHandler(category_callback, pattern=r"^back_to_categories$"),
                CallbackQueryHandler(service_callback, pattern=r"^page_"),
                CallbackQueryHandler(service_callback, pattern=r"^search_services$"),
            ],
            SEARCHING_SERVICES: [
                MessageHandler(Filters.text & ~Filters.command, process_search_term),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel_command)],
        name="services_conversation",
        persistent=False,
    )
    dispatcher.add_handler(services_conv_handler)
    
    # Order handler
    order_conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("order", order_command),
            CallbackQueryHandler(do_nothing_callback, pattern="^order_"),
        ],
        states={
            ENTERING_LINK: [MessageHandler(Filters.text & ~Filters.command, process_link)],
            ENTERING_QUANTITY: [MessageHandler(Filters.text & ~Filters.command, process_quantity)],
            ENTERING_COMMENTS: [
                MessageHandler(Filters.text & ~Filters.command, process_comments),
                CommandHandler("skip", process_comments),
            ],
            CONFIRMING_ORDER: [
                CallbackQueryHandler(confirm_order, pattern="^confirm_order$"),
                CallbackQueryHandler(cancel_command, pattern="^cancel_order$"),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel_command)],
        name="order_conversation",
        persistent=False,
    )
    dispatcher.add_handler(order_conv_handler)
    
    # Other handlers
    dispatcher.add_handler(CommandHandler("balance", balance_command))
    dispatcher.add_handler(CallbackQueryHandler(refresh_balance_callback, pattern="^refresh_balance$"))
    
    dispatcher.add_handler(CommandHandler("status", status_command))
    dispatcher.add_handler(CommandHandler("checkorder", check_order_command))
    dispatcher.add_handler(CallbackQueryHandler(refresh_status_callback, pattern="^refresh_status$"))
    
    dispatcher.add_handler(CommandHandler("account", account_command))
    dispatcher.add_handler(CallbackQueryHandler(refresh_account_callback, pattern="^refresh_account$"))
    
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("adminhelp", admin_help_command))
    
    dispatcher.add_handler(recharge_conv_handler)
    
    # Command menu handlers
    menu_handlers = get_command_menu_handlers()
    for handler in menu_handlers:
        dispatcher.add_handler(handler)
    
    # Admin handlers - add outside conversation for flexibility
    dispatcher.add_handler(admin_conv_handler)
    
    # Add support handlers
    dispatcher.add_handler(support_conv_handler)
    dispatcher.add_handler(admin_reply_conv_handler)
    
    # Tutorial handlers
    dispatcher.add_handler(tutorial_handlers.get_tutorial_conv_handler())
    
    # More commands
    dispatcher.add_handler(CommandHandler("more", more_command))
    dispatcher.add_handler(CommandHandler("customerservice", customer_service_command))
    dispatcher.add_handler(CommandHandler("myorders", my_orders_command))
    dispatcher.add_handler(CommandHandler("upload", upload_receipt_command))
    
    # Add fallback handler for all other callbacks
    dispatcher.add_handler(CallbackQueryHandler(debug_callback))
    
    # Flask web server for webhook
    app = Flask(__name__)
    
    @app.route('/', methods=['GET'])
    def index():
        return 'Bot is running'
    
    @app.route(f'/{TOKEN}', methods=['POST'])
    def webhook():
        """Handle incoming webhook updates"""
        update = Update.de_json(request.get_json(force=True), bot)
        dispatcher.process_update(update)
        return 'OK'
    
    # Set webhook
    webhook_url = f"{APP_URL}/{TOKEN}"
    bot.set_webhook(webhook_url)
    logger.info(f"Webhook set to {webhook_url}")
    
    # Start Flask server
    logger.info(f"Starting webhook server on port {port}")
    app.run(host='0.0.0.0', port=port)

if __name__ == "__main__":
    main() 