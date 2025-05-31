from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from utils.db import db
import logging
import os
from utils.messages import get_message
from utils.helpers import is_admin

# Define conversation states
WAITING_FOR_MESSAGE = 1

# Module logger
logger = logging.getLogger(__name__)

def support_command(update: Update, context: CallbackContext):
    """Handler for /support command or support button"""
    user = update.effective_user
    db.update_user_activity(user.id)
    
    # Get user's language preference
    language = db.get_language(user.id)
    
    # Get admin username from environment variable
    admin_username = os.getenv("ADMIN_USERNAME", "admin")  # Use the existing ADMIN_USERNAME from env
    
    # Ensure the admin username starts with @
    if not admin_username.startswith('@'):
        admin_username = f'@{admin_username}'
    
    # Create support message
    message = (
        f"{get_message(language, 'support', 'title')}\n\n"
        f"{get_message(language, 'support', 'description')}"
    )
    
    # Create keyboard with start chat (now linking to admin) and back to menu buttons
    keyboard = [
        [InlineKeyboardButton(get_message(language, 'support', 'start_chat'), url=f"https://t.me/{admin_username.replace('@', '')}")],
        [InlineKeyboardButton(get_message(language, 'support', 'back_to_menu'), callback_data="back_to_main")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Send message
    if update.callback_query:
        query = update.callback_query
        query.answer()
        query.edit_message_text(
            text=message,
            reply_markup=reply_markup,
            parse_mode="HTML"
        )
    else:
        update.message.reply_html(
            text=message,
            reply_markup=reply_markup
        )
    
    return ConversationHandler.END

def start_support_chat(update: Update, context: CallbackContext):
    """Start a support chat session"""
    query = update.callback_query
    user = update.effective_user
    
    # Get user's language
    language = db.get_language(user.id)
    
    # Answer the callback query
    query.answer()
    
    # Create message
    message = get_message(language, 'support', 'chat_started')
    
    # Create keyboard with cancel button
    keyboard = [[InlineKeyboardButton(get_message(language, 'support', 'end_chat'), callback_data="cancel_support_chat")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Edit message
    query.edit_message_text(
        text=message,
        reply_markup=reply_markup,
        parse_mode="HTML"
    )
    
    # Set user state
    context.user_data["support_chat_active"] = True
    
    # Reset admin reply flag
    context.user_data["admin_has_replied"] = False
    
    # Reset first message flag
    context.user_data["first_message_sent"] = False
    
    return WAITING_FOR_MESSAGE

def handle_support_message(update: Update, context: CallbackContext):
    """Handle user message in support chat"""
    user = update.effective_user
    
    # Check if user is in support chat
    if not context.user_data.get("support_chat_active", False):
        return
    
    # Get admin IDs from environment
    admin_ids_str = os.getenv("ADMIN_USER_ID", "")
    admin_ids = [id.strip() for id in admin_ids_str.split(",")]
    
    if not admin_ids:
        logger.error("Admin IDs not found in environment variables")
        update.message.reply_html(
            "❌ <b>Error</b>\n\nUnable to send message to support. Please try again later."
        )
        return ConversationHandler.END
    
    try:
        # Get user's language
        language = db.get_language(user.id)
        
        # Format user info with more details
        username = user.username
        first_name = user.first_name or ""
        last_name = user.last_name or ""
        full_name = f"{first_name} {last_name}".strip()
        
        # Create detailed user info
        if username:
            user_info = f"@{username}"
            detailed_user_info = f"@{username} ({full_name})" if full_name else f"@{username}"
        else:
            user_info = full_name if full_name else f"User {user.id}"
            detailed_user_info = full_name if full_name else f"User {user.id}"
        
        # Add user ID to detailed info
        detailed_user_info = f"{detailed_user_info}\nID: <code>{user.id}</code>"
        
        # Determine message type and forward to admin
        if update.message.text:
            # Text message
            message_text = update.message.text
            
            # Send message to admins
            for admin_id in admin_ids:
                context.bot.send_message(
                    chat_id=admin_id,
                    text=get_message(language, 'support', 'admin_notification').format(
                        user_info=detailed_user_info,
                        user_id=user.id,
                        message=message_text
                    ),
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton(f"📝 Reply to {user_info}", callback_data=f"reply_to_user_{user.id}")]
                    ])
                )
        elif update.message.photo:
            # Photo message
            photo = update.message.photo[-1]  # Get the largest photo
            caption = update.message.caption or ""
            
            # Send photo to admins
            for admin_id in admin_ids:
                context.bot.send_photo(
                    chat_id=admin_id,
                    photo=photo.file_id,
                    caption=f"📩 <b>Photo from user:</b>\n\nFrom: {detailed_user_info}\n\n<b>Caption:</b>\n{caption}",
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton(f"📝 Reply to {user_info}", callback_data=f"reply_to_user_{user.id}")]
                    ])
                )
        elif update.message.video:
            # Video message
            video = update.message.video
            caption = update.message.caption or ""
            
            # Send video to admins
            for admin_id in admin_ids:
                context.bot.send_video(
                    chat_id=admin_id,
                    video=video.file_id,
                    caption=f"📩 <b>Video from user:</b>\n\nFrom: {detailed_user_info}\n\n<b>Caption:</b>\n{caption}",
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton(f"📝 Reply to {user_info}", callback_data=f"reply_to_user_{user.id}")]
                    ])
                )
        elif update.message.document:
            # Document message
            document = update.message.document
            caption = update.message.caption or ""
            
            # Send document to admins
            for admin_id in admin_ids:
                context.bot.send_document(
                    chat_id=admin_id,
                    document=document.file_id,
                    caption=f"📩 <b>Document from user:</b>\n\nFrom: {detailed_user_info}\n\n<b>Caption:</b>\n{caption}",
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton(f"📝 Reply to {user_info}", callback_data=f"reply_to_user_{user.id}")]
                    ])
                )
        elif update.message.voice:
            # Voice message
            voice = update.message.voice
            
            # Send voice to admins
            for admin_id in admin_ids:
                context.bot.send_voice(
                    chat_id=admin_id,
                    voice=voice.file_id,
                    caption=f"📩 <b>Voice message from user:</b>\n\nFrom: {detailed_user_info}",
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton(f"📝 Reply to {user_info}", callback_data=f"reply_to_user_{user.id}")]
                    ])
                )
        elif update.message.audio:
            # Audio message
            audio = update.message.audio
            caption = update.message.caption or ""
            
            # Send audio to admins
            for admin_id in admin_ids:
                context.bot.send_audio(
                    chat_id=admin_id,
                    audio=audio.file_id,
                    caption=f"📩 <b>Audio from user:</b>\n\nFrom: {detailed_user_info}\n\n<b>Caption:</b>\n{caption}",
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton(f"📝 Reply to {user_info}", callback_data=f"reply_to_user_{user.id}")]
                    ])
                )
        else:
            # Unsupported message type
            for admin_id in admin_ids:
                context.bot.send_message(
                    chat_id=admin_id,
                    text=f"📩 <b>Unsupported message type from user:</b>\n\nFrom: {detailed_user_info}\n\n<i>The user sent a message type that is not supported by the bot.</i>",
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton(f"📝 Reply to {user_info}", callback_data=f"reply_to_user_{user.id}")]
                    ])
                )
        
        # Check if this is the first message or if admin has not replied yet
        admin_replied = context.user_data.get("admin_has_replied", False)
        
        if not admin_replied:
            # For first message, show "message sent" confirmation
            if not context.user_data.get("first_message_sent", False):
                # Create keyboard with cancel button
                keyboard = [[InlineKeyboardButton(get_message(language, 'support', 'end_chat'), callback_data="cancel_support_chat")]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                update.message.reply_html(
                    get_message(language, 'support', 'message_sent'),
                    reply_markup=reply_markup
                )
                # Mark that first message has been sent
                context.user_data["first_message_sent"] = True
            else:
                # For subsequent messages before admin reply, show "waiting" message
                # Create keyboard with cancel button
                keyboard = [[InlineKeyboardButton(get_message(language, 'support', 'end_chat'), callback_data="cancel_support_chat")]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                update.message.reply_html(
                    get_message(language, 'support', 'waiting_for_reply'),
                    reply_markup=reply_markup
                )
        # No else needed - for messages after admin reply, we don't send any confirmation
        
        # Log the message
        logger.info(f"Support message from user {user.id} ({user_info}) sent to admins")
        
    except Exception as e:
        logger.error(f"Error sending support message to admins: {e}")
        update.message.reply_html(
            "❌ <b>Error</b>\n\nUnable to send message to support. Please try again later."
        )
    
    return WAITING_FOR_MESSAGE

def cancel_support_chat(update: Update, context: CallbackContext):
    """Cancel support chat"""
    query = update.callback_query
    user = update.effective_user
    
    # Get user's language
    language = db.get_language(user.id)
    
    query.answer()
    
    # Clear support chat state
    context.user_data["support_chat_active"] = False
    
    # Notify user that chat has ended
    query.edit_message_text(
        text=get_message(language, 'support', 'chat_ended'),
        parse_mode="HTML"
    )
    
    # Return to main menu
    from handlers.start import start_command
    return start_command(update, context)

def reply_to_user(update: Update, context: CallbackContext):
    """Admin initiating reply to user"""
    query = update.callback_query
    admin = update.effective_user
    
    # Check if user is admin
    if not is_admin(admin.id):
        query.answer("You don't have permission to use this feature.")
        return ConversationHandler.END
    
    # Get user ID from callback data
    callback_data = query.data
    try:
        user_id = int(callback_data.split("_")[-1])
    except (ValueError, IndexError):
        query.answer("Invalid user ID")
        return ConversationHandler.END
    
    # Get user info from database
    user_info = db.get_user(user_id)
    
    # Format display name
    username = user_info.get("username") if user_info else None
    first_name = user_info.get("first_name", "") if user_info else ""
    last_name = user_info.get("last_name", "") if user_info else ""
    full_name = f"{first_name} {last_name}".strip() if first_name or last_name else ""
    
    # Create display name with username if available
    if username:
        display_name = f"@{username}"
        detailed_display_name = f"@{username}"
        if full_name:
            detailed_display_name += f" ({full_name})"
    else:
        display_name = full_name if full_name else f"User {user_id}"
        detailed_display_name = display_name
    
    # Add user ID to detailed display name
    detailed_display_name = f"{detailed_display_name}\nID: <code>{user_id}</code>"
    
    # Store user ID and display name in context for later use
    context.user_data["reply_to_user_id"] = user_id
    context.user_data["reply_to_user_name"] = display_name
    
    # Answer callback query
    query.answer()
    
    # Prompt admin for reply
    query.edit_message_text(
        f"📝 <b>Reply to User</b>\n\n"
        f"You are replying to: <b>{detailed_display_name}</b>\n\n"
        f"<i>Type your reply message and send it.</i>",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("❌ Cancel", callback_data="cancel_admin_reply")]
        ])
    )
    
    # Set admin state
    context.user_data["admin_replying"] = True
    
    return WAITING_FOR_MESSAGE

def handle_admin_reply(update: Update, context: CallbackContext):
    """Handle admin reply to user"""
    admin = update.effective_user
    
    # Check if admin is in reply mode
    if not context.user_data.get("admin_replying", False):
        return
    
    # Get user ID to reply to
    user_id = context.user_data.get("reply_to_user_id")
    if not user_id:
        update.message.reply_text("Error: No user to reply to.")
        return ConversationHandler.END
    
    # Get user's display name
    user_display_name = context.user_data.get("reply_to_user_name", f"User {user_id}")
    
    # Get user's language
    language = db.get_language(int(user_id))
    
    # Create reply header
    reply_header = get_message(language, 'support', 'admin_reply_header')
    
    try:
        # Determine message type and send to user
        if update.message.text:
            # Text message
            message_text = update.message.text
            
            # Send message to user
            context.bot.send_message(
                chat_id=user_id,
                text=f"{reply_header}\n\n{message_text}",
                parse_mode="HTML"
            )
        elif update.message.photo:
            # Photo message
            photo = update.message.photo[-1]  # Get the largest photo
            caption = update.message.caption or ""
            
            # Send photo to user
            context.bot.send_photo(
                chat_id=user_id,
                photo=photo.file_id,
                caption=f"{reply_header}\n\n{caption}",
                parse_mode="HTML"
            )
        elif update.message.video:
            # Video message
            video = update.message.video
            caption = update.message.caption or ""
            
            # Send video to user
            context.bot.send_video(
                chat_id=user_id,
                video=video.file_id,
                caption=f"{reply_header}\n\n{caption}",
                parse_mode="HTML"
            )
        elif update.message.document:
            # Document message
            document = update.message.document
            caption = update.message.caption or ""
            
            # Send document to user
            context.bot.send_document(
                chat_id=user_id,
                document=document.file_id,
                caption=f"{reply_header}\n\n{caption}",
                parse_mode="HTML"
            )
        elif update.message.voice:
            # Voice message
            voice = update.message.voice
            
            # Send voice to user
            context.bot.send_voice(
                chat_id=user_id,
                voice=voice.file_id,
                caption=f"{reply_header}",
                parse_mode="HTML"
            )
        elif update.message.audio:
            # Audio message
            audio = update.message.audio
            caption = update.message.caption or ""
            
            # Send audio to user
            context.bot.send_audio(
                chat_id=user_id,
                audio=audio.file_id,
                caption=f"{reply_header}\n\n{caption}",
                parse_mode="HTML"
            )
        else:
            # Unsupported message type
            update.message.reply_html(
                "❌ <b>Error</b>\n\nThis message type is not supported."
            )
            return WAITING_FOR_MESSAGE
        
        # Mark that admin has replied to this user
        try:
            # Try to update user data in the database
            # We'll add a column for admin_has_replied if needed
            db.update_user_data(int(user_id), {"admin_has_replied": 1})
            
            # Also try to store in user_data dictionary as a backup
            try:
                user_data = context.dispatcher.user_data.get(int(user_id), {})
                
                # Check if this is the first admin reply
                if not user_data.get("admin_has_replied", False):
                    user_data["admin_has_replied"] = True
                    context.dispatcher.user_data[int(user_id)] = user_data
                    
                    # Send notification to user that admin has joined the chat (only once)
                    context.bot.send_message(
                        chat_id=int(user_id),
                        text=get_message(language, 'support', 'admin_has_replied'),
                        parse_mode="HTML",
                        reply_markup=InlineKeyboardMarkup([
                            [InlineKeyboardButton(get_message(language, 'support', 'end_chat'), callback_data="cancel_support_chat")]
                        ])
                    )
            except Exception as e:
                logger.warning(f"Could not set admin_has_replied in user_data: {e}")
        except Exception as e:
            logger.warning(f"Could not set admin_has_replied flag: {e}")
            # Continue anyway as the message was sent
        
        # Confirm to admin
        update.message.reply_html(
            f"✅ Your reply has been sent to {user_display_name}."
        )
        
        # Log the reply
        logger.info(f"Admin {admin.id} replied to user {user_id} ({user_display_name})")
        
        # Set flag in user_data that admin has replied
        context.user_data["admin_has_replied"] = True
        
        # Clear admin reply state
        context.user_data["admin_replying"] = False
        context.user_data["reply_to_user_id"] = None
        context.user_data["reply_to_user_name"] = None
        
        return ConversationHandler.END
        
    except Exception as e:
        logger.error(f"Error sending admin reply to user: {e}")
        update.message.reply_html(
            "❌ <b>Error</b>\n\nUnable to send reply to user. Please try again later."
        )
        return WAITING_FOR_MESSAGE

def cancel_admin_reply(update: Update, context: CallbackContext):
    """Cancel admin reply"""
    query = update.callback_query
    query.answer()
    
    # Clear admin reply state
    context.user_data["admin_replying"] = False
    context.user_data["reply_to_user_id"] = None
    context.user_data["reply_to_user_name"] = None
    
    # Show cancellation message
    query.edit_message_text(
        "❌ Reply cancelled.",
        parse_mode="HTML"
    )
    
    return ConversationHandler.END

# Create conversation handler for support chat
support_conv_handler = ConversationHandler(
    entry_points=[
        CommandHandler("support", support_command),
        CallbackQueryHandler(support_command, pattern=r"^support$")
    ],
    states={},
    fallbacks=[
        CommandHandler("start", lambda update, context: ConversationHandler.END),
        CommandHandler("cancel", lambda update, context: ConversationHandler.END),
    ],
    allow_reentry=True
)

# Create conversation handler for admin replies
admin_reply_conv_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(reply_to_user, pattern=r"^reply_to_user_\d+$")
    ],
    states={
        WAITING_FOR_MESSAGE: [
            MessageHandler(Filters.text & ~Filters.command, handle_admin_reply),
            MessageHandler(Filters.photo, handle_admin_reply),
            MessageHandler(Filters.video, handle_admin_reply),
            MessageHandler(Filters.document, handle_admin_reply),
            MessageHandler(Filters.voice, handle_admin_reply),
            MessageHandler(Filters.audio, handle_admin_reply),
            CallbackQueryHandler(cancel_admin_reply, pattern=r"^cancel_admin_reply$")
        ]
    },
    fallbacks=[
        CallbackQueryHandler(cancel_admin_reply, pattern=r"^cancel_admin_reply$")
    ],
    allow_reentry=True
) 