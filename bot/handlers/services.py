import logging
import time
import re
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler

from utils.api_client import api_client
from utils.db import db
from utils.helpers import format_service_details, chunk_list, is_admin
from utils.constants import CURRENCY_RATES
from utils.messages import get_message

# Define states
SELECTING_PLATFORM, SELECTING_CATEGORY, SELECTING_SERVICE = range(3)

# Module logger
logger = logging.getLogger(__name__)

# Cache for services with expiration time (5 minutes)
_services_cache = {
    "data": None,
    "timestamp": 0,
    "expiry": 300  # 5 minutes
}

# Cache for categories with expiration time (5 minutes)
_categories_cache = {
    "data": None,
    "timestamp": 0,
    "expiry": 300  # 5 minutes
}

# Cache for platforms with expiration time (5 minutes)
_platforms_cache = {
    "data": None,
    "timestamp": 0,
    "expiry": 300  # 5 minutes
}

def invalidate_services_cache():
    """Invalidate the services cache to force a refresh on next fetch"""
    global _services_cache
    _services_cache["data"] = None
    _services_cache["timestamp"] = 0
    logger.info("Services cache invalidated")

def _get_services():
    """Get services from API or cache"""
    current_time = time.time()
    
    # Check if cache is expired
    if _services_cache["data"] is None or (current_time - _services_cache["timestamp"] > _services_cache["expiry"]):
        logger.info("Fetching services from API")
        
        # Fetch services from API
        response = api_client.get_services()
        
        if response and isinstance(response, list):
            # Update cache
            _services_cache["data"] = response
            _services_cache["timestamp"] = current_time
            logger.info(f"Successfully cached {len(response)} services")
        else:
            logger.error(f"Failed to fetch services from API: {response}")
            # Return empty list if failed
            return []
    
    return _services_cache["data"]

def _get_platforms():
    """Extract main platforms from categories"""
    current_time = time.time()
    
    # Check if cache is expired
    if _platforms_cache["data"] is None or (current_time - _platforms_cache["timestamp"] > _platforms_cache["expiry"]):
        logger.info("Extracting platforms from categories")
        
        # Get categories first
        categories = _get_categories()
        
        # Extract main platforms by looking for common prefixes
        platforms = {}
        category_to_platform = {}
        
        # Special case for categories that should be grouped
        platform_prefixes = {
            "Facebook": "Facebook",
            "Instagram": "Instagram",
            "TikTok": "TikTok",
            "YouTube": "YouTube",
            "Twitter": "Twitter",
            "Telegram": "Telegram",
            "Discord": "Discord",
            "Spotify": "Spotify",
            "Twitch": "Twitch",
            "Reddit": "Reddit",
            "LinkedIn": "LinkedIn",
            "SoundCloud": "SoundCloud",
            "WhatsApp": "WhatsApp",
            "Snapchat": "Snapchat",
            "Pinterest": "Pinterest"
        }
        
        # Map categories to platforms
        for category in categories:
            assigned = False
            
            # Check if category starts with a known platform
            for prefix, platform in platform_prefixes.items():
                if category.startswith(prefix):
                    if platform not in platforms:
                        platforms[platform] = []
                    platforms[platform].append(category)
                    category_to_platform[category] = platform
                    assigned = True
                    break
            
            # If not assigned to a specific platform, put in "Other"
            if not assigned:
                if "Other" not in platforms:
                    platforms["Other"] = []
                platforms["Other"].append(category)
                category_to_platform[category] = "Other"
        
        # Update cache
        _platforms_cache["data"] = {
            "platforms": platforms,
            "category_to_platform": category_to_platform
        }
        _platforms_cache["timestamp"] = current_time
        logger.info(f"Successfully cached {len(platforms)} platforms")
    
    return _platforms_cache["data"]

def _get_categories():
    """Get unique categories from services"""
    current_time = time.time()
    
    # Check if cache is expired
    if _categories_cache["data"] is None or (current_time - _categories_cache["timestamp"] > _categories_cache["expiry"]):
        logger.info("Extracting categories from services")
        
        # Get services
        services = _get_services()
        
        # Extract unique categories
        categories = []
        for service in services:
            category = service.get("category", "Uncategorized")
            if category and category not in categories:
                categories.append(category)
        
        # Sort categories
        categories.sort()
        
        # Update cache
        _categories_cache["data"] = categories
        _categories_cache["timestamp"] = current_time
        logger.info(f"Successfully cached {len(categories)} categories: {categories[:5]}...")
    
    return _categories_cache["data"]

def sanitize_callback_data(text):
    """Sanitize text for use in callback data to stay under 64 bytes"""
    if not text:
        return "unknown"
        
    # Replace special characters and keep only alphanumeric and some punctuation
    sanitized = re.sub(r'[^\w\s\-]', '', text)
    # Replace spaces with underscores and trim
    sanitized = sanitized.replace(' ', '_')[:30]
    return sanitized.lower()

def services_command(update: Update, context: CallbackContext):
    """Handler for /services command - Show platforms first"""
    user = update.effective_user
    db.update_user_activity(user.id)
    
    # Get user's language preference
    language = db.get_language(user.id)
    
    try:
        # Get platforms
        platform_data = _get_platforms()
        platforms = list(platform_data["platforms"].keys())
        platforms.sort()
        
        logger.info(f"Retrieved {len(platforms)} platforms")
        
        # Create buttons for platforms
        buttons = []
        
        # Add "All Services" button at the top
        buttons.append([InlineKeyboardButton(get_message(language, 'services', 'all_services'), callback_data="platform_all")])
        
        # Add search button
        buttons.append([InlineKeyboardButton(get_message(language, 'services', 'search_services'), callback_data="search_services")])
        
        # Add platform buttons
        platform_buttons = []
        for i, platform in enumerate(platforms):
            # Store the platform mapping in context
            if "platform_map" not in context.bot_data:
                context.bot_data["platform_map"] = {}
            
            # Use index instead of full platform name in callback data
            callback_id = f"plt_{i}"
            context.bot_data["platform_map"][callback_id] = platform
            
            # Count categories in this platform
            category_count = len(platform_data["platforms"][platform])
            
            # Create button with platform name and category count
            platform_buttons.append(InlineKeyboardButton(
                get_message(language, 'services', 'platform_button').format(platform=platform, count=category_count), 
                callback_data=callback_id
            ))
        
        # Group platform buttons in rows of 1
        for chunk in chunk_list(platform_buttons, 1):
            buttons.append(chunk)
        
        # Create keyboard markup
        keyboard = InlineKeyboardMarkup(buttons)
        
        # Send platforms message
        platforms_title = get_message(language, 'services', 'platforms_title')
        platforms_description = get_message(language, 'services', 'platforms_description')
        message_text = f"{platforms_title}\n\n{platforms_description}"
        
        if update.callback_query:
            query = update.callback_query
            query.answer()
            query.edit_message_text(
                message_text,
                reply_markup=keyboard,
                parse_mode="HTML"
            )
        else:
            update.message.reply_html(
                message_text,
                reply_markup=keyboard
            )
        
        logger.info(f"Successfully displayed platforms to user {user.id}")
        return SELECTING_PLATFORM
    except Exception as e:
        logger.error(f"Error in services_command: {e}", exc_info=True)
        error_text = get_message(language, 'services', 'error_retrieving')
        if update.callback_query:
            update.callback_query.answer()
            update.callback_query.edit_message_text(error_text)
        else:
            update.message.reply_text(error_text)
        return ConversationHandler.END

def platform_callback(update: Update, context: CallbackContext):
    """Handle platform selection"""
    query = update.callback_query
    query.answer()
    user = update.effective_user
    
    # Get user's language preference
    language = db.get_language(user.id)
    
    try:
        # Get callback data
        callback_data = query.data
        
        # Get platform name from callback data
        if callback_data == "platform_all":
            # If "All Services" selected, go straight to categories
            return show_all_categories(update, context)
        elif callback_data.startswith("plt_"):
            # Get the platform from the mapping
            platform_map = context.bot_data.get("platform_map", {})
            platform = platform_map.get(callback_data, "Other")
        else:
            # Handle unexpected callback data
            logger.warning(f"Unexpected platform callback data: {callback_data}")
            platform = "Other"
        
        logger.info(f"Selected platform: {platform}")
        
        # Store selected platform in context
        context.user_data["selected_platform"] = platform
        
        # Get categories for this platform
        platforms_data = _get_platforms()
        platform_categories = platforms_data["platforms"].get(platform, [])
        platform_categories.sort()
        
        # Create buttons for categories
        buttons = []
        
        # Add "All [Platform] Services" button at the top
        buttons.append([InlineKeyboardButton(f"{get_message(language, 'services', 'all_services')} - {platform}", callback_data="category_platform_all")])
        
        # Add search button
        buttons.append([InlineKeyboardButton(get_message(language, 'services', 'search_services'), callback_data="search_services")])
        
        # Add category buttons
        category_buttons = []
        for i, category in enumerate(platform_categories):
            # Store the category mapping in context
            if "category_map" not in context.bot_data:
                context.bot_data["category_map"] = {}
            
            # Use index instead of full category name in callback data
            callback_id = f"cat_{i}"
            context.bot_data["category_map"][callback_id] = category
            
            # Create button with safe callback data
            category_buttons.append(InlineKeyboardButton(
                f"📂 {category}", 
                callback_data=callback_id
            ))
        
        # Group category buttons in rows of 1
        for chunk in chunk_list(category_buttons, 1):
            buttons.append(chunk)
        
        # Add "Back to Platforms" button
        buttons.append([InlineKeyboardButton(get_message(language, 'services', 'back_to_platforms'), callback_data="back_to_platforms")])
        
        # Create keyboard markup
        keyboard = InlineKeyboardMarkup(buttons)
        
        # Send categories message
        categories_title = get_message(language, 'services', 'categories_title').format(platform=platform)
        categories_description = get_message(language, 'services', 'categories_description')
        message_text = f"{categories_title}\n\n{categories_description}"
        
        query.edit_message_text(
            message_text,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        
        logger.info(f"Displayed {len(platform_categories)} categories for platform {platform}")
        return SELECTING_CATEGORY
    except Exception as e:
        logger.error(f"Error in platform_callback: {e}", exc_info=True)
        error_text = get_message(language, 'services', 'error_retrieving')
        query.edit_message_text(error_text)
        return SELECTING_PLATFORM

def show_all_categories(update: Update, context: CallbackContext):
    """Show all categories without platform filtering"""
    user = update.effective_user
    
    # Get user's language preference
    language = db.get_language(user.id)
    
    try:
        # Get all categories
        categories = _get_categories()
        logger.info(f"Retrieved {len(categories)} categories for all platforms")
        
        # Create buttons for categories
        buttons = []
        
        # Add "All Services" button at the top
        buttons.append([InlineKeyboardButton(get_message(language, 'services', 'all_services'), callback_data="category_all")])
        
        # Add search button
        buttons.append([InlineKeyboardButton(get_message(language, 'services', 'search_services'), callback_data="search_services")])
        
        # Add category buttons
        category_buttons = []
        for i, category in enumerate(categories):
            # Store the category mapping in context
            if "category_map" not in context.bot_data:
                context.bot_data["category_map"] = {}
            
            # Use index instead of full category name in callback data
            callback_id = f"cat_{i}"
            context.bot_data["category_map"][callback_id] = category
            
            # Create button with safe callback data
            category_buttons.append(InlineKeyboardButton(
                f"📂 {category}", 
                callback_data=callback_id
            ))
        
        # Group category buttons in rows of 1
        for chunk in chunk_list(category_buttons, 1):
            buttons.append(chunk)
        
        # Add "Back to Platforms" button
        buttons.append([InlineKeyboardButton(get_message(language, 'services', 'back_to_platforms'), callback_data="back_to_platforms")])
        
        # Create keyboard markup
        keyboard = InlineKeyboardMarkup(buttons)
        
        # Send categories message
        categories_title = get_message(language, 'services', 'categories_title').format(platform="All")
        categories_description = get_message(language, 'services', 'categories_description')
        message_text = f"{categories_title}\n\n{categories_description}"
        
        query = update.callback_query
        query.edit_message_text(
            message_text,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        
        logger.info(f"Displayed all {len(categories)} categories")
        return SELECTING_CATEGORY
    except Exception as e:
        logger.error(f"Error in show_all_categories: {e}", exc_info=True)
        error_text = get_message(language, 'services', 'error_retrieving')
        if update.callback_query:
            update.callback_query.answer()
            update.callback_query.edit_message_text(error_text)
        else:
            update.message.reply_text(error_text)
        return ConversationHandler.END

def category_callback(update: Update, context: CallbackContext):
    """Handle category selection"""
    query = update.callback_query
    query.answer()
    user = update.effective_user
    
    # Get user's language preference
    language = db.get_language(user.id)
    
    try:
        # Get callback data
        callback_data = query.data
        
        # Handle back to platforms
        if callback_data == "back_to_platforms":
            return services_command(update, context)
            
        # Handle back to categories from service list
        if callback_data == "back_to_categories":
            logger.info("Handling back to categories callback")
            # Get the current platform from user data
            platform = context.user_data.get("selected_platform", None)
            if platform:
                # Show categories for the selected platform
                return platform_callback(update, context)
            else:
                # If no platform is stored, go back to platforms
                return services_command(update, context)
        
        # Get category name from callback data
        if callback_data == "category_all":
            category = "all"
        elif callback_data == "category_platform_all":
            # Get all services for the selected platform
            platform = context.user_data.get("selected_platform", "Other")
            platform_data = _get_platforms()
            
            # Get all services for this platform
            all_services = _get_services()
            
            # Filter services by platform
            services = [service for service in all_services if service.get("platform", "Other") == platform]
            
            # Store services in context
            context.user_data["filtered_services"] = services
            context.user_data["current_page"] = 0
            
            logger.info(f"Filtered to {len(services)} services for platform {platform}")
            
            # Show services
            return display_services_page(update, context)
        elif callback_data.startswith("cat_"):
            # Get the category from the mapping
            category_map = context.bot_data.get("category_map", {})
            category = category_map.get(callback_data, "Uncategorized")
        else:
            # Handle unexpected callback data
            logger.warning(f"Unexpected category callback data: {callback_data}")
            category = "Uncategorized"
        
        logger.info(f"Selected category: {category}")
        
        # Store selected category
        context.user_data["selected_category"] = category
        
        # Get services
        all_services = _get_services()
        
        # Filter services by category if not "all"
        if category != "all":
            services = [service for service in all_services if service.get("category", "Uncategorized") == category]
        else:
            services = all_services
        
        # Store services in context
        context.user_data["filtered_services"] = services
        context.user_data["current_page"] = 0
        
        logger.info(f"Filtered to {len(services)} services for category {category}")
        
        # Show services
        return display_services_page(update, context)
    except Exception as e:
        logger.error(f"Error in category_callback: {e}", exc_info=True)
        error_text = get_message(language, 'services', 'error_retrieving')
        query.edit_message_text(error_text)
        return SELECTING_CATEGORY

def display_services_page(update: Update, context: CallbackContext):
    """Display a page of services"""
    query = update.callback_query
    user = update.effective_user
    
    # Get user's language preference
    language = db.get_language(user.id)
    
    try:
        # Get services from context
        services = context.user_data.get("filtered_services", [])
        current_page = context.user_data.get("current_page", 0)
        
        # Calculate pagination
        items_per_page = 10  # Keep at 10 for actual services
        total_pages = max(1, (len(services) - 1) // items_per_page + 1)
        
        # Ensure current page is valid
        if current_page < 0:
            current_page = 0
        elif current_page >= total_pages:
            current_page = total_pages - 1
        
        # Update current page in context
        context.user_data["current_page"] = current_page
        
        # Get services for current page
        start_idx = current_page * items_per_page
        end_idx = min(start_idx + items_per_page, len(services))
        page_services = services[start_idx:end_idx]
        
        # Create buttons for services
        buttons = []
        
        for service in page_services:
            service_id = service.get("service")
            service_name = service.get("name", f"Service #{service_id}")
            
            # Fix the type error by ensuring service_rate is numeric
            service_rate = service.get("rate", 0)
            try:
                # Convert to float if it's a string
                if isinstance(service_rate, str):
                    service_rate = float(service_rate)
                
                # Check if this service has a custom price that should skip markup
                if service.get('skip_markup', False) or service.get('has_custom_price', False):
                    # Use the rate directly without additional markup
                    price_per_1k = service_rate / 1000
                    
                    # Always show both USD and ETB prices
                    etb_price = price_per_1k * CURRENCY_RATES["ETB"]
                    price_text = f"${price_per_1k:.6f} / ETB {etb_price:.2f}/1k"
                    
                    # Store the rate in the service for later use
                    service["increased_rate"] = service_rate
                else:
                    # Apply price increase based on original price
                    original_price_per_1k = service_rate/1000
                    
                    # Apply price increase: 100% for prices under $1, 50% for prices $1 and above
                    if original_price_per_1k < 1:
                        increased_price = original_price_per_1k * 2  # 100% increase
                    else:
                        increased_price = original_price_per_1k * 1.5  # 50% increase
                    
                    # Always show both USD and ETB prices
                    etb_price = increased_price * CURRENCY_RATES["ETB"]
                    price_text = f"${increased_price:.6f} / ETB {etb_price:.2f}/1k"
                    
                    # Store the increased rate in the service for later use
                    service["increased_rate"] = increased_price * 1000
                
            except (ValueError, TypeError):
                # Handle conversion errors
                logger.warning(f"Invalid rate format for service {service_id}: {service_rate}")
                price_text = f"${service_rate} / ETB ?"
            
            # Create button text with price
            # Standard format for all searches
            button_text = f"{service_name} - {price_text}"
            
            # Add button
            buttons.append([InlineKeyboardButton(
                button_text,
                callback_data=f"service_{service_id}"
            )])
        
        # Add search button
        buttons.append([InlineKeyboardButton(
            get_message(language, 'services', 'search_services'),
            callback_data="search_services"
        )])
        
        # Add the "More Options" button in its own row
        admin_username = os.getenv("ADMIN_USERNAME", "")
        if admin_username:
            buttons.append([InlineKeyboardButton(
                f"💬 Contact Admin (@{admin_username})",
                url=f"https://t.me/{admin_username}"
            )])
        else:
            # Get admin user ID as fallback
            admin_ids_str = os.getenv("ADMIN_USER_ID", "")
            if admin_ids_str:
                admin_id = admin_ids_str.split(',')[0]
                buttons.append([InlineKeyboardButton(
                    "💬 Contact Admin",
                    url=f"tg://user?id={admin_id}"
                )])
            else:
                # Final fallback if no admin info is available
                buttons.append([InlineKeyboardButton(
                    "💬 Contact Admin",
                    callback_data="contact_admin"
                )])
        
        # Add pagination buttons if there are multiple pages
        if total_pages > 1:
            # Create page number buttons
            page_buttons = []
            
            # Add Previous button if not on first page
            if current_page > 0:
                page_buttons.append(InlineKeyboardButton("⬅️ Prev", callback_data=f"page_{current_page - 1}"))
            
            # Add page number buttons (show up to 5 page numbers)
            max_page_buttons = min(5, total_pages)
            
            # Calculate which page numbers to show
            if total_pages <= max_page_buttons:
                # Show all pages if there are 5 or fewer
                page_range = range(total_pages)
            else:
                # Show pages centered around current page
                start_page = max(0, current_page - max_page_buttons // 2)
                end_page = min(total_pages, start_page + max_page_buttons)
                
                # Adjust start_page if we're near the end
                if end_page == total_pages:
                    start_page = max(0, total_pages - max_page_buttons)
                
                page_range = range(start_page, end_page)
            
            # Add page number buttons
            for page_num in page_range:
                # Highlight current page
                if page_num == current_page:
                    button_text = f"[{page_num + 1}]"
                else:
                    button_text = f"{page_num + 1}"
                
                page_buttons.append(InlineKeyboardButton(
                    button_text, 
                    callback_data=f"page_{page_num}"
                ))
            
            # Add Next button if not on last page
            if current_page < total_pages - 1:
                page_buttons.append(InlineKeyboardButton("Next ➡️", callback_data=f"page_{current_page + 1}"))
            
            # Add pagination row
            buttons.append(page_buttons)
        
        # Add a Back button
        buttons.append([InlineKeyboardButton(get_message(language, 'services', 'back_to_categories'), callback_data="back_to_categories")])
        
        # Create keyboard markup
        keyboard = InlineKeyboardMarkup(buttons)
        
        # Get the category name
        category_name = context.user_data.get("selected_category", "all")
        if category_name == "all":
            category_name = get_message(language, 'services', 'all_services')
        
        # Add page information if there are multiple pages
        page_info = ""
        if total_pages > 1:
            page_info = get_message(language, 'services', 'services_page_info').format(current_page=current_page + 1, total_pages=total_pages)
        
        # Edit message with services list
        try:
            services_title = get_message(language, 'services', 'services_title').format(category=category_name)
            services_description = get_message(language, 'services', 'services_description')
            message_text = f"{services_title}{page_info}\n\n{services_description}"
            
            query.edit_message_text(
                message_text,
                reply_markup=keyboard,
                parse_mode="HTML"
            )
        except Exception as e:
            logger.error(f"Error updating message: {e}")
            # If we can't edit message, try sending a new one
            try:
                services_title = get_message(language, 'services', 'services_title').format(category=category_name)
                services_description = get_message(language, 'services', 'services_description')
                message_text = f"{services_title}{page_info}\n\n{services_description}"
                
                query.message.reply_html(
                    message_text,
                    reply_markup=keyboard
                )
            except Exception as e2:
                logger.error(f"Error sending new message: {e2}")
        
        return SELECTING_SERVICE
    except Exception as e:
        logger.error(f"Error in display_services_page: {e}", exc_info=True)
        try:
            error_text = get_message(language, 'services', 'error_display')
            query.edit_message_text(error_text)
        except:
            pass
        return SELECTING_CATEGORY

def view_search_results(update: Update, context: CallbackContext):
    """Display search results"""
    query = update.callback_query
    query.answer()
    
    # Get user's language preference
    user = update.effective_user
    language = db.get_language(user.id)
    
    try:
        # Ensure we have filtered services to display
        if "filtered_services" not in context.user_data or not context.user_data["filtered_services"]:
            query.edit_message_text(
                "❌ No search results to display. Please try a new search.",
                parse_mode="HTML"
            )
            return SELECTING_SERVICE
            
        # Reset page to 0 to show first page of results
        context.user_data["current_page"] = 0
        
        # Log that we're displaying search results
        search_term = context.user_data.get("selected_category", "")
        if search_term.startswith("Search: "):
            search_term = search_term[8:]  # Remove "Search: " prefix
        logger.info(f"Displaying search results for '{search_term}' - {len(context.user_data['filtered_services'])} services found")
        
        # Display the services page with filtered results
        return display_services_page(update, context)
    except Exception as e:
        logger.error(f"Error in view_search_results: {e}", exc_info=True)
        query.edit_message_text(
            "⚠️ An error occurred while displaying search results. Please try again.",
            parse_mode="HTML"
        )
        return SELECTING_SERVICE

def show_services_list(update: Update, context: CallbackContext, services):
    """Show a list of services"""
    # Store services in context
    context.user_data["filtered_services"] = services
    context.user_data["current_page"] = 0
    
    # Display the services page
    return display_services_page(update, context)

def service_callback(update: Update, context: CallbackContext):
    """Handle service selection and navigation"""
    # Get the callback data
    query = update.callback_query
    callback_data = query.data
    user = update.effective_user
    
    # Get user's language preference
    language = db.get_language(user.id)
    
    # Update user activity
    db.update_user_activity(user.id)
    
    # Check if we're processing a service directly
    direct_processing = False
    
    # Log the callback
    logger.debug(f"Service callback: {callback_data}")
    
    try:
        # Handle search services button
        if callback_data == "search_services":
            return search_services_callback(update, context)
            
        # Handle view search results button
        if callback_data == "view_search_results":
            return view_search_results(update, context)
            
        # Handle back to services button
        if callback_data == "back_to_services":
            # Get services for the current category
            category = context.user_data.get("selected_category", {}).get("name")
            
            # If no category selected or all services were shown
            if not category or category == "All Services":
                # Get all services
                services = _get_services()
            else:
                # Filter services by selected category
                services = [service for service in _get_services() if service.get("category") == category]
            
            # Show services list
            show_services_list(update, context, services)
            return SELECTING_SERVICE
        
        # Handle back to categories button
        if callback_data == "back_to_categories":
            # If we came from a platform selection
            if "selected_platform" in context.user_data:
                platform = context.user_data.get("selected_platform")
                # Show platform categories
                platform_data = _get_platforms()
                platform_categories = platform_data["platforms"].get(platform, [])
                platform_categories.sort()
                
                # Create buttons for categories
                buttons = []
                
                # Add "All [Platform] Services" button at the top
                buttons.append([InlineKeyboardButton(f"{get_message(language, 'services', 'all_services')} - {platform}", callback_data="category_platform_all")])
                
                # Add search button
                buttons.append([InlineKeyboardButton(get_message(language, 'services', 'search_services'), callback_data="search_services")])
                
                # Add category buttons
                category_buttons = []
                for i, category in enumerate(platform_categories):
                    # Store the category mapping in context
                    if "category_map" not in context.bot_data:
                        context.bot_data["category_map"] = {}
                    
                    # Use index instead of full category name in callback data
                    callback_id = f"cat_{i}"
                    context.bot_data["category_map"][callback_id] = category
                    
                    # Create button with safe callback data
                    category_buttons.append(InlineKeyboardButton(
                        f"📂 {category}", 
                        callback_data=callback_id
                    ))
                
                # Group category buttons in rows of 1
                for chunk in chunk_list(category_buttons, 1):
                    buttons.append(chunk)
                
                # Add "Back to Platforms" button
                buttons.append([InlineKeyboardButton(get_message(language, 'services', 'back_to_platforms'), callback_data="back_to_platforms")])
                
                # Create keyboard markup
                keyboard = InlineKeyboardMarkup(buttons)
                
                # Send categories message
                categories_title = get_message(language, 'services', 'categories_title').format(platform=platform)
                categories_description = get_message(language, 'services', 'categories_description')
                message_text = f"{categories_title}\n\n{categories_description}"
                
                query.edit_message_text(
                    message_text,
                    reply_markup=keyboard,
                    parse_mode="HTML"
                )
                
                return SELECTING_CATEGORY
            else:
                # Otherwise show all categories
                return show_all_categories(update, context)
        
        # Handle service selection
        if callback_data.startswith("service_") and not direct_processing:
            try:
                # Get service ID
                service_id = callback_data.split("_")[1]
                
                # Get services
                services = _get_services()
                
                # Find service by ID
                service_info = None
                for service in services:
                    if str(service.get("service")) == service_id:
                        service_info = service
                        break
                
                if not service_info:
                    error_text = get_message(language, 'services', 'error_service_details')
                    query.edit_message_text(error_text)
                    return SELECTING_SERVICE
                
                # Store in user data
                context.user_data["selected_service"] = {
                    "id": service_id,
                    "info": service_info
                }
                
                # Format service details
                service_text = format_service_details(service_info, user.id, language)
                
                # Create order button
                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton(get_message(language, 'services', 'place_order'), callback_data=f"order_{service_id}")],
                    [InlineKeyboardButton(get_message(language, 'services', 'back_to_services'), callback_data=f"back_to_services")]
                ])
                
                # Edit message with service details
                query.edit_message_text(
                    f"{service_text}\n\n"
                    f"{get_message(language, 'services', 'services_description')}",
                    reply_markup=keyboard,
                    parse_mode="HTML"
                )
                
                return SELECTING_SERVICE
            except Exception as e:
                logger.error(f"Error showing service details: {e}")
                error_text = get_message(language, 'services', 'error_service_details')
                query.edit_message_text(error_text)
                return SELECTING_SERVICE
                
        # Handle order button
        if callback_data.startswith("order_"):
            # Forward to order handler
            service_id = callback_data.split("_")[1]
            
            # Store in user data
            for service in _get_services():
                if str(service.get("service")) == service_id:
                    context.user_data["selected_service"] = {
                        "id": service_id,
                        "info": service
                    }
                    break
            
            # Import order command to handle the flow
            from ..order import order_command, ENTERING_LINK
            return order_command(update, context)
            
        # Handle page navigation
        if callback_data.startswith("page_"):
            # Get page number
            page = int(callback_data.split("_")[1])
            
            # Update current page in context
            context.user_data["current_page"] = page
            
            # Display the services page
            return display_services_page(update, context)
            
        # Handle contact admin button
        if callback_data == "contact_admin":
            return contact_admin(update, context)
            
    except Exception as e:
        logger.error(f"Error in service_callback: {e}")
        error_text = get_message(language, 'services', 'error_retrieving')
        query.edit_message_text(f"{error_text}")
        return ConversationHandler.END
    
    # Default fallback
    error_text = get_message(language, 'services', 'error_retrieving')
    query.edit_message_text(error_text)
    return SELECTING_SERVICE

def contact_admin(update: Update, context: CallbackContext):
    """Handle contact admin button click"""
    query = update.callback_query
    query.answer()
    user = update.effective_user
    
    # Get user's language preference
    language = db.get_language(user.id)
    
    try:
        admin_ids_str = os.getenv("ADMIN_USER_ID", "")
        
        # Send a message with admin contact info
        query.edit_message_text(
            "📞 <b>Contact Admin</b>\n\n"
            "If you need assistance or have questions about our services, "
            "please contact the administrator.\n\n"
            f"Admin ID: <code>{admin_ids_str.split(',')[0]}</code>\n\n"
            "You can forward this message to start a conversation.",
            parse_mode="HTML"
        )
        
        return ConversationHandler.END
    except Exception as e:
        logger.error(f"Error in contact_admin: {e}", exc_info=True)
        error_text = get_message(language, 'services', 'error_retrieving')
        query.edit_message_text(error_text)
        return ConversationHandler.END

# Define state for search
SEARCHING_SERVICES = 10

def search_services_callback(update: Update, context: CallbackContext):
    """Handle search services button press"""
    query = update.callback_query
    query.answer() # Always answer the callback to prevent the "loading" animation
    user = update.effective_user
    
    # Get user's language preference
    language = db.get_language(user.id)
    
    try:
        # Reset search type and set user state to waiting for search term
        context.user_data["search_type"] = "text"  # Default to text search
        context.user_data["state"] = "waiting_for_search_term"
        
        # Create a clear, enhanced search instructions message
        search_instructions = (
            "🔍 <b>Search Services</b>\n\n"
            "Please enter a search term to find services:\n\n"
            "💡 <b>Search Tips:</b>\n\n"
            "• Enter a <b>service ID</b> (e.g., <code>1234</code>) to find a specific service\n"
            "• Enter a <b>service name</b> like <code>Telegram Members</code>\n"
            "• Enter keywords like <code>followers</code> or <code>views</code>\n\n"
            "⌨️ <i>Type your search term and send it</i>"
        )
        
        query.edit_message_text(
            search_instructions,
            parse_mode="HTML"
        )
        
        return SEARCHING_SERVICES
    except Exception as e:
        logger.error(f"Error in search_services_callback: {e}", exc_info=True)
        error_text = get_message(language, 'services', 'error_search')
        query.edit_message_text(error_text)
        return SELECTING_SERVICE

def process_search_term(update: Update, context: CallbackContext):
    """Process search term entered by user"""
    user = update.effective_user
    db.update_user_activity(user.id)
    
    # Get user's language preference
    language = db.get_language(user.id)
    
    # Get search term
    search_term = update.message.text.strip().lower()
    
    # Set defaults to prevent errors
    filtered_services = []
    
    try:
        # First check if the input is empty
        if not search_term:
            logger.warning("Empty search term received")
            update.message.reply_html("Please enter a valid search term.")
            return SEARCHING_SERVICES
            
        # Check if the search term is a numeric ID
        is_id_search = search_term.isdigit()
        all_services = _get_services()
        
        if is_id_search:
            # Search by service ID
            service_id = search_term
            logger.info(f"Searching for service with ID: {service_id}")
            
            for service in all_services:
                if str(service.get("service")) == service_id:
                    filtered_services.append(service)
                    break
            
            if filtered_services:
                logger.info(f"Found service with ID {service_id}")
                # If we found a service by ID, we can directly show its details
                service_info = filtered_services[0]
                
                # Store selected service in context
                context.user_data["selected_service"] = service_info
                
                # Format service details
                service_details = format_service_details(service_info, language)
                
                # Create keyboard with order button
                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton(get_message(language, 'services', 'order_service'), callback_data=f"order_{service_info['service']}")],
                    [InlineKeyboardButton(get_message(language, 'services', 'back_to_services'), callback_data="back_to_services")],
                    [InlineKeyboardButton(get_message(language, 'services', 'back_to_categories'), callback_data="back_to_categories")]
                ])
                
                # Send service details
                update.message.reply_html(
                    f"🔍 <b>Service Found by ID: {service_id}</b>\n\n{service_details}",
                    reply_markup=keyboard
                )
                
                return SELECTING_SERVICE
        
        # If not an ID search or no service found by ID, do regular text search
        if not is_id_search or not filtered_services:
            filtered_services = []
            
            # Regular text search - Filter services by search term
        # We'll use sophisticated matching for multi-word searches
        search_words = search_term.split()
        
        # If only one search term, do simple matching
        if len(search_words) == 1:
            for service in all_services:
                service_name = service.get("name", "").lower()
                service_category = service.get("category", "").lower()
                
                # Check if the word appears in service name or category
                if search_term in service_name or search_term in service_category:
                    filtered_services.append(service)
        else:
            # For multi-word searches, try different matching strategies
            # First, exact phrase match
            exact_matches = []
            for service in all_services:
                service_name = service.get("name", "").lower()
                if search_term in service_name:
                    exact_matches.append(service)
            
            # If we have exact matches, use those
            if exact_matches:
                filtered_services = exact_matches
            else:
                # Otherwise, match if ANY word is present
                for service in all_services:
                    service_name = service.get("name", "").lower()
                    service_category = service.get("category", "").lower()
                    
                    for word in search_words:
                        if len(word) > 2 and (word in service_name or word in service_category):
                            filtered_services.append(service)
                            break
        
        # Set a descriptive category name for the search
        context.user_data["selected_category"] = f"Search: {search_term}"
        
        # Store filtered services in context
        context.user_data["filtered_services"] = filtered_services
        context.user_data["current_page"] = 0
        
        logger.info(f"Search found {len(filtered_services)} services matching '{search_term}'")
        
        # If ID search found no results, inform the user specifically
        if is_id_search and not filtered_services:
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton(get_message(language, 'services', 'search_services'), callback_data="search_services")],
                [InlineKeyboardButton(get_message(language, 'services', 'back_to_categories'), callback_data="back_to_categories")]
            ])
            
            no_results_message = f"❌ <b>No service found with ID '{search_term}'</b>\n\n" + \
                               "Please check the ID and try again, or search by name."
            
            update.message.reply_html(
                no_results_message,
                reply_markup=keyboard
            )
            return SELECTING_SERVICE
        
        # Show search results for text searches
        if filtered_services:
            # Show the search results with prominent View All button
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton(f"👁️ View All {len(filtered_services)} Services", callback_data="view_search_results")],
                [InlineKeyboardButton(get_message(language, 'services', 'search_services'), callback_data="search_services")],
                [InlineKeyboardButton(get_message(language, 'services', 'back_to_categories'), callback_data="back_to_categories")]
            ])
            
            search_results_title = f"🔍 <b>Search Results for '{search_term}'</b>"
            message_text = f"{search_results_title}\n\n" + \
                           f"<i>Found {len(filtered_services)} matching services</i>\n\n" + \
                           f"Click below to view all matching services."
            
            update.message.reply_html(
                message_text,
                reply_markup=keyboard
            )
        else:
            # No results found
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton(get_message(language, 'services', 'search_services'), callback_data="search_services")],
                [InlineKeyboardButton(get_message(language, 'services', 'back_to_categories'), callback_data="back_to_categories")]
            ])
            
            # Text search with no results
            no_results_message = f"❌ <b>No services found matching '{search_term}'</b>\n\n" + \
                               "Try a different search term."
            
            update.message.reply_html(
                no_results_message,
                reply_markup=keyboard
            )
        
        return SELECTING_SERVICE
    except Exception as e:
        logger.error(f"Error processing search term: {e}", exc_info=True)
        error_text = get_message(language, 'services', 'error_search')
        update.message.reply_html(error_text)
        return SELECTING_SERVICE 