import logging
from telegram import Update
from telegram.ext import CallbackContext
from utils.db import db
from utils.api_client import api_client
from utils.messages import get_message

logger = logging.getLogger(__name__)

async def check_and_process_refunds(context: CallbackContext):
    """Check for refunded orders and process refunds to users"""
    try:
        # Get all orders that aren't marked as refunded
        orders = db.get_orders(status=['pending', 'processing', 'completed', 'partial'])
        
        for order in orders:
            order_id = order['id']
            
            # Check order status from API
            status_response = api_client.get_order_status(order_id)
            
            if status_response and status_response.get('status') == 'Refunded':
                # Get order details from database
                order_details = db.get_order_details(order_id)
                
                if order_details and order_details['status'] != 'refunded':
                    user_id = order_details['user_id']
                    refund_amount = order_details['price']
                    service_name = order_details['service_name']
                    
                    # Process the refund
                    if db.add_refund(user_id, order_id, refund_amount):
                        # Send notification to user
                        try:
                            user_lang = db.get_language(user_id)
                            message = (
                                f"💰 <b>Refund Received!</b>\n\n"
                                f"Your order #{order_id} for {service_name} has been refunded.\n"
                                f"Amount: ${refund_amount:.2f}\n\n"
                                f"The refund has been added to your balance."
                            )
                            
                            await context.bot.send_message(
                                chat_id=user_id,
                                text=message,
                                parse_mode='HTML'
                            )
                            
                            logger.info(f"Refund processed and notification sent for order {order_id} to user {user_id}")
                        except Exception as e:
                            logger.error(f"Error sending refund notification: {e}")
                    else:
                        logger.error(f"Failed to process refund for order {order_id}")
                
    except Exception as e:
        logger.error(f"Error in check_and_process_refunds: {e}")

def setup_refund_checker(application):
    """Set up the periodic refund checker"""
    job_queue = application.job_queue
    
    # Check for refunds every 30 minutes
    job_queue.run_repeating(check_and_process_refunds, interval=1800, first=10)
    logger.info("Refund checker scheduled") 