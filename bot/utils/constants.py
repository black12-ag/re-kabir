# Currency exchange rates (USD to other currencies)
# Default rates, will be overridden by database values if available
DEFAULT_CURRENCY_RATES = {
    "ETB": 158.5,  # 1 USD = 158.5 ETB (Ethiopian Birr)
    "EUR": 0.925,   # 1 USD = 0.92 EUR
    "GBP": 0.80,   # 1 USD = 0.78 GBP
    "AUD": 1.75,   # 1 USD = 1.52 AUD
    "AED": 3.695,   # 1 USD = 3.67 AED
    "CAD": 1.46,   # 1 USD = 1.37 CAD
}

# Currency symbols for display
CURRENCY_SYMBOLS = {
    "USD": "$",
    "ETB": "Br",
    "EUR": "€",
    "GBP": "£",
    "AUD": "A$",
    "AED": "د.إ",
    "CAD": "C$"
}

# Order status emojis
ORDER_STATUS_EMOJIS = {
    "Pending": "⏳",
    "In progress": "🔄",
    "Completed": "✅",
    "Partial": "⚠️",
    "Canceled": "❌",
    "Processing": "⚙️",
    "Failed": "❗"
}

# This will be populated from the database at runtime
CURRENCY_RATES = DEFAULT_CURRENCY_RATES.copy()

def load_currency_rates_from_db():
    """Load currency rates from the database"""
    from utils.db import db
    
    # Get all currency rates from the database
    db_rates = db.get_all_currency_rates()
    
    # If we have rates in the database, update our rates dictionary
    if db_rates:
        for currency, rate in db_rates.items():
            CURRENCY_RATES[currency] = rate
    
    # Initialize any missing rates in the database
    for currency, rate in DEFAULT_CURRENCY_RATES.items():
        if currency not in db_rates:
            db.update_currency_rate(currency, rate)
    
    return CURRENCY_RATES

def reload_currency_rates():
    """Reload currency rates from the database"""
    global CURRENCY_RATES
    CURRENCY_RATES = load_currency_rates_from_db()
    return CURRENCY_RATES

# Load currency rates when the module is imported
try:
    load_currency_rates_from_db()
except Exception as e:
    import logging
    logging.getLogger(__name__).error(f"Error loading currency rates from database: {e}") 