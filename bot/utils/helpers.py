import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import logging
from utils.db import db
from utils.constants import CURRENCY_RATES
from utils.messages import get_message

logger = logging.getLogger(__name__)

def is_admin(user_id):
    """Check if a user is an admin"""
    admin_ids_str = os.getenv("ADMIN_USER_ID", "")
    admin_ids = [id.strip() for id in admin_ids_str.split(",")]
    return str(user_id) in admin_ids

def chunk_list(lst, chunk_size):
    """Split a list into chunks of the specified size"""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

def create_service_keyboard(services, page=0, items_per_page=10, include_back=False, user_id=None):
    """Create a keyboard with services for the specified page"""
    keyboard = []
    
    # Get user's currency preference if user_id is provided
    currency_preference = 'USD'
    if user_id:
        currency_preference = db.get_currency_preference(user_id)
    
    # Convert services dict to list if needed
    if isinstance(services, dict):
        services_list = list(services.values())
    else:
        services_list = services
    
    # Calculate start and end index for pagination
    start_idx = page * items_per_page
    end_idx = min(start_idx + items_per_page, len(services_list))
    
    # Add service buttons
    for service in services_list[start_idx:end_idx]:
        service_id = service.get("service")
        name = service.get("name", "Unknown")
        rate = service.get("rate", 0)
        
        # Convert rate to float if it's a string
        if isinstance(rate, str):
            try:
                rate = float(rate)
            except (ValueError, TypeError):
                logger.warning(f"Invalid rate format for service {service_id}: {rate}")
        
        # Check if this service has a custom price that should skip markup
        if service.get('skip_markup', False) or service.get('has_custom_price', False):
            # Use the rate directly without additional markup
            price_per_1k = rate / 1000
            
            # Store the rate in the service for later use
            service["increased_rate"] = rate
            
            # Format price based on currency preference
            if currency_preference == 'ETB':
                # Convert to ETB
                etb_price = price_per_1k * CURRENCY_RATES["ETB"]
                price_text = f"ETB {etb_price:.2f}/1k"
            else:
                # Format the price with 6 decimal places for precision
                price_text = f"${price_per_1k:.6f}/1k"
        else:
            # Apply price increase based on original price
            original_price = rate
            original_price_per_1k = original_price/1000
            
            # Apply price increase: 100% for prices under $1, 50% for prices $1 and above
            if original_price_per_1k < 1:
                increased_price = original_price_per_1k * 2  # 100% increase
            else:
                increased_price = original_price_per_1k * 1.5  # 50% increase
            
            # Store the increased rate in the service for later use
            service["increased_rate"] = increased_price * 1000
            
            # Format price based on currency preference
            if currency_preference == 'ETB':
                # Convert to ETB
                etb_price = increased_price * CURRENCY_RATES["ETB"]
                price_text = f"ETB {etb_price:.2f}/1k"
            else:
                # Format the price with 6 decimal places for precision
                price_text = f"${increased_price:.6f}/1k"
        
        keyboard.append([
            InlineKeyboardButton(
                f"{name} - {price_text}",
                callback_data=f"service_{service_id}"
            )
        ])
    
    # Add the 11th item - "More" option that leads to admin
    admin_username = os.getenv("ADMIN_USERNAME", "")
    if admin_username:
        keyboard.append([InlineKeyboardButton(
            f"💬 Contact Admin (@{admin_username})",
            url=f"https://t.me/{admin_username}"
        )])
    else:
        # Try to use admin ID if username is not set
        admin_ids_str = os.getenv("ADMIN_USER_ID", "")
        if admin_ids_str:
            # Get the first admin ID from the list
            admin_id = admin_ids_str.split(',')[0].strip()
            keyboard.append([InlineKeyboardButton(
                "💬 Contact Admin",
                url=f"tg://user?id={admin_id}"
            )])
        else:
            # Fallback if no admin info is available
            keyboard.append([InlineKeyboardButton(
                "💬 Contact Admin",
                callback_data="contact_admin"
            )])
    
    # Add a single Back button if requested
    if include_back:
        keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data="back_to_categories")])
    
    return InlineKeyboardMarkup(keyboard)

def create_confirmation_keyboard():
    """Create a keyboard with confirmation and cancel buttons"""
    keyboard = [
        [
            InlineKeyboardButton("✅ Confirm", callback_data="order_confirm"),
            InlineKeyboardButton("❌ Cancel", callback_data="order_cancel")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def format_service_details(service, user_id=None, language='en'):
    """Format service details for display"""
    # Get the original rate
    original_rate = service.get("rate", 0)
    
    # Get the increased rate if available, otherwise calculate it
    if "increased_rate" in service:
        increased_rate = service.get("increased_rate")
    else:
        # Convert to float if it's a string
        if isinstance(original_rate, str):
            try:
                original_rate = float(original_rate)
            except (ValueError, TypeError):
                original_rate = 0
        
        # Check if this service has a custom price that should skip markup
        if service.get('skip_markup', False) or service.get('has_custom_price', False):
            # Use the rate directly without additional markup
            increased_rate = original_rate
        else:
            # Calculate the increased rate
            original_price_per_1k = original_rate/1000
            if original_price_per_1k < 1:
                increased_price = original_price_per_1k * 2  # 100% increase
            else:
                increased_price = original_price_per_1k * 1.5  # 50% increase
            
            increased_rate = increased_price * 1000
    
    # Format the price with 6 decimal places
    price_per_1k = increased_rate/1000
    
    # Always show both USD and ETB prices
    etb_price_per_1k = price_per_1k * CURRENCY_RATES["ETB"]
    
    # Get service details messages
    service_details_title = get_message(language, 'services', 'service_details')
    service_id_text = get_message(language, 'services', 'service_id').format(id=service.get('service', 'Unknown'))
    service_name_text = get_message(language, 'services', 'service_name').format(name=service.get('name', 'Unknown'))
    service_category_text = get_message(language, 'services', 'service_category').format(category=service.get('category', 'Unknown'))
    service_rate_text = get_message(language, 'services', 'service_rate').format(rate=price_per_1k)
    service_min_text = get_message(language, 'services', 'service_min').format(min=service.get('min', 0))
    service_max_text = get_message(language, 'services', 'service_max').format(max=service.get('max', 0))
    
    # Get description if available
    description = service.get('description', '')
    service_description_text = ""
    if description:
        service_description_text = get_message(language, 'services', 'service_description').format(description=description)
    
    service_text = (
        f"{service_details_title}\n\n"
        f"{service_id_text}\n"
        f"{service_name_text}\n"
        f"{service_category_text}\n"
        f"{service_rate_text}\n"
        f"{service_min_text}\n"
        f"{service_max_text}"
    )
    
    # Add description if available
    if service_description_text:
        service_text += f"\n{service_description_text}"
    
    return service_text

def format_order_details(order, service_info=None, user_id=None):
    """Format order details for display"""
    # Get user's currency preference if user_id is provided
    currency_preference = 'USD'
    if user_id:
        currency_preference = db.get_currency_preference(user_id)
    
    service_name = "Unknown"
    if service_info:
        service_name = service_info.get("name", "Unknown")
    
    price = order.get('price', 0)
    
    # Format price based on currency preference
    if currency_preference == 'ETB':
        # Convert to ETB
        etb_price = price * CURRENCY_RATES["ETB"]
        price_display = f"ETB {etb_price:.2f} (≈${price:.2f})"
    else:
        price_display = f"${price:.2f}"
    
    order_text = (
        f"🔢 <b>Order #{order.get('id', 'Unknown')}</b>\n"
        f"📊 Service: {service_name}\n"
        f"📊 Quantity: {order.get('quantity', 'Unknown')}\n"
        f"💰 Price: {price_display}\n"
        f"📊 Status: {order.get('status', 'Unknown')}\n"
        f"🕒 Date: {order.get('created_at', 'Unknown')[:10]}"
    )
    return order_text

def update_user_info(user):
    """Update user information in the database"""
    from utils.db import db
    
    # Update user information
    user_data = {
        'username': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name
    }
    
    # Update user data in database
    db.update_user_data(user.id, user_data) 