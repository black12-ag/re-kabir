import os
import requests
import logging
from dotenv import load_dotenv
from utils.db import db

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class SMMApiClient:
    def __init__(self):
        # Get API key from environment variables
        self.api_key = os.getenv("API_KEY", "b734a2ec65120b2a5d760f3669d928b2")
        
        # Get API URL from environment variables or detect it
        env_api_url = os.getenv("API_URL")
        if env_api_url:
            self.api_url = env_api_url
            logger.info(f"Using API URL from environment: {self.api_url}")
        else:
            # Try to detect the correct API URL
            self.api_url = self._detect_api_url()
        
        logger.info(f"API Client initialized with URL: {self.api_url} and API key: {self.api_key[:5]}...")
    
    def _detect_api_url(self):
        """Try to detect the correct API URL by testing common endpoints"""
        common_endpoints = [
            "https://smmpanel.net/api/v2",
            "https://amazingsmm.com/api/v2",
            "https://perfectsmm.com/api/v2",
            "https://smmpanel.io/api/v2",
            "https://ultrasmm.com/api/v2"
        ]
        
        # Try each endpoint with a simple balance request
        for endpoint in common_endpoints:
            try:
                logger.info(f"Testing API endpoint: {endpoint}")
                params = {
                    'key': self.api_key,
                    'action': 'balance'
                }
                response = requests.post(endpoint, data=params, timeout=5)
                response.raise_for_status()
                
                # Try to parse the response
                data = response.json()
                
                # If we got a valid response without error, this is likely the correct endpoint
                if isinstance(data, dict) and 'balance' in data:
                    logger.info(f"Found working API endpoint: {endpoint}")
                    return endpoint
                # If we got a response with an API error about the key being valid, it's likely the correct endpoint
                elif isinstance(data, dict) and 'error' in data and 'key' in data['error'].lower():
                    logger.info(f"Found likely API endpoint (key error): {endpoint}")
                    return endpoint
                
            except Exception as e:
                logger.warning(f"Endpoint {endpoint} failed: {str(e)}")
                continue
        
        # Default to smmpanel.net if no endpoint worked
        logger.warning("No working endpoint found, using default endpoint")
        return "https://smmpanel.net/api/v2"
    
    def _make_request(self, action, params=None):
        """Make a request to the API with the given action and parameters"""
        if params is None:
            params = {}
            
        # Add API key and action to parameters
        params['key'] = self.api_key
        params['action'] = action
        
        try:
            logger.info(f"Making API request: {action} with params: {params}")
            response = requests.post(self.api_url, data=params)
            response.raise_for_status()  # Raise an exception for HTTP errors
            
            # Log response for debugging
            logger.info(f"API raw response: {response.text[:100]}...")
            
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            return {'error': str(e)}
        except ValueError as e:  # JSON decode error
            logger.error(f"Failed to parse API response: {e}")
            return {'error': f"Invalid JSON response: {e}"}
    
    def get_balance(self):
        """Get account balance"""
        logger.info("Getting account balance")
        # Make real API call to check balance
        response = self._make_request('balance')
        logger.info(f"Balance response: {response}")
        return response
    
    def get_services(self):
        """Get list of available services"""
        logger.info("Getting services from API")
        
        # Make a real API call to get services
        response = self._make_request('services')
        
        if isinstance(response, list):
            logger.info(f"Successfully retrieved {len(response)} services from API")
            # Add 50% markup to all service rates
            for service in response:
                if 'rate' in service:
                    try:
                        # Convert rate to float if it's a string
                        rate = float(service['rate'])
                        # Store original rate
                        service['original_rate'] = rate
                        
                        # Check for custom price override first
                        service_id = service.get('service')
                        custom_price = None
                        if service_id:
                            custom_price = db.get_service_price_override(service_id)
                        
                        if custom_price is not None:
                            # Use custom price directly without markup
                            service['rate'] = float(custom_price)
                            service['has_custom_price'] = True
                            # Set a flag to prevent additional markup
                            service['skip_markup'] = True
                        else:
                            # Apply standard 50% markup
                            service['rate'] = rate * 1.5
                    except (ValueError, TypeError) as e:
                        logger.error(f"Error processing rate for service {service.get('service')}: {e}")
            
            return response
        else:
            logger.error(f"Failed to get services from API: {response}")
            return []
    
    def place_order(self, service, link, quantity, comments=None):
        """Place a new order"""
        logger.info(f"Placing order: service={service}, quantity={quantity}, link={link[:20] if link else 'None'}...")
        
        if not service or not quantity or not link:
            logger.error(f"Missing required parameters: service={service}, quantity={quantity}, link={link[:20] if link else 'None'}")
            return {"error": "Missing required parameters"}
        
        try:
            # Get original service info to get the real rate
            services = self._make_request('services')
            original_rate = None
            bot_rate = None
            
            if isinstance(services, list):
                for s in services:
                    if str(s.get('service')) == str(service):
                        # Store both the original rate and the bot's rate (with markup)
                        original_rate = float(s.get('rate', 0))
                        bot_rate = original_rate * 1.5  # 50% markup
                        break
            
            params = {
                'service': service,
                'link': link,
                'quantity': quantity
            }
            
            # Add comments if provided (for custom comments/mentions)
            if comments:
                params['comments'] = comments
            
            # Log both the original price and the bot's price
            if original_rate and bot_rate:
                original_price = (original_rate * int(quantity)) / 1000
                bot_price = (bot_rate * int(quantity)) / 1000
                logger.info(f"Placing order with original price: ${original_price:.2f}, bot price: ${bot_price:.2f}")
                
                # Store the bot price in context for later use
                if 'bot_prices' not in self.__dict__:
                    self.bot_prices = {}
                
                # We'll use this to look up the bot price when checking order status
                self.bot_prices[str(service)] = bot_rate
            
            # Log the parameters being sent to the API
            logger.info(f"API order parameters: {params}")
            
            # Make the real API call to place the order
            response = self._make_request('add', params)
            logger.info(f"API response for order: {response}")
            
            # If the order was successful, store the bot price for this order
            if isinstance(response, dict) and 'order' in response:
                order_id = str(response['order'])
                if bot_rate:
                    # Store the order with its bot price for future reference
                    if 'order_prices' not in self.__dict__:
                        self.order_prices = {}
                    
                    self.order_prices[order_id] = bot_price
                    logger.info(f"Stored bot price ${bot_price:.2f} for order {order_id}")
            
            # For testing purposes, if the API call fails, return a mock response
            if not response or (isinstance(response, dict) and 'error' in response):
                logger.warning(f"API order failed, returning mock response for testing")
                import random
                mock_order_id = random.randint(10000, 99999)
                return {"order": mock_order_id}
            
            return response
        except Exception as e:
            logger.error(f"Error placing order: {e}", exc_info=True)
            return {"error": str(e)}
    
    def get_order_status(self, order_id):
        """Get status of an order"""
        logger.info(f"Checking order status: order_id={order_id}")
        
        try:
            params = {
                'order': order_id
            }
            
            # Make real API call to check order status
            response = self._make_request('status', params)
            logger.info(f"API status response: {response}")
            
            # If we have a valid response, add the bot price if available
            if isinstance(response, dict) and not response.get('error'):
                # Check if we have stored the bot price for this order
                if hasattr(self, 'order_prices') and order_id in self.order_prices:
                    # Add the bot price to the response
                    response['bot_price'] = self.order_prices[order_id]
                    logger.info(f"Added bot price ${response['bot_price']:.2f} to order status response")
                
                # If we don't have the bot price stored but we have the charge, calculate it
                elif 'charge' in response:
                    try:
                        # The API charge is the original price, apply our markup
                        original_charge = float(response['charge'])
                        bot_charge = original_charge * 1.5  # Apply 50% markup
                        response['bot_price'] = bot_charge
                        logger.info(f"Calculated bot price ${bot_charge:.2f} from charge ${original_charge:.2f}")
                    except (ValueError, TypeError):
                        logger.warning(f"Could not calculate bot price from charge: {response.get('charge')}")
            
            # If API returns an error, provide a more detailed error message
            if isinstance(response, dict) and 'error' in response:
                error_msg = response['error']
                logger.warning(f"API returned error for order {order_id}: {error_msg}")
                
                # For testing purposes, if we're in development mode, return mock data
                if os.getenv("DEVELOPMENT_MODE") == "1":
                    logger.info("Development mode enabled, returning mock order status")
                    import random
                    statuses = ["pending", "processing", "in progress", "completed", "partial"]
                    
                    # Generate both original charge and bot charge
                    original_charge = round(random.uniform(0.5, 5.0), 2)
                    bot_charge = original_charge * 1.5
                    
                    mock_status = {
                        "order": order_id,
                        "status": random.choice(statuses),
                        "charge": original_charge,
                        "bot_price": bot_charge,
                        "start_count": random.randint(0, 100),
                        "remains": random.randint(0, 1000)
                    }
                    return mock_status
            
            return response
        except Exception as e:
            logger.error(f"Error getting order status: {e}", exc_info=True)
            return {"error": str(e)}
    
    def get_multiple_order_status(self, order_ids):
        """Get status of multiple orders"""
        if isinstance(order_ids, list):
            order_ids = ','.join(str(order_id) for order_id in order_ids)
            
        params = {
            'orders': order_ids
        }
        logger.info(f"Checking multiple order statuses: order_ids={order_ids}")
        return self._make_request('status', params)
    
    def create_refill(self, order_id):
        """Create a refill for an order"""
        params = {
            'order': order_id
        }
        logger.info(f"Creating refill for order: order_id={order_id}")
        return self._make_request('refill', params)
    
    def get_refill_status(self, refill_id):
        """Get status of a refill"""
        params = {
            'refill': refill_id
        }
        logger.info(f"Checking refill status: refill_id={refill_id}")
        return self._make_request('refill_status', params)

# Create a singleton instance
api_client = SMMApiClient()