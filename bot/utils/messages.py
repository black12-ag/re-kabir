import logging

logger = logging.getLogger(__name__)

# Language-specific messages for the bot

MESSAGES = {
    'en': {  # English (US)
        'welcome': (
            "🌉 Welcome to KabirBridge!\n\n"
            "Your gateway to quick and efficient online services.\n\n"
            "✅ How to Use:\n"
            "1️⃣ Tap Services to browse available options.\n"
            "2️⃣ Select your desired service and follow the process.\n"
            "3️⃣ Complete your order and let the bot do the rest!\n\n"
            "💵 Payments: Safe and convenient payment options.\n"
            "📞 Support: +251907806267, @muay011\n\n"
            "🔹 Start now and experience instant results!"
        ),
        'select_language': "🌐 Please select your preferred language:",
        'language_changed': "✅ Language has been changed successfully!",
        'main_menu': {
            'services': "🛒 Services",
            'place_order': "📦 Place Order",
            'balance': "💰 Balance",
            'order_status': "📊 Order Status",
            'recharge': "💳 Recharge",
            'help': "❓ Help",
            'languages': "🌐 Languages",
            'referrals': "👥 Referrals",
            'support': "Customer Support",
            'tutorial': "📚 Tutorials"
        },
        'balance': {
            'title': "💰 <b>Your Balance</b>",
            'current_balance_usd': "Current Balance: <code>${balance:.2f}</code>",
            'current_balance_etb': "Current Balance: <code>ETB {formatted_etb}</code> (≈${balance:.2f})",
            'recent_transactions': "📝 <b>Recent Transactions:</b>",
            'no_transactions': "No recent transactions found.",
            'add_balance_note': "To add balance, please contact the administrator.",
            'refresh_button': "🔄 Refresh",
            'refreshed': "Balance refreshed",
            'up_to_date': "Balance is up to date",
            'error_message': "❌ An error occurred while fetching your balance. Please try again later.",
            'error_refresh': "❌ An error occurred while refreshing your balance. Please try again later."
        },
        'status': {
            'title': "📦 <b>Check Order Status</b>",
            'enter_order_id': "Please enter the order ID you want to check.\nExample: <code>1234567</code>\n\nOr click the button below to see your recent order IDs:",
            'show_order_ids': "📋 Show My Order IDs",
            'back_to_main': "◀️ Back to Main Menu",
            'no_orders': "You don't have any orders yet. Use /services to browse available services and place an order.",
            'your_order_ids': "📋 <b>Your Order IDs</b>\n\nCopy any ID and send it to check its status:",
            'back': "◀️ Back",
            'order_status': "📦 <b>Order Status</b>",
            'order_id': "🔢 Order ID: <code>{order_id}</code>",
            'service': "🛍️ Service: {service_name}",
            'quantity': "🔢 Quantity: {quantity}",
            'status': "📊 Status: {status}",
            'price': "💰 Price: ${price:.6f} / ETB {etb_price:.2f}",
            'start_count': "⏳ Start Count: {start_count}",
            'remains': "⌛ Remains: {remains}",
            'refresh': "🔄 Refresh",
            'status_up_to_date': "Status is already up to date!",
            'error_updating': "Error updating status",
            'order_not_found': "⚠️ Order not found or not accessible",
            'error_checking': "⚠️ An error occurred while checking the order status: {error}"
        },
        'recharge': {
            'title': "💳 <b>Recharge Account</b>",
            'select_payment_method': "Please select your preferred payment method:",
            'select_amount': "Please select the amount you want to recharge:\n\nChoose from preset amounts or click 'Custom Amount' to enter your own.",
            'custom_amount_usd': "💰 Please enter the amount you want to recharge (in USD):\nExample: <code>50</code> for $50",
            'custom_amount_etb': "💰 Please enter the amount you want to recharge (in ETB):\nExample: <code>1000</code> for ETB 1000",
            'minimum_amount_usd': "❌ Please enter a valid amount greater than $1.",
            'minimum_amount_etb': "❌ Minimum recharge amount for Ethiopian banks is <b>ETB 100</b>.\nPlease enter a higher amount.",
            'invalid_amount': "❌ Please enter a valid number.\nExample: <code>500</code> for {currency}500",
            'payment_verified': "✅ <b>Payment Verified!</b>\n\nYour payment of <code>${amount:.2f}</code> has been verified.\nThe amount has been added to your balance.\n\nUse /account to check your updated balance.",
            'payment_verified_etb': "✅ <b>Payment Verified!</b>\n\nYour payment of <code>ETB {formatted_etb}</code> (≈${amount:.2f}) has been verified.\nThe amount has been added to your balance.\n\nYour balance will now be displayed in ETB.\n\nUse /account to check your updated balance.",
            'payment_rejected': "❌ <b>Payment Rejected</b>\n\nYour payment of <code>${amount:.2f}</code> was not verified.\nPlease contact {admin_username} for more information.\n\nUse /recharge to try again.",
            'cancelled': "❌ Recharge cancelled. Use /recharge to start again.",
            'custom_amount': "💰 Custom Amount",
            'back': "🔙 Back",
            'cancel': "❌ Cancel",
            'wise': "🌐 Wise (International)",
            'eth_banks': "🏦 Ethiopian Banks",
            'intl_options': "🌍 Other International Options",
            'crypto': "₿ Cryptocurrency"
        },
        'services': {
            'platforms_title': "📱 <b>Service Platforms</b>",
            'platforms_description': "Please select a platform, search for services, or view all services:",
            'all_services': "🔍 All Services",
            'search_services': "🔎 Search Services",
            'platform_button': "📱 {platform} ({count})",
            'error_retrieving': "Error retrieving services. Please try again later.",
            'categories_title': "📂 <b>Categories</b> - {platform}",
            'categories_description': "Please select a category:",
            'all_categories': "📂 All Categories",
            'back_to_platforms': "⬅️ Back to Platforms",
            'services_title': "📋 <b>Services</b> - {category}",
            'services_page_info': " (Page {current_page}/{total_pages})",
            'services_description': "Select a service to place an order:",
            'back_to_categories': "⬅️ Back",
            'search_title': "🔍 <b>Search Services</b>",
            'search_description': "Please enter a search term to find services by name:",
            'search_results': "🔍 <b>Search Results</b> - {term}",
            'no_results': "No services found matching your search term. Please try again.",
            'service_details': "📋 <b>Service Details</b>",
            'service_id': "🆔 Service ID: <code>{id}</code>",
            'service_name': "📝 Name: {name}",
            'service_category': "📂 Category: {category}",
            'service_rate': "💰 Rate: ${rate} per 1000",
            'service_min': "⬇️ Min: {min}",
            'service_max': "⬆️ Max: {max}",
            'service_description': "📄 Description: {description}",
            'place_order': "🛒 Place Order",
            'back_to_services': "🔙 Back to Services",
            'error_service_details': "Error showing service details. Please try again.",
            'error_search': "Error initiating search. Please try again.",
            'error_display': "Error displaying services. Please try again."
        },
        'order': {
            'processing': "⏳ <b>Processing Order...</b>\n\nYour order is being placed on the website. Please wait...",
            'success': "✅ <b>Order Placed Successfully!{admin_note}</b>\n\nOrder ID: <code>{order_id}</code>\nService: {service_name}\nQuantity: {quantity}\nPrice: {price_display}\n\nYour order has been submitted to the website and is being processed.\nYou can check the status of your order with /status command.",
            'failed': "❌ <b>Order Failed</b>\n\nError: {error_message}\n\nYour order could not be placed on the website. Please try again later or contact support.",
            'error': "❌ <b>Order Failed</b>\n\nAn unexpected error occurred: {error}\n\nPlease try again later or contact support.",
            'quantity_set': "✅ Quantity set to: {quantity}\n\nPlease provide a link or username:",
            'invalid_quantity': "⚠️ Please enter a valid number for quantity.",
            'insufficient_balance': "❌ <b>Insufficient Balance</b>\n\nRequired: ${price:.6f} / ETB {etb_price:.2f}\nYour balance: ${user_balance:.6f} / ETB {etb_balance:.2f}\n\nPlease add funds to your account before placing the order.",
            'enter_link': "Please send the link to the post/profile you want to boost:",
            'select_service_first': "Please select a service first using the Services button or /services command.",
            'order_summary': "📋 <b>Order Summary</b>\n\nService: {service_name}\nLink: {link}\nQuantity: {quantity}\nPrice: {price_display}\n\nPlease confirm your order:",
            'min_quantity': "⚠️ Minimum quantity for this service is {min_quantity}. Please enter a higher quantity.",
            'max_quantity': "⚠️ Maximum quantity for this service is {max_quantity}. Please enter a lower quantity.",
            'order_quantity': "📊 <b>Order Quantity</b>",
            'please_select_quantity': "Please select the quantity you want to order:"
        },
        'help': {
            'title': "❓ <b>Help & Support</b>",
            'description': "If you need assistance or have any questions, please contact our support team.",
            'contact_admin': "📞 Contact Admin",
            'back_to_menu': "◀️ Back to Main Menu",
            'contact_support': "💬 Contact Support"
        },
        'referrals': {
            'title': "Referral Program",
            'description': "Invite your friends to join our service and earn rewards! Share your unique referral link with friends and earn a commission when they make purchases.",
            'your_link': "Your Referral Link",
            'stats': "Your Referral Stats",
            'total_referrals': "Total Referrals",
            'how_it_works': "How it works:\n1. Share your referral link with friends\n2. When they join using your link, they'll be counted as your referral\n3. You'll receive notifications when someone joins using your link",
            'share': "📤 Share Your Link",
            'share_text': "Join me on this amazing SMM Panel Bot! Use my referral link:",
            'back_to_menu': "◀️ Back to Main Menu",
            'new_referral': "🎉 <b>New Referral!</b>\n\nSomeone just joined using your referral link!",
            'welcome_referred': "👋 <b>Welcome!</b>\n\nYou've joined through a referral link. Enjoy our services!",
            'check_referrals': "Check My Referrals",
            'no_referrals': "You don't have any referrals yet. Share your referral link with friends to get started!",
            'referrals_list': "Here are the users who joined using your referral link",
            'back_to_referrals': "◀️ Back to Referrals"
        },
        'support': {
            'title': "💬 <b>Customer Support</b>",
            'description': "Need help? You can send a message directly to our support team. We'll get back to you as soon as possible.",
            'start_chat': "📝 Start Support Chat",
            'back_to_menu': "◀️ Back to Main Menu",
            'chat_started': "✅ <b>Support chat started!</b>\n\nPlease type your message below. Our team will respond as soon as possible.",
            'message_sent': "✅ Your message has been sent to our support team. We'll respond as soon as possible.",
            'chat_ended': "✅ Support chat has ended. If you need further assistance, you can start a new chat anytime.",
            'admin_notification': "📩 <b>New support message from user:</b>\n\nFrom: {user_info}\n\n<b>Message:</b>\n{message}",
            'reply_prompt': "✍️ Please type your reply to the user:",
            'reply_sent': "✅ Your reply has been sent to the user.",
            'reply_from_admin': "📩 <b>Reply from support team:</b>\n\n{message}",
            'admin_reply_header': "📩 <b>Reply from support team:</b>",
            'admin_has_replied': "✅ A support team member has joined the chat. You can continue your conversation.",
            'no_permission': "❌ You don't have permission to use this command.",
            'waiting_for_reply': "⏳ Please wait for our support team to respond to your message.",
            'end_chat': "❌ End Chat"
        },
        'tutorial': {
            'title': "📚 <b>Tutorials</b>",
            'select_tutorial': "Select a tutorial to learn how to use different features of the bot:",
            'back_to_tutorials': "◀️ Back to Tutorials",
            'back_to_menu': "🏠 Main Menu",
            'admin_manage': "🔧 Admin: Manage Tutorials",
            'edit_text': "✏️ Edit Text",
            'add_media': "🖼️ Add Media",
            'delete_media': "🗑️ Delete Media",
            'no_content': "This tutorial is currently being updated. Please check back later."
        },
        'new_user_bonus': "🎁 <b>Welcome Bonus!</b>\n\nAs a new user, you have received a bonus of {amount} {currency}!\n\nYou can check your balance with /balance"
    },
    'en_uk': {  # English (UK)
        'welcome': (
            "🌉 Welcome to KabirBridge!\n\n"
            "Your gateway to quick and efficient online services.\n\n"
            "✅ How to Use:\n"
            "1️⃣ Tap Services to browse available options.\n"
            "2️⃣ Select your desired service and follow the process.\n"
            "3️⃣ Complete your order and let the bot do the rest!\n\n"
            "💵 Payments: Safe and convenient payment options.\n"
            "📞 Support: +251907806267, @muay011\n\n"
            "🔹 Start now and experience instant results!"
        ),
        'select_language': "🌐 Please select your preferred language:",
        'language_changed': "✅ Language has been changed successfully!",
        'main_menu': {
            'services': "🛒 Services",
            'place_order': "📦 Place Order",
            'balance': "💰 Balance",
            'order_status': "📊 Order Status",
            'recharge': "💳 Recharge",
            'help': "❓ Help",
            'languages': "🌐 Languages",
            'referrals': "👥 Referrals"
        },
        'balance': {
            'title': "💰 <b>Your Balance</b>",
            'current_balance_usd': "Current Balance: <code>${balance:.2f}</code>",
            'current_balance_etb': "Current Balance: <code>ETB {formatted_etb}</code> (≈${balance:.2f})",
            'recent_transactions': "📝 <b>Recent Transactions:</b>",
            'no_transactions': "No recent transactions found.",
            'add_balance_note': "To add balance, please contact the administrator.",
            'refresh_button': "🔄 Refresh",
            'refreshed': "Balance refreshed",
            'up_to_date': "Balance is up to date",
            'error_message': "❌ An error occurred while fetching your balance. Please try again later.",
            'error_refresh': "❌ An error occurred while refreshing your balance. Please try again later."
        },
        'status': {
            'title': "📦 <b>Check Order Status</b>",
            'enter_order_id': "Please enter the order ID you want to check.\nExample: <code>1234567</code>\n\nOr click the button below to see your recent order IDs:",
            'show_order_ids': "📋 Show My Order IDs",
            'back_to_main': "◀️ Back to Main Menu",
            'no_orders': "You don't have any orders yet. Use /services to browse available services and place an order.",
            'your_order_ids': "📋 <b>Your Order IDs</b>\n\nCopy any ID and send it to check its status:",
            'back': "◀️ Back",
            'order_status': "📦 <b>Order Status</b>",
            'order_id': "🔢 Order ID: <code>{order_id}</code>",
            'service': "🛍️ Service: {service_name}",
            'quantity': "🔢 Quantity: {quantity}",
            'status': "📊 Status: {status}",
            'price': "💰 Price: ${price:.6f} / ETB {etb_price:.2f}",
            'start_count': "⏳ Start Count: {start_count}",
            'remains': "⌛ Remains: {remains}",
            'refresh': "🔄 Refresh",
            'status_up_to_date': "Status is already up to date!",
            'error_updating': "Error updating status",
            'order_not_found': "⚠️ Order not found or not accessible",
            'error_checking': "⚠️ An error occurred while checking the order status: {error}"
        },
        'recharge': {
            'title': "💳 <b>Recharge Account</b>",
            'select_payment_method': "Please select your preferred payment method:",
            'select_amount': "Please select the amount you want to recharge:\n\nChoose from preset amounts or click 'Custom Amount' to enter your own.",
            'custom_amount_usd': "💰 Please enter the amount you want to recharge (in USD):\nExample: <code>50</code> for $50",
            'custom_amount_etb': "💰 Please enter the amount you want to recharge (in ETB):\nExample: <code>1000</code> for ETB 1000",
            'minimum_amount_usd': "❌ Please enter a valid amount greater than $1.",
            'minimum_amount_etb': "❌ Minimum recharge amount for Ethiopian banks is <b>ETB 100</b>.\nPlease enter a higher amount.",
            'invalid_amount': "❌ Please enter a valid number.\nExample: <code>500</code> for {currency}500",
            'payment_verified': "✅ <b>Payment Verified!</b>\n\nYour payment of <code>${amount:.2f}</code> has been verified.\nThe amount has been added to your balance.\n\nUse /account to check your updated balance.",
            'payment_verified_etb': "✅ <b>Payment Verified!</b>\n\nYour payment of <code>ETB {formatted_etb}</code> (≈${amount:.2f}) has been verified.\nThe amount has been added to your balance.\n\nYour balance will now be displayed in ETB.\n\nUse /account to check your updated balance.",
            'payment_rejected': "❌ <b>Payment Rejected</b>\n\nYour payment of <code>${amount:.2f}</code> was not verified.\nPlease contact {admin_username} for more information.\n\nUse /recharge to try again.",
            'cancelled': "❌ Recharge cancelled. Use /recharge to start again.",
            'custom_amount': "💰 Custom Amount",
            'back': "🔙 Back",
            'cancel': "❌ Cancel",
            'wise': "🌐 Wise (International)",
            'eth_banks': "🏦 Ethiopian Banks",
            'intl_options': "🌍 Other International Options",
            'crypto': "₿ Cryptocurrency"
        },
        'services': {
            'platforms_title': "📱 <b>Service Platforms</b>",
            'platforms_description': "Please select a platform, search for services, or view all services:",
            'all_services': "🔍 All Services",
            'search_services': "🔎 Search Services",
            'platform_button': "📱 {platform} ({count})",
            'error_retrieving': "Error retrieving services. Please try again later.",
            'categories_title': "📂 <b>Categories</b> - {platform}",
            'categories_description': "Please select a category:",
            'all_categories': "📂 All Categories",
            'back_to_platforms': "⬅️ Back to Platforms",
            'services_title': "📋 <b>Services</b> - {category}",
            'services_page_info': " (Page {current_page}/{total_pages})",
            'services_description': "Select a service to place an order:",
            'back_to_categories': "⬅️ Back",
            'search_title': "🔍 <b>Search Services</b>",
            'search_description': "Please enter a search term to find services by name:",
            'search_results': "🔍 <b>Search Results</b> - {term}",
            'no_results': "No services found matching your search term. Please try again.",
            'service_details': "📋 <b>Service Details</b>",
            'service_id': "🆔 Service ID: <code>{id}</code>",
            'service_name': "📝 Name: {name}",
            'service_category': "📂 Category: {category}",
            'service_rate': "💰 Rate: ${rate} per 1000",
            'service_min': "⬇️ Min: {min}",
            'service_max': "⬆️ Max: {max}",
            'service_description': "📄 Description: {description}",
            'place_order': "🛒 Place Order",
            'back_to_services': "🔙 Back to Services",
            'error_service_details': "Error showing service details. Please try again.",
            'error_search': "Error initiating search. Please try again.",
            'error_display': "Error displaying services. Please try again."
        },
        'order': {
            'processing': "⏳ <b>Processing Order...</b>\n\nYour order is being placed on the website. Please wait...",
            'success': "✅ <b>Order Placed Successfully!{admin_note}</b>\n\nOrder ID: <code>{order_id}</code>\nService: {service_name}\nQuantity: {quantity}\nPrice: {price_display}\n\nYour order has been submitted to the website and is being processed.\nYou can check the status of your order with /status command.",
            'failed': "❌ <b>Order Failed</b>\n\nError: {error_message}\n\nYour order could not be placed on the website. Please try again later or contact support.",
            'error': "❌ <b>Order Failed</b>\n\nAn unexpected error occurred: {error}\n\nPlease try again later or contact support.",
            'quantity_set': "✅ Quantity set to: {quantity}\n\nPlease provide a link or username:",
            'invalid_quantity': "⚠️ Please enter a valid number for quantity.",
            'insufficient_balance': "❌ <b>Insufficient Balance</b>\n\nRequired: ${price:.6f} / ETB {etb_price:.2f}\nYour balance: ${user_balance:.6f} / ETB {etb_balance:.2f}\n\nPlease add funds to your account before placing the order.",
            'enter_link': "Please send the link to the post/profile you want to boost:",
            'select_service_first': "Please select a service first using the Services button or /services command.",
            'order_summary': "📋 <b>Order Summary</b>\n\nService: {service_name}\nLink: {link}\nQuantity: {quantity}\nPrice: {price_display}\n\nPlease confirm your order:",
            'min_quantity': "⚠️ Minimum quantity for this service is {min_quantity}. Please enter a higher quantity.",
            'max_quantity': "⚠️ Maximum quantity for this service is {max_quantity}. Please enter a lower quantity.",
            'order_quantity': "📊 <b>Order Quantity</b>",
            'please_select_quantity': "Please select the quantity you want to order:"
        },
        'help': {
            'title': "❓ <b>Help & Support</b>",
            'description': "If you need assistance or have any questions, please contact our support team.",
            'contact_admin': "📞 Contact Admin",
            'back_to_menu': "◀️ Back to Main Menu",
            'contact_support': "💬 Contact Support"
        },
        'referrals': {
            'title': "Referral Program",
            'description': "Invite your friends to join our service and earn rewards! Share your unique referral link with friends and earn a commission when they make purchases.",
            'your_link': "Your Referral Link",
            'stats': "Your Referral Stats",
            'total_referrals': "Total Referrals",
            'how_it_works': "How it works:\n1. Share your referral link with friends\n2. When they join using your link, they'll be counted as your referral\n3. You'll receive notifications when someone joins using your link",
            'share': "📤 Share Your Link",
            'share_text': "Join me on this amazing SMM Panel Bot! Use my referral link:",
            'back_to_menu': "◀️ Back to Main Menu",
            'new_referral': "🎉 <b>New Referral!</b>\n\nSomeone just joined using your referral link!",
            'welcome_referred': "👋 <b>Welcome!</b>\n\nYou've joined through a referral link. Enjoy our services!",
            'check_referrals': "Check My Referrals",
            'no_referrals': "You don't have any referrals yet. Share your referral link with friends to get started!",
            'referrals_list': "Here are the users who joined using your referral link",
            'back_to_referrals': "◀️ Back to Referrals"
        },
        'support': {
            'title': "💬 <b>Customer Support</b>",
            'description': "Need help? You can send a message directly to our support team. We'll get back to you as soon as possible.",
            'start_chat': "📝 Start Support Chat",
            'back_to_menu': "◀️ Back to Main Menu",
            'chat_started': "✅ <b>Support chat started!</b>\n\nPlease type your message below. Our team will respond as soon as possible.",
            'message_sent': "✅ Your message has been sent to our support team. We'll respond as soon as possible.",
            'chat_ended': "✅ Support chat has ended. If you need further assistance, you can start a new chat anytime.",
            'admin_notification': "📩 <b>New support message from user:</b>\n\nFrom: {user_info}\n\n<b>Message:</b>\n{message}",
            'reply_prompt': "✍️ Please type your reply to the user:",
            'reply_sent': "✅ Your reply has been sent to the user.",
            'reply_from_admin': "📩 <b>Reply from support team:</b>\n\n{message}",
            'admin_reply_header': "📩 <b>Reply from support team:</b>",
            'admin_has_replied': "✅ A support team member has joined the chat. You can continue your conversation.",
            'no_permission': "❌ You don't have permission to use this command.",
            'waiting_for_reply': "⏳ Please wait for our support team to respond to your message.",
            'end_chat': "❌ End Chat"
        },
        'tutorial': {
            'title': "📚 <b>Tutorials</b>",
            'select_tutorial': "Select a tutorial to learn how to use different features of the bot:",
            'back_to_tutorials': "◀️ Back to Tutorials",
            'back_to_menu': "🏠 Main Menu",
            'admin_manage': "🔧 Admin: Manage Tutorials",
            'edit_text': "✏️ Edit Text",
            'add_media': "🖼️ Add Media",
            'delete_media': "🗑️ Delete Media",
            'no_content': "This tutorial is currently being updated. Please check back later."
        }
    },
    'am': {  # Amharic
        'welcome': (
            "🌉 Welcome to KabirBridge!\n\n"
            "Your gateway to quick and efficient online services.\n\n"
            "✅ How to Use:\n"
            "1️⃣ Tap Services to browse available options.\n"
            "2️⃣ Select your desired service and follow the process.\n"
            "3️⃣ Complete your order and let the bot do the rest!\n\n"
            "💵 Payments: Safe and convenient payment options.\n"
            "📞 Support: +251907806267, @muay011\n\n"
            "🔹 Start now and experience instant results!"
        ),
        'select_language': "🌐 እባክዎ የወደዱትን ቋንቋ ይምረጡ:",
        'language_changed': "✅ ቋንቋ በተሳካ ሁኔታ ተቀይሯል!",
        'main_menu': {
            'services': "🛒 አገልግሎቶች",
            'place_order': "📦 ትዕዛዝ ይስጡ",
            'balance': "💰 ቀሪ ገንዘብ",
            'order_status': "📊 የትዕዛዝ ሁኔታ",
            'recharge': "💳 መለያ መሙላት",
            'help': "❓ እርዳታ",
            'languages': "🌐 ቋንቋዎች",
            'referrals': "👥 ሪፈራሎች",
            'support': "Customer Support",
            'tutorial': "📚 Tutorials"
        },
        'balance': {
            'title': "💰 <b>የእርስዎ ቀሪ ሂሳብ</b>",
            'current_balance_usd': "አሁን ያለው ቀሪ ሂሳብ: <code>${balance:.2f}</code>",
            'current_balance_etb': "አሁን ያለው ቀሪ ሂሳብ: <code>ETB {formatted_etb}</code> (≈${balance:.2f})",
            'recent_transactions': "📝 <b>የቅርብ ጊዜ ግብይቶች:</b>",
            'no_transactions': "ምንም የቅርብ ጊዜ ግብይቶች አልተገኙም።",
            'add_balance_note': "ቀሪ ሂሳብ ለመጨመር፣ እባክዎን አስተዳዳሪውን ያግኙ።",
            'refresh_button': "🔄 አድስ",
            'refreshed': "ቀሪ ሂሳብ ታድሷል",
            'up_to_date': "ቀሪ ሂሳብ የዘመነ ነው",
            'error_message': "❌ ቀሪ ሂሳብዎን በማግኘት ላይ ስህተት ተከስቷል። እባክዎ ቆይተው እንደገና ይሞክሩ።",
            'error_refresh': "❌ ቀሪ ሂሳብዎን በማደስ ላይ ስህተት ተከስቷል። እባክዎ ቆይተው እንደገና ይሞክሩ።"
        },
        'status': {
            'title': "📦 <b>የትዕዛዝ ሁኔታ ይመልከቱ</b>",
            'enter_order_id': "እባክዎን ሁኔታውን ማየት የሚፈልጉትን የትዕዛዝ መታወቂያ ያስገቡ።\nምሳሌ: <code>1234567</code>\n\nወይም የቅርብ ጊዜ የትዕዛዝ መታወቂያዎችዎን ለማየት ከዚህ በታች ያለውን አዝራር ጠቅ ያድርጉ:",
            'show_order_ids': "📋 የእኔን የትዕዛዝ መታወቂያዎች አሳይ",
            'back_to_main': "◀️ ወደ ዋናው ምናሌ ተመለስ",
            'no_orders': "እስካሁን ምንም ትዕዛዞች የሉዎትም። የሚገኙ አገልግሎቶችን ለማየት እና ትዕዛዝ ለማስቀመጥ /services ይጠቀሙ።",
            'your_order_ids': "📋 <b>የእርስዎ የትዕዛዝ መታወቂያዎች</b>\n\nሁኔታውን ለማየት ማንኛውንም መታወቂያ ይቅዱ እና ይላኩ:",
            'back': "◀️ ተመለስ",
            'order_status': "📦 <b>የትዕዛዝ ሁኔታ</b>",
            'order_id': "🔢 የትዕዛዝ መታወቂያ: <code>{order_id}</code>",
            'service': "🛍️ አገልግሎት: {service_name}",
            'quantity': "🔢 ብዛት: {quantity}",
            'status': "📊 ሁኔታ: {status}",
            'price': "💰 ዋጋ: ${price:.6f} / ETB {etb_price:.2f}",
            'start_count': "⏳ የመጀመሪያ ብዛት: {start_count}",
            'remains': "⌛ ቀሪ: {remains}",
            'refresh': "🔄 አድስ",
            'status_up_to_date': "ሁኔታው አስቀድሞ የዘመነ ነው!",
            'error_updating': "ሁኔታን በማዘመን ላይ ስህተት",
            'order_not_found': "⚠️ ትዕዛዝ አልተገኘም ወይም ተደራሽ አይደለም",
            'error_checking': "⚠️ የትዕዛዝ ሁኔታን በመፈተሽ ላይ ስህተት ተከስቷል: {error}"
        },
        'recharge': {
            'title': "💳 <b>መለያ መሙላት</b>",
            'select_payment_method': "እባክዎ የሚፈልጉትን የክፍያ ዘዴ ይምረጡ:",
            'select_amount': "እባክዎ መሙላት የሚፈልጉትን መጠን ይምረጡ:\n\nከቅድመ ተዘጋጅ መጠኖች ይምረጡ ወይም የራስዎን ለማስገባት 'ልዩ መጠን' ጠቅ ያድርጉ።",
            'custom_amount_usd': "💰 እባክዎ መሙላት የሚፈልጉትን መጠን ያስገቡ (በዶላር):\nምሳሌ: <code>50</code> ለ $50",
            'custom_amount_etb': "💰 እባክዎ መሙላት የሚፈልጉትን መጠን ያስገቡ (በብር):\nምሳሌ: <code>1000</code> ለ ETB 1000",
            'minimum_amount_usd': "❌ እባክዎ ከ $1 በላይ ትክክለኛ መጠን ያስገቡ።",
            'minimum_amount_etb': "❌ ለኢትዮጵያ ባንኮች ዝቅተኛው የመሙያ መጠን <b>ETB 100</b> ነው።\nእባክዎ ከፍ ያለ መጠን ያስገቡ።",
            'invalid_amount': "❌ እባክዎ ትክክለኛ ቁጥር ያስገቡ።\nምሳሌ: <code>500</code> ለ {currency}500",
            'payment_verified': "✅ <b>ክፍያ ተረጋግጧል!</b>\n\nየእርስዎ <code>${amount:.2f}</code> ክፍያ ተረጋግጧል።\nመጠኑ ወደ ሂሳብዎ ተጨምሯል።\n\nየተዘመነውን ሂሳብዎን ለማየት /account ይጠቀሙ።",
            'payment_verified_etb': "✅ <b>ክፍያ ተረጋግጧል!</b>\n\nየእርስዎ <code>ETB {formatted_etb}</code> (≈${amount:.2f}) ክፍያ ተረጋግጧል።\nመጠኑ ወደ ሂሳብዎ ተጨምሯል።\n\nሂሳብዎ አሁን በብር ይታያል።\n\nየተዘመነውን ሂሳብዎን ለማየት /account ይጠቀሙ።",
            'payment_rejected': "❌ <b>ክፍያ ተቀባይነት አላገኘም</b>\n\nየእርስዎ <code>${amount:.2f}</code> ክፍያ አልተረጋገጠም።\nለተጨማሪ መረጃ እባክዎ {admin_username}ን ያግኙ።\n\nእንደገና ለመሞከር /recharge ይጠቀሙ።",
            'cancelled': "❌ መሙላት ተሰርዟል። እንደገና ለመጀመር /recharge ይጠቀሙ።",
            'custom_amount': "💰 ልዩ መጠን",
            'back': "🔙 ተመለስ",
            'cancel': "❌ ሰርዝ",
            'wise': "🌐 ዋይዝ (ዓለም አቀፍ)",
            'eth_banks': "🏦 የኢትዮጵያ ባንኮች",
            'intl_options': "🌍 ሌሎች ዓለም አቀፍ አማራጮች",
            'crypto': "₿ ክሪፕቶከረንሲ"
        },
        'services': {
            'platforms_title': "📱 <b>የአገልግሎት መድረኮች</b>",
            'platforms_description': "እባክዎ መድረክ ይምረጡ፣ አገልግሎቶችን ይፈልጉ፣ ወይም ሁሉንም አገልግሎቶች ይመልከቱ፡",
            'all_services': "🔍 ሁሉም አገልግሎቶች",
            'search_services': "🔎 አገልግሎቶችን ይፈልጉ",
            'platform_button': "📱 {platform} ({count})",
            'error_retrieving': "አገልግሎቶችን በማግኘት ላይ ስህተት። እባክዎ ቆይተው እንደገና ይሞክሩ።",
            'categories_title': "📂 <b>ምድቦች</b> - {platform}",
            'categories_description': "እባክዎ ምድብ ይምረጡ፡",
            'all_categories': "📂 ሁሉም ምድቦች",
            'back_to_platforms': "⬅️ ወደ መድረኮች ተመለስ",
            'services_title': "📋 <b>አገልግሎቶች</b> - {category}",
            'services_page_info': " (ገጽ {current_page}/{total_pages})",
            'services_description': "ትዕዛዝ ለመስጠት አገልግሎት ይምረጡ፡",
            'back_to_categories': "⬅️ ተመለስ",
            'search_title': "🔍 <b>አገልግሎቶችን ይፈልጉ</b>",
            'search_description': "አገልግሎቶችን በስም ለማግኘት የፍለጋ ቃል ያስገቡ፡",
            'search_results': "🔍 <b>የፍለጋ ውጤቶች</b> - {term}",
            'no_results': "ከፍለጋ ቃልዎ ጋር የሚዛመዱ አገልግሎቶች አልተገኙም። እባክዎ እንደገና ይሞክሩ።",
            'service_details': "📋 <b>የአገልግሎት ዝርዝሮች</b>",
            'service_id': "🆔 የአገልግሎት መታወቂያ: <code>{id}</code>",
            'service_name': "📝 ስም: {name}",
            'service_category': "📂 ምድብ: {category}",
            'service_rate': "💰 ዋጋ: ${rate} ለ 1000",
            'service_min': "⬇️ ዝቅተኛ: {min}",
            'service_max': "⬆️ ከፍተኛ: {max}",
            'service_description': "📄 መግለጫ: {description}",
            'place_order': "🛒 ትዕዛዝ ይስጡ",
            'back_to_services': "🔙 ወደ አገልግሎቶች ተመለስ",
            'error_service_details': "የአገልግሎት ዝርዝሮችን በማሳየት ላይ ስህተት። እባክዎ እንደገና ይሞክሩ።",
            'error_search': "ፍለጋን በመጀመር ላይ ስህተት። እባክዎ እንደገና ይሞክሩ።",
            'error_display': "አገልግሎቶችን በማሳየት ላይ ስህተት። እባክዎ እንደገና ይሞክሩ።"
        },
        'order': {
            'processing': "⏳ <b>ትዕዛዝ በማስኬድ ላይ...</b>\n\nትዕዛዝዎ በድህረ ገጹ ላይ እየተቀመጠ ነው። እባክዎ ይጠብቁ...",
            'success': "✅ <b>ትዕዛዝ በተሳካ ሁኔታ ተቀምጧል!{admin_note}</b>\n\nየትዕዛዝ መታወቂያ: <code>{order_id}</code>\nአገልግሎት: {service_name}\nብዛት: {quantity}\nዋጋ: {price_display}\n\nትዕዛዝዎ ለድህረ ገጹ ተልኳል እና እየተካሄደ ነው።\nየትዕዛዝዎን ሁኔታ በ /status ትዕዛዝ መፈተሽ ይችላሉ።",
            'failed': "❌ <b>ትዕዛዝ አልተሳካም</b>\n\nስህተት: {error_message}\n\nትዕዛዝዎ በድህረ ገጹ ላይ ሊቀመጥ አልቻለም። እባክዎ ቆይተው እንደገና ይሞክሩ ወይም ድጋፍን ያግኙ።",
            'error': "❌ <b>ትዕዛዝ አልተሳካም</b>\n\nያልተጠበቀ ስህተት ተከስቷል: {error}\n\nእባክዎ ቆይተው እንደገና ይሞክሩ ወይም ድጋፍን ያግኙ።",
            'quantity_set': "✅ ብዛት ተቀምጧል: {quantity}\n\nእባክዎ አገናኝ ወይም የተጠቃሚ ስም ያቅርቡ:",
            'invalid_quantity': "⚠️ እባክዎ ለብዛት ትክክለኛ ቁጥር ያስገቡ።",
            'insufficient_balance': "❌ <b>በቂ ያልሆነ ቀሪ ሂሳብ</b>\n\nየሚያስፈልገው: ${price:.6f} / ETB {etb_price:.2f}\nየእርስዎ ቀሪ ሂሳብ: ${user_balance:.6f} / ETB {etb_balance:.2f}\n\nትዕዛዝ ከማስቀመጥዎ በፊት እባክዎ ወደ መለያዎ ገንዘብ ይጨምሩ።",
            'enter_link': "እባክዎ ማሳደግ የሚፈልጉትን ልጥፍ/መገለጫ አገናኝ ይላኩ:",
            'select_service_first': "እባክዎ አገልግሎቶች አዝራሩን ወይም /services ትዕዛዝን በመጠቀም መጀመሪያ አገልግሎት ይምረጡ።",
            'order_summary': "📋 <b>የትዕዛዝ ማጠቃለያ</b>\n\nአገልግሎት: {service_name}\nአገናኝ: {link}\nብዛት: {quantity}\nዋጋ: {price_display}\n\nእባክዎ ትዕዛዝዎን ያረጋግጡ:",
            'min_quantity': "⚠️ ለዚህ አገልግሎት ዝቅተኛው ብዛት {min_quantity} ነው። እባክዎ ከፍ ያለ ብዛት ያስገቡ።",
            'max_quantity': "⚠️ ለዚህ አገልግሎት ከፍተኛው ብዛት {max_quantity} ነው። እባክዎ ዝቅ ያለ ብዛት ያስገቡ።",
            'order_quantity': "📊 <b>የትዕዛዝ ብዛት</b>",
            'please_select_quantity': "እባክዎ ማዘዝ የሚፈልጉትን ብዛት ይምረጡ:"
        },
        'help': {
            'title': "❓ <b>Help & Support</b>",
            'description': "If you need assistance or have any questions, please contact our support team.",
            'contact_admin': "📞 Contact Admin",
            'back_to_menu': "◀️ Back to Main Menu",
            'contact_support': "💬 Contact Support"
        },
        'referrals': {
            'title': "የሪፈራል ፕሮግራም",
            'description': "ጓደኞችዎን ወደ አገልግሎታችን እንዲቀላቀሉ ይጋብዙ እና ሽልማቶችን ያግኙ! የእርስዎን ልዩ የሪፈራል ማስፈንጠሪያ ከጓደኞች ጋር ይጋሩ እና ግዢዎችን ሲያደርጉ ኮሚሽን ያግኙ።",
            'your_link': "የእርስዎ የሪፈራል ማስፈንጠሪያ",
            'stats': "የእርስዎ የሪፈራል ስታቲስቲክስ",
            'total_referrals': "ጠቅላላ ሪፈራሎች",
            'how_it_works': "እንዴት እንደሚሰራ:\n1. የሪፈራል ማስፈንጠሪያዎን ከጓደኞች ጋር ይጋሩ\n2. በማስፈንጠሪያዎ ሲቀላቀሉ፣ እንደ ሪፈራልዎ ይቆጠራሉ\n3. ሰው በማስፈንጠሪያዎ ሲቀላቀል ማሳወቂያዎችን ይቀበላሉ",
            'share': "📤 ማስፈንጠሪያዎን ያጋሩ",
            'share_text': "በዚህ አስደናቂ SMM Panel Bot ላይ ይቀላቀሉኝ! የእኔን የሪፈራል ማስፈንጠሪያ ይጠቀሙ:",
            'back_to_menu': "◀️ ወደ ዋና ምናሌ ተመለስ",
            'new_referral': "🎉 <b>አዲስ ሪፈራል!</b>\n\nአንድ ሰው አሁን በእርስዎ የሪፈራል ማስፈንጠሪያ ተቀላቅሏል!",
            'welcome_referred': "👋 <b>እንኳን ደህና መጡ!</b>\n\nበሪፈራል ማስፈንጠሪያ አማካኝነት ተቀላቅለዋል። አገልግሎታችንን ይደሰቱበት!",
            'check_referrals': "የእኔን ሪፈራሎች ይመልከቱ",
            'no_referrals': "እስካሁን ምንም ሪፈራሎች የሉዎትም። ለመጀመር የሪፈራል ማስፈንጠሪያዎን ከጓደኞች ጋር ይጋሩ!",
            'referrals_list': "እነዚህ በእርስዎ የሪፈራል ማስፈንጠሪያ የተቀላቀሉ ተጠቃሚዎች ናቸው",
            'back_to_referrals': "◀️ ወደ ሪፈራሎች ተመለስ"
        },
        'support': {
            'title': "💬 <b>Customer Support</b>",
            'description': "Need help? You can send a message directly to our support team. We'll get back to you as soon as possible.",
            'start_chat': "📝 Start Support Chat",
            'back_to_menu': "◀️ Back to Main Menu",
            'chat_started': "✅ <b>Support chat started!</b>\n\nPlease type your message below. Our team will respond as soon as possible.",
            'message_sent': "✅ Your message has been sent to our support team. We'll respond as soon as possible.",
            'chat_ended': "✅ Support chat has ended. If you need further assistance, you can start a new chat anytime.",
            'admin_notification': "📩 <b>New support message from user:</b>\n\nFrom: {user_info}\nUser ID: <code>{user_id}</code>\n\n<b>Message:</b>\n{message}",
            'reply_prompt': "✍️ Please type your reply to the user:",
            'reply_sent': "✅ Your reply has been sent to the user.",
            'reply_from_admin': "📩 <b>Reply from support team:</b>\n\n{message}",
            'admin_reply_header': "📩 <b>Reply from support team:</b>",
            'admin_has_replied': "✅ A support team member has joined the chat. You can continue your conversation.",
            'no_permission': "❌ You don't have permission to use this command.",
            'waiting_for_reply': "⏳ Please wait for our support team to respond to your message.",
            'end_chat': "❌ End Chat"
        },
        'tutorial': {
            'title': "📚 <b>Tutorials</b>",
            'select_tutorial': "Select a tutorial to learn how to use different features of the bot:",
            'back_to_tutorials': "◀️ Back to Tutorials",
            'back_to_menu': "🏠 Main Menu",
            'admin_manage': "🔧 Admin: Manage Tutorials",
            'edit_text': "✏️ Edit Text",
            'add_media': "🖼️ Add Media",
            'delete_media': "🗑️ Delete Media",
            'no_content': "This tutorial is currently being updated. Please check back later."
        },
        'new_user_bonus': "🎁 <b>Welcome Bonus!</b>\n\nAs a new user, you have received a bonus of {amount} {currency}!\n\nYou can check your balance with /balance"
    },
    'ar': {  # Arabic
        'welcome': (
            "🌉 Welcome to KabirBridge!\n\n"
            "Your gateway to quick and efficient online services.\n\n"
            "✅ How to Use:\n"
            "1️⃣ Tap Services to browse available options.\n"
            "2️⃣ Select your desired service and follow the process.\n"
            "3️⃣ Complete your order and let the bot do the rest!\n\n"
            "💵 Payments: Safe and convenient payment options.\n"
            "📞 Support: +251907806267, @muay011\n\n"
            "🔹 Start now and experience instant results!"
        ),
        'select_language': "🌐 الرجاء اختيار اللغة المفضلة:",
        'language_changed': "✅ اللغة تم تغييرها بنجاح!",
        'main_menu': {
            'services': "🛒 الخدمات",
            'place_order': "📦 تقديم طلب",
            'balance': "💰 الرصيد",
            'order_status': "📊 حالة الطلب",
            'recharge': "💳 إعادة الشحن",
            'help': "❓ المساعدة",
            'languages': "🌐 اللغات",
            'referrals': "👥 الإحالات",
            'support': "Customer Support",
            'tutorial': "📚 الدليل"
        },
        'balance': {
            'title': "💰 <b>رصيدك</b>",
            'current_balance_usd': "الرصيد الحالي: <code>${balance:.2f}</code>",
            'current_balance_etb': "الرصيد الحالي: <code>ETB {formatted_etb}</code> (≈${balance:.2f})",
            'recent_transactions': "📝 <b>المعاملات الأخيرة:</b>",
            'no_transactions': "لم يتم العثور على معاملات حديثة.",
            'add_balance_note': "لإضافة رصيد، يرجى الاتصال بالمسؤول.",
            'refresh_button': "🔄 تحديث",
            'refreshed': "تم تحديث الرصيد",
            'up_to_date': "الرصيد محدث",
            'error_message': "❌ حدث خطأ أثناء جلب رصيدك. يرجى المحاولة مرة أخرى لاحقًا.",
            'error_refresh': "❌ حدث خطأ أثناء تحديث رصيدك. يرجى المحاولة مرة أخرى لاحقًا."
        },
        'status': {
            'title': "📦 <b>التحقق من حالة الطلب</b>",
            'enter_order_id': "الرجاء إدخال معرف الطلب الذي تريد التحقق منه.\nمثال: <code>1234567</code>\n\nأو انقر على الزر أدناه لرؤية معرفات الطلبات الأخيرة:",
            'show_order_ids': "📋 عرض معرفات طلباتي",
            'back_to_main': "◀️ العودة إلى القائمة الرئيسية",
            'no_orders': "ليس لديك أي طلبات حتى الآن. استخدم /services لتصفح الخدمات المتاحة وتقديم طلب.",
            'your_order_ids': "📋 <b>معرفات طلباتك</b>\n\nانسخ أي معرف وأرسله للتحقق من حالته:",
            'back': "◀️ رجوع",
            'order_status': "📦 <b>حالة الطلب</b>",
            'order_id': "🔢 معرف الطلب: <code>{order_id}</code>",
            'service': "🛍️ الخدمة: {service_name}",
            'quantity': "🔢 الكمية: {quantity}",
            'status': "📊 الحالة: {status}",
            'price': "💰 السعر: ${price:.6f} / ETB {etb_price:.2f}",
            'start_count': "⏳ العدد الأولي: {start_count}",
            'remains': "⌛ المتبقي: {remains}",
            'refresh': "🔄 تحديث",
            'status_up_to_date': "الحالة محدثة بالفعل!",
            'error_updating': "خطأ في تحديث الحالة",
            'order_not_found': "⚠️ الطلب غير موجود أو غير قابل للوصول",
            'error_checking': "⚠️ حدث خطأ أثناء التحقق من حالة الطلب: {error}"
        },
        'recharge': {
            'title': "💳 <b>إعادة شحن الحساب</b>",
            'select_payment_method': "يرجى اختيار طريقة الدفع المفضلة لديك:",
            'select_amount': "يرجى اختيار المبلغ الذي تريد إعادة شحنه:\n\nاختر من المبالغ المحددة مسبقًا أو انقر على 'مبلغ مخصص' لإدخال المبلغ الخاص بك.",
            'custom_amount_usd': "💰 يرجى إدخال المبلغ الذي تريد إعادة شحنه (بالدولار الأمريكي):\nمثال: <code>50</code> لـ $50",
            'custom_amount_etb': "💰 يرجى إدخال المبلغ الذي تريد إعادة شحنه (بالبر الإثيوبي):\nمثال: <code>1000</code> لـ ETB 1000",
            'minimum_amount_usd': "❌ يرجى إدخال مبلغ صالح أكبر من $1.",
            'minimum_amount_etb': "❌ الحد الأدنى لمبلغ إعادة الشحن للبنوك الإثيوبية هو <b>ETB 100</b>.\nيرجى إدخال مبلغ أعلى.",
            'invalid_amount': "❌ يرجى إدخال رقم صالح.\nمثال: <code>500</code> لـ {currency}500",
            'payment_verified': "✅ <b>تم التحقق من الدفع!</b>\n\nتم التحقق من دفعتك البالغة <code>${amount:.2f}</code>.\nتمت إضافة المبلغ إلى رصيدك.\n\nاستخدم /account للتحقق من رصيدك المحدث.",
            'payment_verified_etb': "✅ <b>تم التحقق من الدفع!</b>\n\nتم التحقق من دفعتك البالغة <code>ETB {formatted_etb}</code> (≈${amount:.2f}).\nتمت إضافة المبلغ إلى رصيدك.\n\nسيتم عرض رصيدك الآن بالبر الإثيوبي.\n\nاستخدم /account للتحقق من رصيدك المحدث.",
            'payment_rejected': "❌ <b>تم رفض الدفع</b>\n\nلم يتم التحقق من دفعتك البالغة <code>${amount:.2f}</code>.\nيرجى الاتصال بـ {admin_username} لمزيد من المعلومات.\n\nاستخدم /recharge للمحاولة مرة أخرى.",
            'cancelled': "❌ تم إلغاء إعادة الشحن. استخدم /recharge للبدء مرة أخرى.",
            'custom_amount': "💰 مبلغ مخصص",
            'back': "🔙 رجوع",
            'cancel': "❌ إلغاء",
            'wise': "🌐 وايز (دولي)",
            'eth_banks': "🏦 البنوك الإثيوبية",
            'intl_options': "🌍 خيارات دولية أخرى",
            'crypto': "₿ العملات المشفرة"
        },
        'services': {
            'platforms_title': "📱 <b>منصات الخدمة</b>",
            'platforms_description': "يرجى اختيار منصة، أو البحث عن الخدمات، أو عرض جميع الخدمات:",
            'all_services': "🔍 جميع الخدمات",
            'search_services': "🔎 البحث عن الخدمات",
            'platform_button': "📱 {platform} ({count})",
            'error_retrieving': "خطأ في استرجاع الخدمات. يرجى المحاولة مرة أخرى لاحقًا.",
            'categories_title': "📂 <b>الفئات</b> - {platform}",
            'categories_description': "يرجى اختيار فئة:",
            'all_categories': "📂 جميع الفئات",
            'back_to_platforms': "⬅️ العودة إلى المنصات",
            'services_title': "📋 <b>الخدمات</b> - {category}",
            'services_page_info': " (الصفحة {current_page}/{total_pages})",
            'services_description': "اختر خدمة لتقديم طلب:",
            'back_to_categories': "⬅️ رجوع",
            'search_title': "🔍 <b>البحث عن الخدمات</b>",
            'search_description': "يرجى إدخال مصطلح البحث للعثور على الخدمات حسب الاسم:",
            'search_results': "🔍 <b>نتائج البحث</b> - {term}",
            'no_results': "لم يتم العثور على خدمات تطابق مصطلح البحث الخاص بك. يرجى المحاولة مرة أخرى.",
            'service_details': "📋 <b>تفاصيل الخدمة</b>",
            'service_id': "🆔 معرف الخدمة: <code>{id}</code>",
            'service_name': "📝 الاسم: {name}",
            'service_category': "📂 الفئة: {category}",
            'service_rate': "💰 السعر: ${rate} لكل 1000",
            'service_min': "⬇️ الحد الأدنى: {min}",
            'service_max': "⬆️ الحد الأقصى: {max}",
            'service_description': "📄 الوصف: {description}",
            'place_order': "🛒 تقديم طلب",
            'back_to_services': "🔙 العودة إلى الخدمات",
            'error_service_details': "خطأ في عرض تفاصيل الخدمة. يرجى المحاولة مرة أخرى.",
            'error_search': "خطأ في بدء البحث. يرجى المحاولة مرة أخرى.",
            'error_display': "خطأ في عرض الخدمات. يرجى المحاولة مرة أخرى."
        },
        'order': {
            'processing': "⏳ <b>جاري معالجة الطلب...</b>\n\nيتم وضع طلبك على الموقع. يرجى الانتظار...",
            'success': "✅ <b>تم وضع الطلب بنجاح!{admin_note}</b>\n\nمعرف الطلب: <code>{order_id}</code>\nالخدمة: {service_name}\nالكمية: {quantity}\nالسعر: {price_display}\n\nتم إرسال طلبك إلى الموقع وهو قيد المعالجة.\nيمكنك التحقق من حالة طلبك باستخدام أمر /status.",
            'failed': "❌ <b>فشل الطلب</b>\n\nخطأ: {error_message}\n\nتعذر وضع طلبك على الموقع. يرجى المحاولة مرة أخرى لاحقًا أو الاتصال بالدعم.",
            'error': "❌ <b>فشل الطلب</b>\n\nحدث خطأ غير متوقع: {error}\n\nيرجى المحاولة مرة أخرى لاحقًا أو الاتصال بالدعم.",
            'quantity_set': "✅ تم تعيين الكمية إلى: {quantity}\n\nيرجى تقديم رابط أو اسم مستخدم:",
            'invalid_quantity': "⚠️ يرجى إدخال رقم صالح للكمية.",
            'insufficient_balance': "❌ <b>رصيد غير كافٍ</b>\n\nالمطلوب: ${price:.6f} / ETB {etb_price:.2f}\nرصيدك: ${user_balance:.6f} / ETB {etb_balance:.2f}\n\nيرجى إضافة أموال إلى حسابك قبل وضع الطلب.",
            'enter_link': "يرجى إرسال الرابط للمنشور/الملف الشخصي الذي تريد تعزيزه:",
            'select_service_first': "يرجى تحديد خدمة أولاً باستخدام زر الخدمات أو أمر /services.",
            'order_summary': "📋 <b>ملخص الطلب</b>\n\nالخدمة: {service_name}\nالرابط: {link}\nالكمية: {quantity}\nالسعر: {price_display}\n\nيرجى تأكيد طلبك:",
            'min_quantity': "⚠️ الحد الأدنى للكمية لهذه الخدمة هو {min_quantity}. يرجى إدخال كمية أعلى.",
            'max_quantity': "⚠️ الحد الأقصى للكمية لهذه الخدمة هو {max_quantity}. يرجى إدخال كمية أقل.",
            'order_quantity': "📊 <b>كمية الطلب</b>",
            'please_select_quantity': "الرجاء تحديد الكمية التي تريد طلبها:"
        },
        'help': {
            'title': "❓ <b>Help & Support</b>",
            'description': "If you need assistance or have any questions, please contact our support team.",
            'contact_admin': "📞 Contact Admin",
            'back_to_menu': "◀️ Back to Main Menu",
            'contact_support': "💬 Contact Support"
        },
        'referrals': {
            'title': "برنامج الإحالة",
            'description': "ادعُ أصدقاءك للانضمام إلى خدمتنا واحصل على مكافآت! شارك رابط الإحالة الفريد الخاص بك مع الأصدقاء واكسب عمولة عندما يقومون بعمليات شراء.",
            'your_link': "رابط الإحالة الخاص بك",
            'stats': "إحصائيات الإحالة الخاصة بك",
            'total_referrals': "إجمالي الإحالات",
            'how_it_works': "كيف يعمل:\n1. شارك رابط الإحالة الخاص بك مع الأصدقاء\n2. عندما ينضمون باستخدام رابطك، سيتم احتسابهم كإحالة لك\n3. ستتلقى إشعارات عندما ينضم شخص ما باستخدام رابط الإحالة الخاص بك",
            'share': "📤 شارك رابطك",
            'share_text': "انضم إليّ في بوت لوحة SMM الرائع هذا! استخدم رابط الإحالة الخاص بي:",
            'back_to_menu': "◀️ العودة إلى القائمة الرئيسية",
            'new_referral': "🎉 <b>إحالة جديدة!</b>\n\nانضم شخص ما للتو باستخدام رابط الإحالة الخاص بك!",
            'welcome_referred': "👋 <b>مرحبًا!</b>\n\nلقد انضممت من خلال رابط إحالة. استمتع بخدماتنا!",
            'check_referrals': "تحقق من إحالاتي",
            'no_referrals': "ليس لديك أي إحالات حتى الآن. شارك رابط الإحالة الخاص بك مع الأصدقاء للبدء!",
            'referrals_list': "هؤلاء هم المستخدمون الذين انضموا باستخدام رابط الإحالة الخاص بك",
            'back_to_referrals': "◀️ العودة إلى الإحالات"
        },
        'support': {
            'title': "💬 <b>Customer Support</b>",
            'description': "Need help? You can send a message directly to our support team. We'll get back to you as soon as possible.",
            'start_chat': "📝 Start Support Chat",
            'back_to_menu': "◀️ Back to Main Menu",
            'chat_started': "✅ <b>Support chat started!</b>\n\nPlease type your message below. Our team will respond as soon as possible.",
            'message_sent': "✅ Your message has been sent to our support team. We'll respond as soon as possible.",
            'chat_ended': "✅ Support chat has ended. If you need further assistance, you can start a new chat anytime.",
            'admin_notification': "📩 <b>New support message from user:</b>\n\nFrom: {user_info}\nUser ID: <code>{user_id}</code>\n\n<b>Message:</b>\n{message}",
            'reply_prompt': "✍️ Please type your reply to the user:",
            'reply_sent': "✅ Your reply has been sent to the user.",
            'reply_from_admin': "📩 <b>Reply from support team:</b>\n\n{message}",
            'admin_reply_header': "📩 <b>Reply from support team:</b>",
            'admin_has_replied': "✅ A support team member has joined the chat. You can continue your conversation.",
            'no_permission': "❌ You don't have permission to use this command.",
            'waiting_for_reply': "⏳ Please wait for our support team to respond to your message.",
            'end_chat': "❌ End Chat"
        },
        'tutorial': {
            'title': "📚 <b>Tutorials</b>",
            'select_tutorial': "Select a tutorial to learn how to use different features of the bot:",
            'back_to_tutorials': "◀️ Back to Tutorials",
            'back_to_menu': "🏠 Main Menu",
            'admin_manage': "🔧 Admin: Manage Tutorials",
            'edit_text': "✏️ Edit Text",
            'add_media': "🖼️ Add Media",
            'delete_media': "🗑️ Delete Media",
            'no_content': "This tutorial is currently being updated. Please check back later."
        }
    },
    'hi': {  # Hindi (Indian)
        'welcome': (
            "🌉 Welcome to KabirBridge!\n\n"
            "Your gateway to quick and efficient online services.\n\n"
            "✅ How to Use:\n"
            "1️⃣ Tap Services to browse available options.\n"
            "2️⃣ Select your desired service and follow the process.\n"
            "3️⃣ Complete your order and let the bot do the rest!\n\n"
            "💵 Payments: Safe and convenient payment options.\n"
            "📞 Support: +251907806267, @muay011\n\n"
            "🔹 Start now and experience instant results!"
        ),
        'select_language': "🌐 कृपया अपनी पसंदीदा भाषा चुनें:",
        'language_changed': "✅ भाषा सफलतापूर्वक बदल दी गई है!",
        'main_menu': {
            'services': "🛒 सेवाएं",
            'place_order': "📦 ऑर्डर दें",
            'balance': "💰 बैलेंस",
            'order_status': "📊 ऑर्डर स्थिति",
            'recharge': "💳 रिचार्ज",
            'help': "❓ सहायता",
            'languages': "🌐 भाषाएं",
            'referrals': "👥 रेफरल",
            'support': "Customer Support",
            'tutorial': "📚 ट्यूटोरियल"
        },
        'balance': {
            'title': "💰 <b>आपका बैलेंस</b>",
            'current_balance_usd': "वर्तमान बैलेंस: <code>${balance:.2f}</code>",
            'current_balance_etb': "वर्तमान बैलेंस: <code>ETB {formatted_etb}</code> (≈${balance:.2f})",
            'recent_transactions': "📝 <b>हाल के लेनदेन:</b>",
            'no_transactions': "कोई हालिया लेनदेन नहीं मिला।",
            'add_balance_note': "बैलेंस जोड़ने के लिए, कृपया प्रशासक से संपर्क करें।",
            'refresh_button': "🔄 रीफ्रेश",
            'refreshed': "बैलेंस रीफ्रेश किया गया",
            'up_to_date': "बैलेंस अप टू डेट है",
            'error_message': "❌ आपका बैलेंस प्राप्त करते समय एक त्रुटि हुई। कृपया बाद में पुनः प्रयास करें।",
            'error_refresh': "❌ आपका बैलेंस रीफ्रेश करते समय एक त्रुटि हुई। कृपया बाद में पुनः प्रयास करें।"
        },
        'status': {
            'title': "📦 <b>ऑर्डर स्थिति जांचें</b>",
            'enter_order_id': "कृपया वह ऑर्डर आईडी दर्ज करें जिसकी आप जांच करना चाहते हैं।\nउदाहरण: <code>1234567</code>\n\nया अपने हाल के ऑर्डर आईडी देखने के लिए नीचे दिए गए बटन पर क्लिक करें:",
            'show_order_ids': "📋 मेरे ऑर्डर आईडी दिखाएं",
            'back_to_main': "◀️ मुख्य मेनू पर वापस जाएं",
            'no_orders': "आपके पास अभी तक कोई ऑर्डर नहीं है। उपलब्ध सेवाओं को ब्राउज़ करने और ऑर्डर देने के लिए /services का उपयोग करें।",
            'your_order_ids': "📋 <b>आपके ऑर्डर आईडी</b>\n\nकिसी भी आईडी को कॉपी करें और उसकी स्थिति जांचने के लिए भेजें:",
            'back': "◀️ वापस",
            'order_status': "📦 <b>ऑर्डर स्थिति</b>",
            'order_id': "🔢 ऑर्डर आईडी: <code>{order_id}</code>",
            'service': "🛍️ सेवा: {service_name}",
            'quantity': "🔢 मात्रा: {quantity}",
            'status': "📊 स्थिति: {status}",
            'price': "💰 कीमत: ${price:.6f} / ETB {etb_price:.2f}",
            'start_count': "⏳ प्रारंभिक गिनती: {start_count}",
            'remains': "⌛ शेष: {remains}",
            'refresh': "🔄 रीफ्रेश",
            'status_up_to_date': "स्थिति पहले से ही अप टू डेट है!",
            'error_updating': "स्थिति अपडेट करने में त्रुटि",
            'order_not_found': "⚠️ ऑर्डर नहीं मिला या पहुंच योग्य नहीं है",
            'error_checking': "⚠️ ऑर्डर स्थिति की जांच करते समय एक त्रुटि हुई: {error}"
        },
        'recharge': {
            'title': "💳 <b>खाता रिचार्ज करें</b>",
            'select_payment_method': "कृपया अपनी पसंदीदा भुगतान विधि चुनें:",
            'select_amount': "कृपया वह राशि चुनें जिसे आप रिचार्ज करना चाहते हैं:\n\nपहले से तय राशियों में से चुनें या अपनी राशि दर्ज करने के लिए 'कस्टम राशि' पर क्लिक करें।",
            'custom_amount_usd': "💰 कृपया वह राशि दर्ज करें जिसे आप रिचार्ज करना चाहते हैं (USD में):\nउदाहरण: <code>50</code> लिए $50",
            'custom_amount_etb': "💰 कृपया वह राशि दर्ज करें जिसे आप रिचार्ज करना चाहते हैं (ETB में):\nउदाहरण: <code>1000</code> लिए ETB 1000",
            'minimum_amount_usd': "❌ कृपया $1'से अधिक की वैध राशि दर्ज करें।",
            'minimum_amount_etb': "❌ इथियोपियाई बैंकों के लिए न्यूनतम रिचार्ज राशि <b>ETB 100</b> है।\nकृपया उच्च राशि दर्ज करें।",
            'invalid_amount': "❌ कृपया एक वैध संख्या दर्ज करें।\nउदाहरण: <code>500</code> लिए {currency}500",
            'payment_verified': "✅ <b>भुगतान सत्यापित!</b>\n\nआपका <code>${amount:.2f}</code> का भुगतान सत्यापित किया गया है।\nराशि आपके बैलेंस में जोड़ दी गई है।\n\nअपने अपडेटेड बैलेंस की जांच करने के लिए /account का उपयोग करें।",
            'payment_verified_etb': "✅ <b>भुगतान सत्यापित!</b>\n\nआपका <code>ETB {formatted_etb}</code> (≈${amount:.2f}) का भुगतान सत्यापित किया गया है।\nराशि आपके बैलेंस में जोड़ दी गई है।\n\nआपका बैलेंस अब ETB में दिखाया जाएगा।\n\nअपने अपडेटेड बैलेंस की जांच करने के लिए /account का उपयोग करें।",
            'payment_rejected': "❌ <b>भुगतान अस्वीकृत</b>\n\nआपके <code>${amount:.2f}</code> के भुगतान का सत्यापन नहीं किया गया।\nअधिक जानकारी के लिए कृपया {admin_username} से संपर्क करें।\n\nपुनः प्रयास करने के लिए /recharge का उपयोग करें।",
            'cancelled': "❌ रिचार्ज रद्द किया गया। फिर से शुरू करने के लिए /recharge का उपयोग करें।",
            'custom_amount': "💰 कस्टम राशि",
            'back': "🔙 वापस",
            'cancel': "❌ रद्द करें",
            'wise': "🌐 वाइज़ (अंतरराष्ट्रीय)",
            'eth_banks': "🏦 इथियोपियाई बैंक",
            'intl_options': "🌍 अन्य अंतरराष्ट्रीय विकल्प",
            'crypto': "₿ क्रिप्टोकरेंसी"
        },
        'services': {
            'platforms_title': "📱 <b>सेवा प्लेटफॉर्म</b>",
            'platforms_description': "कृपया एक प्लेटफॉर्म चुनें, सेवाओं को खोजें, या सभी सेवाएं देखें:",
            'all_services': "🔍 सभी सेवाएं",
            'search_services': "🔎 सेवाएं खोजें",
            'platform_button': "📱 {platform} ({count})",
            'error_retrieving': "सेवाओं को प्राप्त करने में त्रुटि। कृपया बाद में पुनः प्रयास करें।",
            'categories_title': "📂 <b>श्रेणियां</b> - {platform}",
            'categories_description': "कृपया एक श्रेणी चुनें:",
            'all_categories': "📂 सभी श्रेणियां",
            'back_to_platforms': "⬅️ प्लेटफॉर्म पर वापस जाएं",
            'services_title': "📋 <b>सेवाएं</b> - {category}",
            'services_page_info': " (पृष्ठ {current_page}/{total_pages})",
            'services_description': "ऑर्डर देने के लिए एक सेवा चुनें:",
            'back_to_categories': "⬅️ वापस",
            'search_title': "🔍 <b>सेवाएं खोजें</b>",
            'search_description': "नाम से सेवाओं को खोजने के लिए कृपया एक खोज शब्द दर्ज करें:",
            'search_results': "🔍 <b>खोज परिणाम</b> - {term}",
            'no_results': "आपके खोज शब्द से मेल खाती कोई सेवा नहीं मिली। कृपया पुनः प्रयास करें।",
            'service_details': "📋 <b>सेवा विवरण</b>",
            'service_id': "🆔 सेवा आईडी: <code>{id}</code>",
            'service_name': "📝 नाम: {name}",
            'service_category': "📂 श्रेणी: {category}",
            'service_rate': "💰 दर: ${rate} प्रति 1000",
            'service_min': "⬇️ न्यूनतम: {min}",
            'service_max': "⬆️ अधिकतम: {max}",
            'service_description': "📄 विवरण: {description}",
            'place_order': "🛒 ऑर्डर दें",
            'back_to_services': "🔙 सेवाओं पर वापस जाएं",
            'error_service_details': "सेवा विवरण दिखाने में त्रुटि। कृपया पुनः प्रयास करें।",
            'error_search': "खोज शुरू करने में त्रुटि। कृपया पुनः प्रयास करें।",
            'error_display': "सेवाएं प्रदर्शित करने में त्रुटि। कृपया पुनः प्रयास करें।"
        },
        'order': {
            'processing': "⏳ <b>ऑर्डर प्रोसेस हो रहा है...</b>\n\nआपका ऑर्डर वेबसाइट पर रखा जा रहा है। कृपया प्रतीक्षा करें...",
            'success': "✅ <b>ऑर्डर सफलतापूर्वक रखा गया!{admin_note}</b>\n\nऑर्डर आईडी: <code>{order_id}</code>\nसेवा: {service_name}\nमात्रा: {quantity}\nकीमत: {price_display}\n\nआपका ऑर्डर वेबसाइट पर भेज दिया गया है और प्रोसेस किया जा रहा है।\nआप /status कमांड से अपने ऑर्डर की स्थिति जांच सकते हैं।",
            'failed': "❌ <b>ऑर्डर विफल</b>\n\nत्रुटि: {error_message}\n\nआपका ऑर्डर वेबसाइट पर नहीं रखा जा सका। कृपया बाद में पुनः प्रयास करें या सपोर्ट से संपर्क करें।",
            'error': "❌ <b>ऑर्डर विफल</b>\n\nएक अप्रत्याशित त्रुटि हुई: {error}\n\nकृपया बाद में पुनः प्रयास करें या सपोर्ट से संपर्क करें।",
            'quantity_set': "✅ मात्रा सेट की गई: {quantity}\n\nकृपया एक लिंक या उपयोगकर्ता नाम प्रदान करें:",
            'invalid_quantity': "⚠️ कृपया मात्रा के लिए एक वैध संख्या दर्ज करें।",
            'insufficient_balance': "❌ <b>अपर्याप्त बैलेंस</b>\n\nआवश्यक: ${price:.6f} / ETB {etb_price:.2f}\nआपका बैलेंस: ${user_balance:.6f} / ETB {etb_balance:.2f}\n\nऑर्डर देने से पहले कृपया अपने अकाउंट में फंड जोड़ें।",
            'enter_link': "कृपया उस पोस्ट/प्रोफाइल का लिंक भेजें जिसे आप बूस्ट करना चाहते हैं:",
            'select_service_first': "कृपया पहले सर्विसेज बटन या /services कमांड का उपयोग करके एक सेवा चुनें।",
            'order_summary': "📋 <b>ऑर्डर सारांश</b>\n\nसेवा: {service_name}\nलिंक: {link}\nमात्रा: {quantity}\nकीमत: {price_display}\n\nकृपया अपने ऑर्डर की पुष्टि करें:",
            'min_quantity': "⚠️ इस सेवा के लिए न्यूनतम मात्रा {min_quantity} है। कृपया उच्च मात्रा दर्ज करें।",
            'max_quantity': "⚠️ इस सेवा के लिए अधिकतम मात्रा {max_quantity} है। कृपया कम मात्रा दर्ज करें।",
            'order_quantity': "📊 <b>ऑर्डर मात्रा</b>",
            'please_select_quantity': "कृपया वह मात्रा चुनें जिसे आप ऑर्डर करना चाहते हैं:"
        },
        'help': {
            'title': "❓ <b>Help & Support</b>",
            'description': "If you need assistance or have any questions, please contact our support team.",
            'contact_admin': "📞 Contact Admin",
            'back_to_menu': "◀️ Back to Main Menu",
            'contact_support': "💬 Contact Support"
        },
        'referrals': {
            'title': "रेफरल प्रोग्राम",
            'description': "अपने दोस्तों को हमारी सेवा में शामिल होने के लिए आमंत्रित करें और पुरस्कार प्राप्त करें! अपने अद्वितीय रेफरल लिंक को दोस्तों के साथ साझा करें और जब वे खरीदारी करें तो कमीशन कमाएं।",
            'your_link': "आपका रेफरल लिंक",
            'stats': "आपके रेफरल आंकड़े",
            'total_referrals': "कुल रेफरल",
            'how_it_works': "यह कैसे काम करता है:\n1. अपने रेफरल लिंक को दोस्तों के साथ साझा करें\n2. जब वे आपके लिंक का उपयोग करके शामिल होते हैं, तो उन्हें आपके रेफरल के रूप में गिना जाएगा\n3. जब कोई आपके लिंक का उपयोग करके शामिल होता है तो आपको सूचनाएं प्राप्त होंगी",
            'share': "📤 अपना लिंक साझा करें",
            'share_text': "इस अद्भुत SMM पैनल बॉट पर मेरे साथ जुड़ें! मेरा रेफरल लिंक उपयोग करें:",
            'back_to_menu': "◀️ मुख्य मेनू पर वापस जाएं",
            'new_referral': "🎉 <b>नया रेफरल!</b>\n\nकोई अभी आपके रेफरल लिंक का उपयोग करके शामिल हुआ है!",
            'welcome_referred': "👋 <b>स्वागत है!</b>\n\nआप एक रेफरल लिंक के माध्यम से शामिल हुए हैं। हमारी सेवाओं का आनंद लें!",
            'check_referrals': "मेरे रेफरल देखें",
            'no_referrals': "आपके पास अभी तक कोई रेफरल नहीं है। शुरू करने के लिए अपना रेफरल लिंक दोस्तों के साथ साझा करें!",
            'referrals_list': "ये वे उपयोगकर्ता हैं जो आपके रेफरल लिंक का उपयोग करके शामिल हुए हैं",
            'back_to_referrals': "◀️ रेफरल पर वापस जाएं"
        },
        'support': {
            'title': "💬 <b>Customer Support</b>",
            'description': "Need help? You can send a message directly to our support team. We'll get back to you as soon as possible.",
            'start_chat': "📝 Start Support Chat",
            'back_to_menu': "◀️ Back to Main Menu",
            'chat_started': "✅ <b>Support chat started!</b>\n\nPlease type your message below. Our team will respond as soon as possible.",
            'message_sent': "✅ Your message has been sent to our support team. We'll respond as soon as possible.",
            'chat_ended': "✅ Support chat has ended. If you need further assistance, you can start a new chat anytime.",
            'admin_notification': "📩 <b>New support message from user:</b>\n\nFrom: {user_info}\nUser ID: <code>{user_id}</code>\n\n<b>Message:</b>\n{message}",
            'reply_prompt': "✍️ Please type your reply to the user:",
            'reply_sent': "✅ Your reply has been sent to the user.",
            'reply_from_admin': "📩 <b>Reply from support team:</b>\n\n{message}",
            'admin_reply_header': "📩 <b>Reply from support team:</b>",
            'admin_has_replied': "✅ A support team member has joined the chat. You can continue your conversation.",
            'no_permission': "❌ You don't have permission to use this command.",
            'waiting_for_reply': "⏳ Please wait for our support team to respond to your message.",
            'end_chat': "❌ End Chat"
        },
        'tutorial': {
            'title': "📚 <b>Tutorials</b>",
            'select_tutorial': "Select a tutorial to learn how to use different features of the bot:",
            'back_to_tutorials': "◀️ Back to Tutorials",
            'back_to_menu': "🏠 Main Menu",
            'admin_manage': "🔧 Admin: Manage Tutorials",
            'edit_text': "✏️ Edit Text",
            'add_media': "🖼️ Add Media",
            'delete_media': "🗑️ Delete Media",
            'no_content': "This tutorial is currently being updated. Please check back later."
        }
    },
    'es': {  # Spanish
        'welcome': (
            "🌉 Welcome to KabirBridge!\n\n"
            "Your gateway to quick and efficient online services.\n\n"
            "✅ How to Use:\n"
            "1️⃣ Tap Services to browse available options.\n"
            "2️⃣ Select your desired service and follow the process.\n"
            "3️⃣ Complete your order and let the bot do the rest!\n\n"
            "💵 Payments: Safe and convenient payment options.\n"
            "📞 Support: +251907806267, @muay011\n\n"
            "🔹 Start now and experience instant results!"
        ),
        'select_language': "🌐 Por favor, selecciona tu idioma preferido:",
        'language_changed': "✅ ¡El idioma ha sido cambiado con éxito!",
        'main_menu': {
            'services': "🛒 Servicios",
            'place_order': "📦 Realizar Pedido",
            'balance': "💰 Saldo",
            'order_status': "📊 Estado del Pedido",
            'recharge': "💳 Recargar",
            'help': "❓ Ayuda",
            'languages': "🌐 Idiomas",
            'referrals': "👥 Referencias",
            'support': "Customer Support",
            'tutorial': "📚 Tutorials"
        },
        'balance': {
            'title': "💰 <b>Tu Saldo</b>",
            'current_balance_usd': "Saldo Actual: <code>${balance:.2f}</code>",
            'current_balance_etb': "Saldo Actual: <code>ETB {formatted_etb}</code> (≈${balance:.2f})",
            'recent_transactions': "📝 <b>Transacciones Recientes:</b>",
            'no_transactions': "No se encontraron transacciones recientes.",
            'add_balance_note': "Para añadir saldo, por favor contacta al administrador.",
            'refresh_button': "🔄 Actualizar",
            'refreshed': "Saldo actualizado",
            'up_to_date': "El saldo está actualizado",
            'error_message': "❌ Ocurrió un error al obtener tu saldo. Por favor, inténtalo más tarde.",
            'error_refresh': "❌ Ocurrió un error al actualizar tu saldo. Por favor, inténtalo más tarde."
        },
        'status': {
            'title': "📦 <b>Verificar Estado del Pedido</b>",
            'enter_order_id': "Por favor, ingrese el ID del pedido que desea verificar.\nEjemplo: <code>1234567</code>\n\nO haga clic en el botón de abajo para ver sus IDs de pedidos recientes:",
            'show_order_ids': "📋 Mostrar Mis IDs de Pedidos",
            'back_to_main': "◀️ Volver al Menú Principal",
            'no_orders': "Aún no tienes ningún pedido. Usa /services para explorar los servicios disponibles y realizar un pedido.",
            'your_order_ids': "📋 <b>Tus IDs de Pedidos</b>\n\nCopia cualquier ID y envíalo para verificar su estado:",
            'back': "◀️ Volver",
            'order_status': "📦 <b>Estado del Pedido</b>",
            'order_id': "🔢 ID del Pedido: <code>{order_id}</code>",
            'service': "🛍️ Servicio: {service_name}",
            'quantity': "🔢 Cantidad: {quantity}",
            'status': "📊 Estado: {status}",
            'price': "💰 Precio: ${price:.6f} / ETB {etb_price:.2f}",
            'start_count': "⏳ Recuento Inicial: {start_count}",
            'remains': "⌛ Restante: {remains}",
            'refresh': "🔄 Actualizar",
            'status_up_to_date': "¡El estado ya está actualizado!",
            'error_updating': "Error al actualizar el estado",
            'order_not_found': "⚠️ Pedido no encontrado o no accesible",
            'error_checking': "⚠️ Ocurrió un error al verificar el estado del pedido: {error}"
        },
        'recharge': {
            'title': "💳 <b>Recargar Cuenta</b>",
            'select_payment_method': "Por favor, selecciona tu método de pago preferido:",
            'select_amount': "Por favor, selecciona la cantidad que deseas recargar:\n\nElige entre las cantidades predefinidas o haz clic en 'Cantidad Personalizada' para ingresar tu propia cantidad.",
            'custom_amount_usd': "💰 Por favor, ingresa la cantidad que deseas recargar (en USD):\nEjemplo: <code>50</code> para $50",
            'custom_amount_etb': "💰 Por favor, ingresa la cantidad que deseas recargar (en ETB):\nEjemplo: <code>1000</code> para ETB 1000",
            'minimum_amount_usd': "❌ Por favor, ingresa una cantidad válida mayor a $1.",
            'minimum_amount_etb': "❌ La cantidad mínima de recarga para bancos etíopes es <b>ETB 100</b>.\nPor favor, ingresa una cantidad mayor.",
            'invalid_amount': "❌ Por favor, ingresa un número válido.\nEjemplo: <code>500</code> para {currency}500",
            'payment_verified': "✅ <b>¡Pago Verificado!</b>\n\nTu pago de <code>${amount:.2f}</code> ha sido verificado.\nLa cantidad ha sido añadida a tu saldo.\n\nUsa /account para verificar tu saldo actualizado.",
            'payment_verified_etb': "✅ <b>¡Pago Verificado!</b>\n\nTu pago de <code>ETB {formatted_etb}</code> (≈${amount:.2f}) ha sido verificado.\nLa cantidad ha sido añadida a tu saldo.\n\nTu saldo ahora se mostrará en ETB.\n\nUsa /account para verificar tu saldo actualizado.",
            'payment_rejected': "❌ <b>Pago Rechazado</b>\n\nTu pago de <code>${amount:.2f}</code> no fue verificado.\nPor favor, contacta a {admin_username} para más información.\n\nUsa /recharge para intentarlo de nuevo.",
            'cancelled': "❌ Recarga cancelada. Usa /recharge para comenzar de nuevo.",
            'custom_amount': "💰 Cantidad Personalizada",
            'back': "🔙 Volver",
            'cancel': "❌ Cancelar",
            'wise': "🌐 Wise (Internacional)",
            'eth_banks': "🏦 Bancos Etíopes",
            'intl_options': "🌍 Otras Opciones Internacionales",
            'crypto': "₿ Criptomoneda"
        },
        'services': {
            'platforms_title': "📱 <b>Plataformas de Servicio</b>",
            'platforms_description': "Por favor, selecciona una plataforma, busca servicios o ve todos los servicios:",
            'all_services': "🔍 Todos los Servicios",
            'search_services': "🔎 Buscar Servicios",
            'platform_button': "📱 {platform} ({count})",
            'error_retrieving': "Error al recuperar servicios. Por favor, inténtalo de nuevo más tarde.",
            'categories_title': "📂 <b>Categorías</b> - {platform}",
            'categories_description': "Por favor, selecciona una categoría:",
            'all_categories': "📂 Todas las Categorías",
            'back_to_platforms': "⬅️ Volver a Plataformas",
            'services_title': "📋 <b>Servicios</b> - {category}",
            'services_page_info': " (Página {current_page}/{total_pages})",
            'services_description': "Selecciona un servicio para realizar un pedido:",
            'back_to_categories': "⬅️ Volver",
            'search_title': "🔍 <b>Buscar Servicios</b>",
            'search_description': "Por favor, introduce un término de búsqueda para encontrar servicios por nombre:",
            'search_results': "🔍 <b>Resultados de Búsqueda</b> - {term}",
            'no_results': "No se encontraron servicios que coincidan con tu término de búsqueda. Por favor, inténtalo de nuevo.",
            'service_details': "📋 <b>Detalles del Servicio</b>",
            'service_id': "🆔 ID del Servicio: <code>{id}</code>",
            'service_name': "📝 Nombre: {name}",
            'service_category': "📂 Categoría: {category}",
            'service_rate': "💰 Tarifa: ${rate} por 1000",
            'service_min': "⬇️ Mínimo: {min}",
            'service_max': "⬆️ Máximo: {max}",
            'service_description': "📄 Descripción: {description}",
            'place_order': "🛒 Realizar Pedido",
            'back_to_services': "🔙 Volver a Servicios",
            'error_service_details': "Error al mostrar detalles del servicio. Por favor, inténtalo de nuevo.",
            'error_search': "Error al iniciar la búsqueda. Por favor, inténtalo de nuevo.",
            'error_display': "Error al mostrar servicios. Por favor, inténtalo de nuevo."
        },
        'order': {
            'processing': "⏳ <b>Procesando Pedido...</b>\n\nSu pedido está siendo colocado en el sitio web. Por favor espere...",
            'success': "✅ <b>¡Pedido Realizado con Éxito!{admin_note}</b>\n\nID del Pedido: <code>{order_id}</code>\nServicio: {service_name}\nCantidad: {quantity}\nPrecio: {price_display}\n\nSu pedido ha sido enviado al sitio web y está siendo procesado.\nPuede verificar el estado de su pedido con el comando /status.",
            'failed': "❌ <b>Pedido Fallido</b>\n\nError: {error_message}\n\nSu pedido no pudo ser colocado en el sitio web. Por favor intente nuevamente más tarde o contacte a soporte.",
            'error': "❌ <b>Pedido Fallido</b>\n\nOcurrió un error inesperado: {error}\n\nPor favor intente nuevamente más tarde o contacte a soporte.",
            'quantity_set': "✅ Cantidad establecida a: {quantity}\n\nPor favor proporcione un enlace o nombre de usuario:",
            'invalid_quantity': "⚠️ Por favor ingrese un número válido para la cantidad.",
            'insufficient_balance': "❌ <b>Saldo Insuficiente</b>\n\nRequerido: ${price:.6f} / ETB {etb_price:.2f}\nSu saldo: ${user_balance:.6f} / ETB {etb_balance:.2f}\n\nPor favor agregue fondos a su cuenta antes de realizar el pedido.",
            'enter_link': "Por favor envíe el enlace a la publicación/perfil que desea impulsar:",
            'select_service_first': "Por favor seleccione un servicio primero usando el botón de Servicios o el comando /services.",
            'order_summary': "📋 <b>Resumen del Pedido</b>\n\nServicio: {service_name}\nEnlace: {link}\nCantidad: {quantity}\nPrecio: {price_display}\n\nPor favor confirme su pedido:",
            'min_quantity': "⚠️ La cantidad mínima para este servicio es {min_quantity}. Por favor ingrese una cantidad mayor.",
            'max_quantity': "⚠️ La cantidad máxima para este servicio es {max_quantity}. Por favor ingrese una cantidad menor.",
            'order_quantity': "📊 <b>Cantidad del Pedido</b>",
            'please_select_quantity': "Por favor seleccione la cantidad que desea ordenar:"
        },
        'help': {
            'title': "❓ <b>Help & Support</b>",
            'description': "If you need assistance or have any questions, please contact our support team.",
            'contact_admin': "📞 Contact Admin",
            'back_to_menu': "◀️ Back to Main Menu"
        },
        'referrals': {
            'title': "Programa de Referencias",
            'description': "¡Invita a tus amigos a unirse a nuestro servicio y gana recompensas! Comparte tu enlace de referencia único con amigos y gana una comisión cuando realicen compras.",
            'your_link': "Tu Enlace de Referencia",
            'stats': "Tus Estadísticas de Referencias",
            'total_referrals': "Total de Referencias",
            'how_it_works': "Cómo funciona:\n1. Comparte tu enlace de referencia con amigos\n2. Cuando se unan usando tu enlace, se contarán como tu referencia\n3. Recibirás notificaciones cuando alguien se una usando tu enlace",
            'share': "📤 Compartir Tu Enlace",
            'share_text': "¡Únete a mí en este increíble Bot de Panel SMM! Usa mi enlace de referencia:",
            'back_to_menu': "◀️ Volver al Menú Principal",
            'new_referral': "🎉 <b>¡Nueva Referencia!</b>\n\n¡Alguien acaba de unirse usando tu enlace de referencia!",
            'welcome_referred': "👋 <b>¡Bienvenido!</b>\n\nTe has unido a través de un enlace de referencia. ¡Disfruta de nuestros servicios!",
            'check_referrals': "Ver Mis Referencias",
            'no_referrals': "Aún no tienes referencias. ¡Comparte tu enlace de referencia con amigos para comenzar!",
            'referrals_list': "Estos son los usuarios que se unieron usando tu enlace de referencia",
            'back_to_referrals': "◀️ Volver a Referencias"
        },
        'support': {
            'title': "💬 <b>Customer Support</b>",
            'description': "Need help? You can send a message directly to our support team. We'll get back to you as soon as possible.",
            'start_chat': "📝 Start Support Chat",
            'back_to_menu': "◀️ Back to Main Menu",
            'chat_started': "✅ <b>Support chat started!</b>\n\nPlease type your message below. Our team will respond as soon as possible.",
            'message_sent': "✅ Your message has been sent to our support team. We'll respond as soon as possible.",
            'chat_ended': "✅ Support chat has ended. If you need further assistance, you can start a new chat anytime.",
            'admin_notification': "📩 <b>New support message from user:</b>\n\nFrom: {user_info}\nUser ID: <code>{user_id}</code>\n\n<b>Message:</b>\n{message}",
            'reply_prompt': "✍️ Please type your reply to the user:",
            'reply_sent': "✅ Your reply has been sent to the user.",
            'reply_from_admin': "📩 <b>Reply from support team:</b>\n\n{message}",
            'no_permission': "❌ You don't have permission to use this command."
        },
        'tutorial': {
            'title': "📚 <b>Tutorials</b>",
            'select_tutorial': "Select a tutorial to learn how to use different features of the bot:",
            'back_to_tutorials': "◀️ Back to Tutorials",
            'back_to_menu': "🏠 Main Menu",
            'admin_manage': "🔧 Admin: Manage Tutorials",
            'edit_text': "✏️ Edit Text",
            'add_media': "🖼️ Add Media",
            'delete_media': "🗑️ Delete Media",
            'no_content': "This tutorial is currently being updated. Please check back later."
        }
    },
    'zh': {  # Chinese
        'welcome': (
            "🌉 Welcome to KabirBridge!\n\n"
            "Your gateway to quick and efficient online services.\n\n"
            "✅ How to Use:\n"
            "1️⃣ Tap Services to browse available options.\n"
            "2️⃣ Select your desired service and follow the process.\n"
            "3️⃣ Complete your order and let the bot do the rest!\n\n"
            "💵 Payments: Safe and convenient payment options.\n"
            "📞 Support: +251907806267, @muay011\n\n"
            "🔹 Start now and experience instant results!"
        ),
        'select_language': "🌐 请选择您的首选语言：",
        'language_changed': "✅ 语言已成功更改！",
        'main_menu': {
            'services': "🛒 服务",
            'place_order': "📦 下订单",
            'balance': "💰 余额",
            'order_status': "📊 订单状态",
            'recharge': "💳 充值",
            'help': "❓ 帮助",
            'languages': "🌐 语言",
            'support': "Customer Support",
            'tutorial': "📚 教程"
        },
        'balance': {
            'title': "💰 <b>您的余额</b>",
            'current_balance_usd': "当前余额: <code>${balance:.2f}</code>",
            'current_balance_etb': "当前余额: <code>ETB {formatted_etb}</code> (≈${balance:.2f})",
            'recent_transactions': "📝 <b>最近交易:</b>",
            'no_transactions': "未找到最近交易。",
            'add_balance_note': "要添加余额，请联系管理员。",
            'refresh_button': "🔄 刷新",
            'refreshed': "余额已刷新",
            'up_to_date': "余额已是最新",
            'error_message': "❌ 获取余额时发生错误。请稍后再试。",
            'error_refresh': "❌ 刷新余额时发生错误。请稍后再试。"
        },
        'status': {
            'title': "📦 <b>查询订单状态</b>",
            'enter_order_id': "请输入您要查询的订单ID。\n示例: <code>1234567</code>\n\n或点击下方按钮查看您的最近订单ID:",
            'show_order_ids': "📋 显示我的订单ID",
            'back_to_main': "◀️ 返回主菜单",
            'no_orders': "您还没有任何订单。使用 /services 浏览可用服务并下单。",
            'your_order_ids': "📋 <b>您的订单ID</b>\n\n复制任意ID并发送以查询其状态:",
            'back': "◀️ 返回",
            'order_status': "📦 <b>订单状态</b>",
            'order_id': "🔢 订单ID: <code>{order_id}</code>",
            'service': "🛍️ 服务: {service_name}",
            'quantity': "🔢 数量: {quantity}",
            'status': "📊 状态: {status}",
            'price': "💰 价格: ${price:.6f} / ETB {etb_price:.2f}",
            'start_count': "⏳ 起始数量: {start_count}",
            'remains': "⌛ 剩余: {remains}",
            'refresh': "🔄 刷新",
            'status_up_to_date': "状态已是最新!",
            'error_updating': "更新状态时出错",
            'order_not_found': "⚠️ 未找到订单或无法访问",
            'error_checking': "⚠️ 检查订单状态时发生错误: {error}"
        },
        'recharge': {
            'title': "💳 <b>充值账户</b>",
            'select_payment_method': "请选择您的首选支付方式：",
            'select_amount': "请选择您要充值的金额：\n\n从预设金额中选择或点击'自定义金额'输入您自己的金额。",
            'custom_amount_usd': "💰 请输入您要充值的金额（以美元为单位）：\n示例：<code>50</code> 表示 $50",
            'custom_amount_etb': "💰 请输入您要充值的金额（以埃塞俄比亚比尔为单位）：\n示例：<code>1000</code> 表示 ETB 1000",
            'minimum_amount_usd': "❌ 请输入大于 $1 的有效金额。",
            'minimum_amount_etb': "❌ 埃塞俄比亚银行的最低充值金额为 <b>ETB 100</b>。\n请输入更高的金额。",
            'invalid_amount': "❌ 请输入有效的数字。\n示例：<code>500</code> 表示 {currency}500",
            'payment_verified': "✅ <b>支付已验证！</b>\n\n您的 <code>${amount:.2f}</code> 支付已验证。\n该金额已添加到您的余额中。\n\n使用 /account 查看您的更新余额。",
            'payment_verified_etb': "✅ <b>支付已验证！</b>\n\n您的 <code>ETB {formatted_etb}</code> (≈${amount:.2f}) 支付已验证。\n该金额已添加到您的余额中。\n\n您的余额现在将以埃塞俄比亚比尔显示。\n\n使用 /account 查看您的更新余额。",
            'payment_rejected': "❌ <b>支付被拒绝</b>\n\n您的 <code>${amount:.2f}</code> 支付未验证。\n请联系 {admin_username} 获取更多信息。\n\n使用 /recharge 重试。",
            'cancelled': "❌ 充值已取消。使用 /recharge 重新开始。",
            'custom_amount': "💰 自定义金额",
            'back': "🔙 返回",
            'cancel': "❌ 取消",
            'wise': "🌐 Wise（国际）",
            'eth_banks': "🏦 埃塞俄比亚银行",
            'intl_options': "🌍 其他国际选项",
            'crypto': "₿ 加密货币"
        },
        'services': {
            'platforms_title': "📱 <b>服务平台</b>",
            'platforms_description': "请选择一个平台，搜索服务，或查看所有服务：",
            'all_services': "🔍 所有服务",
            'search_services': "🔎 搜索服务",
            'platform_button': "📱 {platform} ({count})",
            'error_retrieving': "获取服务时出错。请稍后再试。",
            'categories_title': "📂 <b>类别</b> - {platform}",
            'categories_description': "请选择一个类别：",
            'all_categories': "📂 所有类别",
            'back_to_platforms': "⬅️ 返回平台",
            'services_title': "📋 <b>服务</b> - {category}",
            'services_page_info': " (第 {current_page}/{total_pages} 页)",
            'services_description': "选择一个服务下单：",
            'back_to_categories': "⬅️ 返回",
            'search_title': "🔍 <b>搜索服务</b>",
            'search_description': "请输入搜索词以按名称查找服务：",
            'search_results': "🔍 <b>搜索结果</b> - {term}",
            'no_results': "未找到与您的搜索词匹配的服务。请重试。",
            'service_details': "📋 <b>服务详情</b>",
            'service_id': "🆔 服务ID: <code>{id}</code>",
            'service_name': "📝 名称: {name}",
            'service_category': "📂 类别: {category}",
            'service_rate': "💰 费率: ${rate} 每1000",
            'service_min': "⬇️ 最小值: {min}",
            'service_max': "⬆️ 最大值: {max}",
            'service_description': "📄 描述: {description}",
            'place_order': "🛒 下单",
            'back_to_services': "🔙 返回服务",
            'error_service_details': "显示服务详情时出错。请重试。",
            'error_search': "启动搜索时出错。请重试。",
            'error_display': "显示服务时出错。请重试。"
        },
        'order': {
            'processing': "⏳ <b>处理订单中...</b>\n\n您的订单正在网站上处理。请稍等...",
            'success': "✅ <b>订单成功提交！{admin_note}</b>\n\n订单ID: <code>{order_id}</code>\n服务: {service_name}\n数量: {quantity}\n价格: {price_display}\n\n您的订单已提交到网站，正在处理中。您可以使用 /status 命令检查订单状态。",
            'failed': "❌ <b>订单失败</b>\n\n错误: {error_message}\n\n您的订单无法在网站上提交。请稍后再试或联系支持。",
            'error': "❌ <b>订单失败</b>\n\n发生了意外错误: {error}\n\n请稍后再试或联系支持。",
            'quantity_set': "✅ 数量已设置为: {quantity}\n\n请提供链接或用户名:",
            'invalid_quantity': "⚠️ 请输入有效的数量。",
            'insufficient_balance': "❌ <b>余额不足</b>\n\n所需: ${price:.6f} / ETB {etb_price:.2f}\n您的余额: ${user_balance:.6f} / ETB {etb_balance:.2f}\n\n请在下单前向您的账户添加资金。",
            'enter_link': "请提供要推广的帖子/个人资料的链接:",
            'select_service_first': "请先使用服务按钮或 /services 命令选择服务。",
            'order_summary': "📋 <b>订单摘要</b>\n\n服务: {service_name}\n链接: {link}\n数量: {quantity}\n价格: {price_display}\n\n请确认您的订单:",
            'min_quantity': "⚠️ 此服务的最小数量为 {min_quantity}。请输入更高的数量。",
            'max_quantity': "⚠️ 此服务的最大数量为 {max_quantity}。请输入更低数量。",
            'order_quantity': "📊 <b>订单数量</b>",
            'please_select_quantity': "请选择您要订购的数量:"
        },
        'support': {
            'title': "💬 <b>Customer Support</b>",
            'description': "Need help? You can send a message directly to our support team. We'll get back to you as soon as possible.",
            'start_chat': "📝 Start Support Chat",
            'back_to_menu': "◀️ Back to Main Menu",
            'chat_started': "✅ <b>Support chat started!</b>\n\nPlease type your message below. Our team will respond as soon as possible.",
            'message_sent': "✅ Your message has been sent to our support team. We'll respond as soon as possible.",
            'chat_ended': "✅ Support chat has ended. If you need further assistance, you can start a new chat anytime.",
            'admin_notification': "📩 <b>New support message from user:</b>\n\nFrom: {user_info}\nUser ID: <code>{user_id}</code>\n\n<b>Message:</b>\n{message}",
            'reply_prompt': "✍️ Please type your reply to the user:",
            'reply_sent': "✅ Your reply has been sent to the user.",
            'reply_from_admin': "📩 <b>Reply from support team:</b>\n\n{message}",
            'no_permission': "❌ You don't have permission to use this command.",
            'waiting_for_reply': "⏳ Please wait for our support team to respond to your message.",
            'end_chat': "❌ End Chat"
        },
        'tutorial': {
            'title': "📚 <b>Tutorials</b>",
            'select_tutorial': "Select a tutorial to learn how to use different features of the bot:",
            'back_to_tutorials': "◀️ Back to Tutorials",
            'back_to_menu': "🏠 Main Menu",
            'admin_manage': "🔧 Admin: Manage Tutorials",
            'edit_text': "✏️ Edit Text",
            'add_media': "🖼️ Add Media",
            'delete_media': "🗑️ Delete Media",
            'no_content': "This tutorial is currently being updated. Please check back later."
        }
    },
    'tr': {  # Turkish
        'welcome': (
            "🌉 Welcome to KabirBridge!\n\n"
            "Your gateway to quick and efficient online services.\n\n"
            "✅ How to Use:\n"
            "1️⃣ Tap Services to browse available options.\n"
            "2️⃣ Select your desired service and follow the process.\n"
            "3️⃣ Complete your order and let the bot do the rest!\n\n"
            "💵 Payments: Safe and convenient payment options.\n"
            "📞 Support: +251907806267, @muay011\n\n"
            "🔹 Start now and experience instant results!"
        ),
        'select_language': "🌐 Lütfen tercih ettiğiniz dili seçin:",
        'language_changed': "✅ Dil başarıyla değiştirildi!",
        'main_menu': {
            'services': "🛒 Hizmetler",
            'place_order': "📦 Sipariş Ver",
            'balance': "💰 Bakiye",
            'order_status': "📊 Sipariş Durumu",
            'recharge': "💳 Yükleme",
            'help': "❓ Yardım",
            'languages': "🌐 Diller",
            'support': "Customer Support",
            'tutorial': "📚 Tutorials"
        },
        'balance': {
            'title': "💰 <b>Bakiyeniz</b>",
            'current_balance_usd': "Mevcut Bakiye: <code>${balance:.2f}</code>",
            'current_balance_etb': "Mevcut Bakiye: <code>ETB {formatted_etb}</code> (≈${balance:.2f})",
            'recent_transactions': "📝 <b>Son İşlemler:</b>",
            'no_transactions': "Son işlem bulunamadı.",
            'add_balance_note': "Bakiye eklemek için lütfen yönetici ile iletişime geçin.",
            'refresh_button': "🔄 Yenile",
            'refreshed': "Bakiye yenilendi",
            'up_to_date': "Bakiye güncel",
            'error_message': "❌ Bakiyeniz alınırken bir hata oluştu. Lütfen daha sonra tekrar deneyin.",
            'error_refresh': "❌ Bakiyeniz yenilenirken bir hata oluştu. Lütfen daha sonra tekrar deneyin."
        },
        'status': {
            'title': "📦 <b>Sipariş Durumunu Kontrol Et</b>",
            'enter_order_id': "Lütfen kontrol etmek istediğiniz sipariş ID'sini girin.\nÖrnek: <code>1234567</code>\n\nVeya son sipariş ID'lerinizi görmek için aşağıdaki düğmeye tıklayın:",
            'show_order_ids': "📋 Sipariş ID'lerimi Göster",
            'back_to_main': "◀️ Ana Menüye Dön",
            'no_orders': "Henüz hiç siparişiniz yok. Mevcut hizmetlere göz atmak ve sipariş vermek için /services komutunu kullanın.",
            'your_order_ids': "📋 <b>Sipariş ID'leriniz</b>\n\nDurumunu kontrol etmek için herhangi bir ID'yi kopyalayıp gönderin:",
            'back': "◀️ Geri",
            'order_status': "📦 <b>Sipariş Durumu</b>",
            'order_id': "🔢 Sipariş ID: <code>{order_id}</code>",
            'service': "🛍️ Hizmet: {service_name}",
            'quantity': "🔢 Miktar: {quantity}",
            'status': "📊 Durum: {status}",
            'price': "💰 Fiyat: ${price:.6f} / ETB {etb_price:.2f}",
            'start_count': "⏳ Başlangıç Sayısı: {start_count}",
            'remains': "⌛ Kalan: {remains}",
            'refresh': "🔄 Yenile",
            'status_up_to_date': "Durum zaten güncel!",
            'error_updating': "Durum güncellenirken hata oluştu",
            'order_not_found': "⚠️ Sipariş bulunamadı veya erişilemez",
            'error_checking': "⚠️ Sipariş durumu kontrol edilirken bir hata oluştu: {error}"
        },
        'recharge': {
            'title': "💳 <b>Hesap Yükleme</b>",
            'select_payment_method': "Lütfen tercih ettiğiniz ödeme yöntemini seçin:",
            'select_amount': "Lütfen yüklemek istediğiniz tutarı seçin:\n\nÖnceden belirlenmiş tutarlardan seçin veya kendi tutarınızı girmek için 'Özel Tutar'a tıklayın.",
            'custom_amount_usd': "💰 Lütfen yüklemek istediğiniz tutarı girin (USD cinsinden):\nÖrnek: <code>50</code> $50 için",
            'custom_amount_etb': "💰 Lütfen yüklemek istediğiniz tutarı girin (ETB cinsinden):\nÖrnek: <code>1000</code> ETB 1000 için",
            'minimum_amount_usd': "❌ Lütfen $1'dan büyük geçerli bir tutar girin.",
            'minimum_amount_etb': "❌ Etiyopya bankaları için minimum yükleme tutarı <b>ETB 100</b>'dir.\nLütfen daha yüksek bir tutar girin.",
            'invalid_amount': "❌ Lütfen geçerli bir sayı girin.\nÖrnek: <code>500</code> {currency}500 için",
            'payment_verified': "✅ <b>Ödeme Doğrulandı!</b>\n\n<code>${amount:.2f}</code> tutarındaki ödemeniz doğrulandı.\nTutar bakiyenize eklendi.\n\nGüncellenmiş bakiyenizi kontrol etmek için /account komutunu kullanın.",
            'payment_verified_etb': "✅ <b>Ödeme Doğrulandı!</b>\n\n<code>ETB {formatted_etb}</code> (≈${amount:.2f}) tutarındaki ödemeniz doğrulandı.\nTutar bakiyenize eklendi.\n\nBakiyeniz artık ETB cinsinden gösterilecek.\n\nGüncellenmiş bakiyenizi kontrol etmek için /account komutunu kullanın.",
            'payment_rejected': "❌ <b>Ödeme Reddedildi</b>\n\n<code>${amount:.2f}</code> tutarındaki ödemeniz doğrulanmadı.\nDaha fazla bilgi için lütfen {admin_username} ile iletişime geçin.\n\nTekrar denemek için /recharge komutunu kullanın.",
            'cancelled': "❌ Yükleme iptal edildi. Tekrar başlamak için /recharge komutunu kullanın.",
            'custom_amount': "💰 Özel Tutar",
            'back': "🔙 Geri",
            'cancel': "❌ İptal",
            'wise': "🌐 Wise (Uluslararası)",
            'eth_banks': "🏦 Etiyopya Bankaları",
            'intl_options': "🌍 Diğer Uluslararası Seçenekler",
            'crypto': "₿ Kripto Para"
        },
        'services': {
            'platforms_title': "📱 <b>Hizmet Platformları</b>",
            'platforms_description': "Lütfen bir platform seçin, hizmetleri arayın veya tüm hizmetleri görüntüleyin:",
            'all_services': "🔍 Tüm Hizmetler",
            'search_services': "🔎 Hizmetleri Ara",
            'platform_button': "📱 {platform} ({count})",
            'error_retrieving': "Hizmetler alınırken hata oluştu. Lütfen daha sonra tekrar deneyin.",
            'categories_title': "📂 <b>Kategoriler</b> - {platform}",
            'categories_description': "Lütfen bir kategori seçin:",
            'all_categories': "📂 Tüm Kategoriler",
            'back_to_platforms': "⬅️ Platformlara Dön",
            'services_title': "📋 <b>Hizmetler</b> - {category}",
            'services_page_info': " (Sayfa {current_page}/{total_pages})",
            'services_description': "Sipariş vermek için bir hizmet seçin:",
            'back_to_categories': "⬅️ Geri",
            'search_title': "🔍 <b>Hizmetleri Ara</b>",
            'search_description': "İsme göre hizmet bulmak için lütfen bir arama terimi girin:",
            'search_results': "🔍 <b>Arama Sonuçları</b> - {term}",
            'no_results': "Arama terimiyle eşleşen hizmet bulunamadı. Lütfen tekrar deneyin.",
            'service_details': "📋 <b>Hizmet Detayları</b>",
            'service_id': "🆔 Hizmet ID: <code>{id}</code>",
            'service_name': "📝 İsim: {name}",
            'service_category': "📂 Kategori: {category}",
            'service_rate': "💰 Ücret: ${rate} / 1000",
            'service_min': "⬇️ Minimum: {min}",
            'service_max': "⬆️ Maksimum: {max}",
            'service_description': "📄 Açıklama: {description}",
            'place_order': "🛒 Sipariş Ver",
            'back_to_services': "🔙 Hizmetlere Dön",
            'error_service_details': "Hizmet detayları gösterilirken hata oluştu. Lütfen tekrar deneyin.",
            'error_search': "Arama başlatılırken hata oluştu. Lütfen tekrar deneyin.",
            'error_display': "Hizmetler gösterilirken hata oluştu. Lütfen tekrar deneyin."
        },
        'order': {
            'processing': "⏳ <b>Sipariş İşleniyor...</b>\n\nSiparişiniz web sitesine yerleştiriliyor. Lütfen bekleyin...",
            'success': "✅ <b>Sipariş Başarıyla Verildi!{admin_note}</b>\n\nSipariş ID: <code>{order_id}</code>\nHizmet: {service_name}\nMiktar: {quantity}\nFiyat: {price_display}\n\nSiparişiniz web sitesine gönderildi ve işleniyor.\nSiparişinizin durumunu /status komutuyla kontrol edebilirsiniz.",
            'failed': "❌ <b>Sipariş Başarısız</b>\n\nHata: {error_message}\n\nSiparişiniz web sitesine yerleştirilemedi. Lütfen daha sonra tekrar deneyin veya destek ile iletişime geçin.",
            'error': "❌ <b>Sipariş Başarısız</b>\n\nBeklenmeyen bir hata oluştu: {error}\n\nLütfen daha sonra tekrar deneyin veya destek ile iletişime geçin.",
            'quantity_set': "✅ Miktar ayarlandı: {quantity}\n\nLütfen bir bağlantı veya kullanıcı adı girin:",
            'invalid_quantity': "⚠️ Lütfen miktar için geçerli bir sayı girin.",
            'insufficient_balance': "❌ <b>Yetersiz Bakiye</b>\n\nGerekli: ${price:.6f} / ETB {etb_price:.2f}\nBakiyeniz: ${user_balance:.6f} / ETB {etb_balance:.2f}\n\nLütfen sipariş vermeden önce hesabınıza para ekleyin.",
            'enter_link': "Lütfen artırmak istediğiniz gönderi/profil bağlantısını gönderin:",
            'select_service_first': "Lütfen önce Hizmetler düğmesini veya /services komutunu kullanarak bir hizmet seçin.",
            'order_summary': "📋 <b>Sipariş Özeti</b>\n\nHizmet: {service_name}\nBağlantı: {link}\nMiktar: {quantity}\nFiyat: {price_display}\n\nLütfen siparişinizi onaylayın:",
            'min_quantity': "⚠️ Bu hizmet için minimum miktar {min_quantity}. Lütfen daha yüksek bir miktar girin.",
            'max_quantity': "⚠️ Bu hizmet için maksimum miktar {max_quantity}. Lütfen daha düşük bir miktar girin.",
            'order_quantity': "📊 <b>Sipariş Miktarı</b>",
            'please_select_quantity': "Lütfen sipariş etmek istediğiniz miktarı seçin:"
        },
        'help': {
            'title': "❓ <b>Help & Support</b>",
            'description': "If you need assistance or have any questions, please contact our support team.",
            'contact_admin': "📞 Contact Admin",
            'back_to_menu': "◀️ Back to Main Menu"
        },
        'referrals': {
            'title': "Programa de Referencias",
            'description': "¡Invita a tus amigos a unirse a nuestro servicio y gana recompensas! Comparte tu enlace de referencia único con amigos y gana una comisión cuando realicen compras.",
            'your_link': "Tu Enlace de Referencia",
            'stats': "Tus Estadísticas de Referencias",
            'total_referrals': "Total de Referencias",
            'how_it_works': "Cómo funciona:\n1. Comparte tu enlace de referencia con amigos\n2. Cuando se unan usando tu enlace, se contarán como tu referencia\n3. Recibirás notificaciones cuando alguien se una usando tu enlace",
            'share': "📤 Compartir Tu Enlace",
            'share_text': "¡Únete a mí en este increíble Bot de Panel SMM! Usa mi enlace de referencia:",
            'back_to_menu': "◀️ Volver al Menú Principal",
            'new_referral': "🎉 <b>¡Nueva Referencia!</b>\n\n¡Alguien acaba de unirse usando tu enlace de referencia!",
            'welcome_referred': "👋 <b>¡Bienvenido!</b>\n\nTe has unido a través de un enlace de referencia. ¡Disfruta de nuestros servicios!",
            'check_referrals': "Ver Mis Referencias",
            'no_referrals': "Aún no tienes referencias. ¡Comparte tu enlace de referencia con amigos para comenzar!",
            'referrals_list': "Estos son los usuarios que se unieron usando tu enlace de referencia",
            'back_to_referrals': "◀️ Volver a Referencias"
        },
        'support': {
            'title': "💬 <b>Customer Support</b>",
            'description': "Need help? You can send a message directly to our support team. We'll get back to you as soon as possible.",
            'start_chat': "📝 Start Support Chat",
            'back_to_menu': "◀️ Back to Main Menu",
            'chat_started': "✅ <b>Support chat started!</b>\n\nPlease type your message below. Our team will respond as soon as possible.",
            'message_sent': "✅ Your message has been sent to our support team. We'll respond as soon as possible.",
            'chat_ended': "✅ Support chat has ended. If you need further assistance, you can start a new chat anytime.",
            'admin_notification': "📩 <b>New support message from user:</b>\n\nFrom: {user_info}\nUser ID: <code>{user_id}</code>\n\n<b>Message:</b>\n{message}",
            'reply_prompt': "✍️ Please type your reply to the user:",
            'reply_sent': "✅ Your reply has been sent to the user.",
            'reply_from_admin': "📩 <b>Reply from support team:</b>\n\n{message}",
            'admin_reply_header': "📩 <b>Reply from support team:</b>",
            'admin_has_replied': "✅ A support team member has joined the chat. You can continue your conversation.",
            'no_permission': "❌ You don't have permission to use this command.",
            'waiting_for_reply': "⏳ Please wait for our support team to respond to your message.",
            'end_chat': "❌ End Chat"
        },
        'tutorial': {
            'title': "📚 <b>Tutorials</b>",
            'select_tutorial': "Select a tutorial to learn how to use different features of the bot:",
            'back_to_tutorials': "◀️ Back to Tutorials",
            'back_to_menu': "🏠 Main Menu",
            'admin_manage': "🔧 Admin: Manage Tutorials",
            'edit_text': "✏️ Edit Text",
            'add_media': "🖼️ Add Media",
            'delete_media': "🗑️ Delete Media",
            'no_content': "This tutorial is currently being updated. Please check back later."
        }
    }
}

def get_message(language, key, subkey=None, default=None):
    """Get a message in the specified language
    
    Args:
        language (str): The language code
        key (str): The primary key in the messages dictionary
        subkey (str, optional): The secondary key for nested dictionaries
        default (str, optional): Default value to return if the key is not found
        
    Returns:
        str: The message in the specified language
    """
    logger.info(f"get_message called with language={language}, key={key}, subkey={subkey}")
    
    # First check if this is a custom message that should be loaded from the database
    if subkey is None and key in ['welcome']:
        # These keys can be customized in the database
        from utils.db import db
        custom_message = db.get_custom_message(key)
        if custom_message and custom_message.get('message_text'):
            logger.info(f"Found custom message for key {key} in database")
            return custom_message.get('message_text')
    
    # If no custom message found or if it's not a customizable message, proceed with regular messages
    if language not in MESSAGES:
        logger.warning(f"Language {language} not found in MESSAGES, defaulting to 'en'")
        language = 'en'  # Default to English if language not found
    
    if subkey is None:
        result = MESSAGES[language].get(key, MESSAGES['en'].get(key, default or ''))
        logger.info(f"Returning message for {language}.{key}: {result}")
        return result
    
    # Handle nested keys
    if key in MESSAGES[language] and isinstance(MESSAGES[language][key], dict) and subkey in MESSAGES[language][key]:
        result = MESSAGES[language][key][subkey]
        logger.info(f"Returning message for {language}.{key}.{subkey}: {result}")
        return result
    
    # Fallback to English if the key/subkey combination is not found
    if key in MESSAGES['en'] and isinstance(MESSAGES['en'][key], dict) and subkey in MESSAGES['en'][key]:
        result = MESSAGES['en'][key][subkey]
        logger.warning(f"Key {key}.{subkey} not found in language {language}, falling back to English: {result}")
        return result
    
    # Return the default value if provided, otherwise empty string
    logger.warning(f"Key {key}.{subkey} not found in any language, using default: {default}")
    return default or ''