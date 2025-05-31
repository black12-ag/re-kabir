#!/usr/bin/env python3
import os
import sys
import logging

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Add the current directory to the path so we can import the bot module
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

try:
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Print configuration for debugging
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    api_url = os.getenv('API_URL')
    admin_ids = os.getenv('ADMIN_USER_ID')
    
    print("Starting bot...")
    print(f"Bot token: {bot_token[:10]}... (token hidden)")
    print(f"API URL: {api_url}")
    print(f"Admin IDs: {admin_ids}")
    
    # Setup to keep the app alive on Railway
    PORT = int(os.environ.get('PORT', 8080))
    APP_URL = os.environ.get('APP_URL', '')
    WEBHOOK_MODE = os.environ.get('WEBHOOK_MODE', 'false').lower() == 'true'
    
    # Import and run the bot
    try:
        from bot.bot import main
        
        # If we're on Railway or webhook mode is enabled, run in webhook mode
        if 'RAILWAY_STATIC_URL' in os.environ or WEBHOOK_MODE:
            from bot.bot import webhook_main
            if 'APP_URL' not in os.environ and 'RAILWAY_STATIC_URL' in os.environ:
                # Set APP_URL from Railway URL if not set manually
                os.environ['APP_URL'] = os.environ['RAILWAY_STATIC_URL']
            print(f"Starting in webhook mode on port {PORT}")
            webhook_main(port=PORT)
        else:
            # Otherwise run in polling mode
            print("Starting in polling mode")
            main()
    except ImportError as e:
        # If bot module is not in a subdirectory
        logger.error(f"Could not import the bot module: {e}")
        logger.error("Make sure bot/bot.py exists")
        sys.exit(1)
            
except Exception as e:
    logger.error(f"Error running bot: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1) 