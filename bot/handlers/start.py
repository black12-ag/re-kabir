from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import CallbackContext, ConversationHandler, CommandHandler, CallbackQueryHandler
from utils.db import db
from utils.messages import get_message
import logging
import os
from utils.helpers import update_user_info, is_admin
import time
from utils.constants import CURRENCY_RATES

# Define states
SELECTING_LANGUAGE = 0

logger = logging.getLogger(__name__)

def show_main_menu(update: Update, context: CallbackContext, language=None, command_keyboard=None):
    """Helper function to show main menu with all available options"""
    user_id = update.effective_user.id
    
    if not language:
        language = db.get_language(user_id)
    
    logger.info(f"Showing main menu for user {user_id} in language: {language}")
    
    # Create main menu keyboard with all available buttons - without adding extra emojis
    keyboard = [
        [
            InlineKeyboardButton(get_message(language, 'main_menu', 'services'), callback_data="show_services"),
            InlineKeyboardButton(get_message(language, 'main_menu', 'recharge'), callback_data="recharge")
        ],
        [
            InlineKeyboardButton(get_message(language, 'main_menu', 'balance'), callback_data="show_balance"),
            InlineKeyboardButton(get_message(language, 'main_menu', 'order_status'), callback_data="check_status")
        ],
        [
            InlineKeyboardButton(get_message(language, 'main_menu', 'place_order'), callback_data="place_order"),
            InlineKeyboardButton(get_message(language, 'main_menu', 'help'), callback_data="help")
        ],
        [
            InlineKeyboardButton(get_message(language, 'main_menu', 'referrals'), callback_data="referrals"),
            InlineKeyboardButton(get_message(language, 'main_menu', 'languages'), callback_data="change_language")
        ],
        [
            InlineKeyboardButton(get_message(language, 'main_menu', 'support'), callback_data="support"),
            InlineKeyboardButton(get_message(language, 'main_menu', 'tutorial'), callback_data="tutorial")
        ]
    ]
    
    # Add admin button if user is admin
    if is_admin(user_id):
        keyboard.append([InlineKeyboardButton("🔧 Admin Panel", callback_data="admin")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Get user's balance information
    balance = db.get_balance(user_id)
    
    # Get ETB rate
    etb_rate = db.get_currency_rate("etb", CURRENCY_RATES.get("ETB", 30.0))
    
    # Calculate ETB balance
    etb_balance = balance * etb_rate
    formatted_etb = f"{etb_balance:,.0f}"
    formatted_usd = f"{balance:.2f}"
    
    # Create balance info text with formatted values
    balance_info = f"\n\n💰 <b>YOUR BALANCE:</b>\n🇺🇸 USD: <code>${formatted_usd}</code>\n🇪🇹 ETB: <code>ETB {formatted_etb}</code>\n"
    
    # Try to get custom welcome message from database
    welcome_message = get_message(language, 'welcome')
    logger.info(f"Loaded welcome message: {welcome_message[:30]}...")
    
    # Add balance info to welcome message
    welcome_message = welcome_message + balance_info
    
    # Send welcome message with buttons - simplified approach
    try:
        if update.callback_query:
            query = update.callback_query
            query.answer()
            query.edit_message_text(
                text=welcome_message,
                reply_markup=reply_markup,
                parse_mode=ParseMode.HTML
            )
            logger.info(f"Successfully displayed main menu via callback for user {user_id}")
        else:
            # For direct /start command, send a new message
            sent = update.message.reply_html(
                text=welcome_message,
                reply_markup=reply_markup
            )
            logger.info(f"Successfully displayed main menu via message for user {user_id}")
    except Exception as e:
        logger.error(f"Error sending welcome message: {e}")
        try:
            # Fallback to plain text if HTML parsing fails
            simple_message = "Welcome to our SMM services bot! Please select an option below:"
            if update.callback_query:
                update.callback_query.edit_message_text(
                    text=simple_message,
                    reply_markup=reply_markup
                )
            else:
                update.message.reply_text(
                    text=simple_message,
                    reply_markup=reply_markup
                )
            logger.info(f"Used fallback plain text menu for user {user_id}")
        except Exception as fallback_error:
            logger.error(f"Critical failure showing menu: {fallback_error}")
            # Extra fallback - try to send something, anything
            try:
                if update.message:
                    update.message.reply_text("Welcome! Use /services to browse available services.")
                elif update.callback_query:
                    update.callback_query.answer("Welcome! Use /services to browse available services.")
            except:
                pass

def start_command(update: Update, context: CallbackContext) -> int:
    """Handler for /start command"""
    user = update.effective_user
    user_id = user.id
    logger.info(f"Start command called by user {user_id}")
    
    # Check if this is a new user or an existing user
    is_new_user = False
    cursor = db.conn.cursor()
    cursor.execute('SELECT created_at FROM users WHERE user_id = ?', (user_id,))
    user_data = cursor.fetchone()
    
    if not user_data:
        # This is a new user
        is_new_user = True
        logger.info(f"New user {user_id} joined")
    
    # Ensure user exists in DB and get their language preference
    language = db.get_language(user_id)
    
    # Check if starting from a deep link with a referral
    args = context.args
    if args and len(args) > 0 and args[0].isdigit() and is_new_user:
        try:
            referrer_id = int(args[0])
            # Don't allow self-referrals
            if referrer_id != user_id:
                # Set the referred_by field in the user record
                cursor = db.conn.cursor()
                cursor.execute('UPDATE users SET referred_by = ? WHERE user_id = ?', (referrer_id, user_id))
                db.conn.commit()
                
                # Log the referral
                logger.info(f"User {user_id} was referred by {referrer_id}")
                
                # Notify the referring user (delayed to avoid API rate limits)
                try:
                    context.job_queue.run_once(
                        send_referral_notification,
                        5,  # 5 seconds delay
                        context={
                            'referrer_id': referrer_id, 
                            'new_user_id': user_id,
                            'language': db.get_language(referrer_id)
                        }
                    )
                except Exception as e:
                    logger.error(f"Error scheduling referral notification: {e}")
        except (ValueError, TypeError) as e:
            logger.error(f"Error processing referral: {e}")
    
    # Apply new user bonus if enabled
    if is_new_user:
        bonus_enabled = db.get_new_user_bonus_status()
        if bonus_enabled:
            bonus_amount = db.get_new_user_bonus_amount()
            bonus_currency = db.get_new_user_bonus_currency()
            username_required = db.get_new_user_bonus_username_required()
            
            # Check if username is required and if user has a username
            can_receive_bonus = True
            if username_required and not user.username:
                can_receive_bonus = False
                logger.info(f"User {user_id} does not have a username, no bonus applied")
            
            if bonus_amount > 0 and can_receive_bonus:
                # Add the bonus to the user's account - use the specific currency
                success = db.add_balance(
                    user_id, 
                    bonus_amount, 
                    f"New user welcome bonus", 
                    currency=bonus_currency,
                    silent=False
                )
                
                if success:
                    logger.info(f"Added welcome bonus of {bonus_amount} {bonus_currency} to user {user_id}")
                else:
                    logger.error(f"Failed to add welcome bonus to user {user_id}")
                
                # Notify the user about the bonus
                bonus_msg = get_message(language, 'new_user_bonus').format(
                    amount=bonus_amount,
                    currency=bonus_currency
                )
                try:
                    # Delay the bonus message to avoid API rate limits and ensure it's seen after the welcome message
                    context.job_queue.run_once(
                        send_delayed_message,
                        3,  # 3 seconds delay
                        context={
                            'chat_id': update.effective_chat.id,
                            'text': bonus_msg,
                            'parse_mode': 'HTML'
                        }
                    )
                except Exception as e:
                    logger.error(f"Error scheduling new user bonus message: {e}")
            elif username_required and not user.username and bonus_amount > 0:
                # Notify the user that they need a username to receive the bonus
                try:
                    username_notice = "🎁 <b>Welcome Bonus Available!</b>\n\nTo receive your welcome bonus, please set a username in your Telegram settings and restart the bot with /start."
                    context.job_queue.run_once(
                        send_delayed_message,
                        5,  # 5 seconds delay (after welcome message)
                        context={
                            'chat_id': update.effective_chat.id,
                            'text': username_notice,
                            'parse_mode': 'HTML'
                        }
                    )
                except Exception as e:
                    logger.error(f"Error scheduling username notice message: {e}")
    
    # Update user info in database
    db.update_user_info(user_id, user.username, user.first_name, user.last_name)
    
    # Check if this is a language change request
    if update.callback_query and update.callback_query.data == "change_language":
        current_language = db.get_language(user_id)
        
        # Create language selection keyboard
        keyboard = [
            [
                InlineKeyboardButton("🇺🇸 English (US)", callback_data="lang_en"),
                InlineKeyboardButton("🇬🇧 English (UK)", callback_data="lang_en_uk")
            ],
            [
                InlineKeyboardButton("🇪🇹 Amharic", callback_data="lang_am"),
                InlineKeyboardButton("🇸🇦 Arabic", callback_data="lang_ar")
            ],
            [
                InlineKeyboardButton("🇮🇳 Hindi", callback_data="lang_hi"),
                InlineKeyboardButton("🇪🇸 Spanish", callback_data="lang_es")
            ],
            [
                InlineKeyboardButton("🇨🇳 Chinese", callback_data="lang_zh"),
                InlineKeyboardButton("🇹🇷 Turkish", callback_data="lang_tr")
            ],
            [
                InlineKeyboardButton("◀️ Back to Main Menu", callback_data="back_to_main")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Send language selection message
        query = update.callback_query
        query.answer()
        query.edit_message_text(
            text=get_message(current_language, 'select_language'),
            reply_markup=reply_markup,
            parse_mode="HTML"
        )
        return SELECTING_LANGUAGE
    
    # Check if this is a referral link
    if update.message and context.args and len(context.args) > 0:
        try:
            referrer_id = int(context.args[0])
            
            # Don't allow self-referrals
            if referrer_id != user.id:
                # Record the referral
                success = db.add_referral(referrer_id, user.id)
                
                if success:
                    # Get referrer's language
                    referrer_language = db.get_language(referrer_id)
                    
                    # Notify the referrer
                    try:
                        context.bot.send_message(
                            chat_id=referrer_id,
                            text=get_message(referrer_language, 'referrals', 'new_referral'),
                            parse_mode="HTML"
                        )
                    except Exception as e:
                        logger.error(f"Error notifying referrer {referrer_id}: {e}")
                    
                    # Get user's language
                    language = db.get_language(user.id)
                    
                    # Notify the user
                    update.message.reply_html(
                        get_message(language, 'referrals', 'welcome_referred')
                    )
                    
                    logger.info(f"User {user.id} was referred by {referrer_id}")
        except (ValueError, Exception) as e:
            logger.error(f"Error processing referral: {e}")
    
    # For regular start command or back to main, always show the main menu directly
    if update.message:
        # Ensure we have the latest user info
        db.update_user_info(user_id, user.username, user.first_name, user.last_name)
        
        # Direct method: Show the main menu
        logger.info(f"Displaying main menu for user {user_id} via direct message")
        show_main_menu(update, context, language=language)
        
        # Apply command keyboard in a separate message
        try:
            # Import here to avoid circular imports
            from handlers.command_menu import get_command_keyboard
            reply_markup = get_command_keyboard(user.id)
            # Send a separate message with just the keyboard
            update.message.reply_text(
                "Use these commands for quick access:",
                reply_markup=reply_markup
            )
            context.user_data['command_menu_active'] = True
            logger.info(f"Applied command keyboard separately for user {user.id}")
        except Exception as e:
            logger.error(f"Error applying command keyboard: {e}")
            
    elif update.callback_query and update.callback_query.data == "back_to_main":
        # If returning to main menu from elsewhere
        logger.info(f"Displaying main menu for user {user_id} via callback")
        show_main_menu(update, context, language=language)
    
    return ConversationHandler.END

def language_callback(update: Update, context: CallbackContext):
    """Handle language selection callback"""
    query = update.callback_query
    query.answer()
    
    # Get selected language from callback data
    language = query.data.split('_')[1]
    logger.info(f"User {query.from_user.id} selected language: {language}")
    
    # Update user's language preference
    db.set_language(query.from_user.id, language)
    logger.info(f"Updated language preference for user {query.from_user.id} to {language}")
    
    # Verify the language was set correctly
    saved_language = db.get_language(query.from_user.id)
    logger.info(f"Verified language for user {query.from_user.id}: {saved_language}")
    
    # Show main menu in new language
    show_main_menu(update, context, language)
    return ConversationHandler.END

def referrals_command(update: Update, context: CallbackContext):
    """Handler for referrals command and callback"""
    user = update.effective_user
    db.update_user_activity(user.id)
    
    # Get user's language preference
    language = db.get_language(user.id)
    
    # Get bot username for creating referral link
    bot_username = context.bot.username
    
    # Create referral link
    referral_link = f"https://t.me/{bot_username}?start={user.id}"
    
    # Get referral count
    referral_count = db.get_referral_count(user.id)
    valid_referral_count = db.get_valid_referral_count(user.id)
    
    # Get referral settings
    referral_threshold_str = db.get_setting("referral_threshold", "50")
    # Ensure referral_threshold is an integer for calculations
    try:
        referral_threshold = int(referral_threshold_str)
    except (ValueError, TypeError):
        # Default to 50 if conversion fails
        referral_threshold = 50
        logger.warning(f"Failed to convert referral_threshold to integer. Using default value: {referral_threshold}")
    
    # Check for new referral bonuses
    bonus_result = db.check_and_create_referral_bonus(user.id)
    
    # If new bonus created, notify admin
    if bonus_result:
        try:
            # Get admin chat ID
            admin_chat_id = db.get_setting("admin_chat_id")
            
            if admin_chat_id:
                # Get user info for notification
                user_info = db.get_user(user.id)
                username = user_info.get('username', '')
                first_name = user_info.get('first_name', '')
                last_name = user_info.get('last_name', '')
                
                user_display = username or f"{first_name} {last_name}".strip() or f"User {user.id}"
                
                # Send notification to admin
                context.bot.send_message(
                    chat_id=admin_chat_id,
                    text=f"🎁 <b>New Referral Bonus Request</b>\n\n"
                         f"User: {user_display} (ID: {user.id})\n"
                         f"Referrals: {bonus_result['referral_threshold']}\n"
                         f"Bonus Amount: ETB {bonus_result['bonus_amount']:.2f}\n\n"
                         f"Use /admin to approve or decline this bonus.",
                    parse_mode="HTML"
                )
                logger.info(f"Notified admin about new referral bonus for user {user.id}")
        except Exception as e:
            logger.error(f"Error notifying admin about referral bonus: {e}")
    
    # Get pending bonuses
    pending_bonuses = db.get_pending_referral_bonuses(user.id)
    
    # Get all bonuses
    all_bonuses = db.get_all_referral_bonuses(user.id)
    
    # Create bonus info text
    bonus_text = ""
    if pending_bonuses:
        bonus_text += f"<b>🕒 Pending Bonuses:</b> {len(pending_bonuses)}\n"
    
    if all_bonuses:
        approved_bonuses = [b for b in all_bonuses if b['status'] == 'approved']
        if approved_bonuses:
            total_approved = sum(b['bonus_amount'] for b in approved_bonuses)
            bonus_text += f"<b>✅ Approved Bonuses:</b> {len(approved_bonuses)} (ETB {total_approved:.2f})\n"
    
    # Get the current bonus amount from settings
    bonus_amount = db.get_referral_bonus_amount()
    
    # Add bonus info if there are any bonuses
    if bonus_text:
        bonus_text = (
            f"<b>🎁 Referral Bonuses:</b>\n"
            f"{bonus_text}\n"
            f"<i>You earn ETB {bonus_amount:.2f} for every {referral_threshold} valid referrals!</i>\n\n"
        )
    else:
        # Show progress towards next bonus
        remaining = referral_threshold - (valid_referral_count % referral_threshold)
        bonus_text = (
            f"<b>🎁 Referral Bonuses:</b>\n"
            f"<b>⏳ Progress:</b> {valid_referral_count % referral_threshold}/{referral_threshold} valid referrals\n"
            f"<b>🎯 Next Bonus:</b> {remaining} more valid referrals needed\n\n"
            f"<i>You earn ETB {bonus_amount:.2f} for every {referral_threshold} valid referrals!</i>\n\n"
        )
    
    # Create message
    message = (
        f"🔗 <b>{get_message(language, 'referrals', 'title')}</b>\n\n"
        f"{get_message(language, 'referrals', 'description')}\n\n"
        f"<b>{get_message(language, 'referrals', 'your_link')}:</b>\n"
        f"<code>{referral_link}</code>\n\n"
        f"<b>{get_message(language, 'referrals', 'stats')}:</b>\n"
        f"👥 {get_message(language, 'referrals', 'total_referrals')}: <b>{referral_count}</b>\n"
        f"✅ Valid Referrals (with username): <b>{valid_referral_count}</b>\n"
        f"❌ Invalid Referrals (no username): <b>{referral_count - valid_referral_count}</b>\n\n"
        f"<i>Note: Only users with usernames count toward referral bonuses!</i>\n\n"
        f"{bonus_text}"
        f"{get_message(language, 'referrals', 'how_it_works')}"
    )
    
    # Create keyboard with share button, check referrals button, and back button
    keyboard = [
        [
            InlineKeyboardButton(get_message(language, 'referrals', 'share'), url=f"https://t.me/share/url?url={referral_link}&text={get_message(language, 'referrals', 'share_text')}")
        ],
        [
            InlineKeyboardButton("👤 " + get_message(language, 'referrals', 'check_referrals'), callback_data="check_referrals")
        ],
        [
            InlineKeyboardButton(get_message(language, 'referrals', 'back_to_menu'), callback_data="back_to_main")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Check if this is a callback query or direct command
    if update.callback_query:
        query = update.callback_query
        query.answer()
        query.edit_message_text(
            message,
            reply_markup=reply_markup,
            parse_mode="HTML",
            disable_web_page_preview=True
        )
    else:
        update.message.reply_html(
            message,
            reply_markup=reply_markup,
            disable_web_page_preview=True
        )
    
    return ConversationHandler.END

def check_referrals_callback(update: Update, context: CallbackContext):
    """Handler for check referrals button"""
    query = update.callback_query
    user = update.effective_user
    db.update_user_activity(user.id)
    
    # Get user's language preference
    language = db.get_language(user.id)
    
    # Get referrals
    referrals = db.get_referrals(user.id)
    
    # Get current page from callback data or default to page 1
    callback_data = query.data
    current_page = 1
    
    # Check if this is a page navigation callback
    if callback_data.startswith("ref_page_"):
        try:
            current_page = int(callback_data.split("_")[-1])
        except (ValueError, IndexError):
            current_page = 1
    
    if not referrals:
        # No referrals yet
        message = (
            f"👥 <b>{get_message(language, 'referrals', 'check_referrals')}</b>\n\n"
            f"{get_message(language, 'referrals', 'no_referrals')}"
        )
        
        # Create back button
        keyboard = [
            [
                InlineKeyboardButton(get_message(language, 'referrals', 'back_to_referrals'), callback_data="referrals")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
    else:
        # Pagination settings
        items_per_page = 25
        total_referrals = len(referrals)
        total_pages = (total_referrals + items_per_page - 1) // items_per_page  # Ceiling division
        
        # Ensure current page is valid
        if current_page < 1:
            current_page = 1
        elif current_page > total_pages:
            current_page = total_pages
        
        # Calculate start and end indices for the current page
        start_idx = (current_page - 1) * items_per_page
        end_idx = min(start_idx + items_per_page, total_referrals)
        
        # Get referrals for the current page
        page_referrals = referrals[start_idx:end_idx]
        
        # Count valid referrals (with username)
        valid_count = sum(1 for ref in referrals if ref.get('username'))
        
        # Format referrals list
        referrals_list = ""
        for i, referral in enumerate(page_referrals, start_idx + 1):
            # Format date
            created_at = referral.get('created_at', '')
            if created_at:
                try:
                    # Try to parse the date string
                    if isinstance(created_at, str):
                        from datetime import datetime
                        created_at = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
                    # Format as a readable date
                    date_str = created_at.strftime('%Y-%m-%d %H:%M')
                except Exception as e:
                    logger.error(f"Error formatting date: {e}")
                    date_str = str(created_at)
            else:
                date_str = "Unknown date"
            
            # Get user info
            username = referral.get('username', '')
            first_name = referral.get('first_name', '')
            last_name = referral.get('last_name', '')
            user_id = referral.get('user_id', 'Unknown')
            
            # Format user display name with status indicator
            if username:
                user_display = f"✅ @{username}"  # Valid referral with username
            elif first_name or last_name:
                user_display = f"❌ {first_name} {last_name}".strip()  # No username
            else:
                user_display = f"❌ User {user_id}"  # No username
            
            # Add to list
            referrals_list += f"{i}. {user_display} - {date_str}\n"
        
        # Create pagination buttons
        pagination_buttons = []
        
        # Add Previous button if not on first page
        if current_page > 1:
            pagination_buttons.append(
                InlineKeyboardButton("⬅️ Previous", callback_data=f"ref_page_{current_page - 1}")
            )
        
        # Add page indicator
        pagination_buttons.append(
            InlineKeyboardButton(f"Page {current_page}/{total_pages}", callback_data="do_nothing")
        )
        
        # Add Next button if not on last page
        if current_page < total_pages:
            pagination_buttons.append(
                InlineKeyboardButton("Next ➡️", callback_data=f"ref_page_{current_page + 1}")
            )
        
        # Create message with pagination info
        message = (
            f"👥 <b>{get_message(language, 'referrals', 'check_referrals')}</b>\n\n"
            f"<b>Total Referrals:</b> {total_referrals}\n"
            f"<b>Valid Referrals (with username):</b> {valid_count}\n"
            f"<b>Invalid Referrals (no username):</b> {total_referrals - valid_count}\n\n"
            f"{get_message(language, 'referrals', 'referrals_list')}:\n"
            f"<i>Showing {start_idx + 1}-{end_idx} of {total_referrals} referrals</i>\n\n"
            f"{referrals_list}"
        )
        
        # Create keyboard with pagination and back button
        keyboard = []
        
        # Add pagination row if there are multiple pages
        if total_pages > 1:
            keyboard.append(pagination_buttons)
        
        # Add back button
        keyboard.append([
            InlineKeyboardButton(get_message(language, 'referrals', 'back_to_referrals'), callback_data="referrals")
        ])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Send message
    query.answer()
    query.edit_message_text(
        message,
        reply_markup=reply_markup,
        parse_mode="HTML"
    )
    
    return ConversationHandler.END

def send_delayed_message(context: CallbackContext):
    """Send a delayed message (used for new user bonus notifications)"""
    job = context.job
    chat_id = job.context.get('chat_id')
    text = job.context.get('text')
    parse_mode = job.context.get('parse_mode', None)
    
    try:
        context.bot.send_message(
            chat_id=chat_id,
            text=text,
            parse_mode=parse_mode
        )
    except Exception as e:
        logger.error(f"Error sending delayed message: {e}")

# Create conversation handler for language selection
language_conv_handler = ConversationHandler(
    entry_points=[
        CommandHandler('start', start_command),
        CallbackQueryHandler(start_command, pattern=r'^change_language$')
    ],
    states={
        SELECTING_LANGUAGE: [
            CallbackQueryHandler(language_callback, pattern=r'^lang_'),
            CallbackQueryHandler(start_command, pattern=r'^back_to_main$')
        ]
    },
    fallbacks=[
        CommandHandler('start', start_command),
        CallbackQueryHandler(start_command, pattern=r'^back_to_main$')
    ],
    allow_reentry=True
) 