import json
import os
import logging
from datetime import datetime
import sqlite3
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        # Get database path from environment variable or use default
        db_path = os.getenv('DB_FILE', 'data/smm_bot.db')
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
        
        abs_path = os.path.abspath(db_path)
        logger.info(f"Using database at: {abs_path}")
        
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.create_tables()
        self.migrate_database()
    
    def migrate_database(self):
        """Apply database migrations"""
        cursor = self.conn.cursor()
        
        # Check if currency_preference column exists in users table
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        column_names = [column[1] for column in columns]
        
        if 'currency_preference' not in column_names:
            # Add currency_preference column to users table
            cursor.execute("ALTER TABLE users ADD COLUMN currency_preference TEXT DEFAULT 'USD'")
            self.conn.commit()
            logger.info("Added currency_preference column to users table")
        
        # Check if settings table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='settings'")
        if not cursor.fetchone():
            # Create settings table
            cursor.execute('''
            CREATE TABLE settings (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            # Insert default settings
            cursor.execute("INSERT INTO settings (key, value) VALUES ('referral_threshold', '50')")
            cursor.execute("INSERT INTO settings (key, value) VALUES ('bonus_amount', '50.0')")
            self.conn.commit()
            logger.info("Created settings table with default values")
        
        # Check if service_price_overrides table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='service_price_overrides'")
        if not cursor.fetchone():
            # Create service_price_overrides table
            cursor.execute('''
            CREATE TABLE service_price_overrides (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service_id TEXT NOT NULL,
                price REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(service_id)
            )
            ''')
            self.conn.commit()
            logger.info("Created service_price_overrides table")
        
        # Check if currency_rates table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='currency_rates'")
        if not cursor.fetchone():
            # Create currency_rates table
            cursor.execute('''
            CREATE TABLE currency_rates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                currency TEXT NOT NULL,
                rate REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(currency)
            )
            ''')
            self.conn.commit()
            logger.info("Created currency_rates table")
        
        # Check if tutorials table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tutorials'")
        if not cursor.fetchone():
            # Create tutorials table
            cursor.execute('''
            CREATE TABLE tutorials (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tutorial_id TEXT NOT NULL,
                text TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(tutorial_id)
            )
            ''')
            self.conn.commit()
            logger.info("Created tutorials table")
        
        # Check if tutorial_media table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tutorial_media'")
        if not cursor.fetchone():
            # Create tutorial_media table
            cursor.execute('''
            CREATE TABLE tutorial_media (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tutorial_id TEXT NOT NULL,
                type TEXT NOT NULL,
                file_id TEXT NOT NULL,
                caption TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            self.conn.commit()
            logger.info("Created tutorial_media table")
        
        # Initialize tutorials with default content
        self.initialize_tutorials()
    
    def create_tables(self):
        """Create database tables if they don't exist."""
        cursor = self.conn.cursor()

        # Check if users table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if not cursor.fetchone():
            logger.info("Creating users table")
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                language TEXT DEFAULT 'en',
                balance REAL DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_active_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                currency_preference TEXT DEFAULT 'USD',
                referred_by INTEGER
            )
            ''')
            logger.info("Created users table")

        # Check if settings table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='settings'")
        if not cursor.fetchone():
            logger.info("Creating settings table")
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            logger.info("Created settings table")

        # Check if service_price_overrides table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='service_price_overrides'")
        if not cursor.fetchone():
            logger.info("Creating service_price_overrides table")
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS service_price_overrides (
                service_id TEXT PRIMARY KEY,
                original_price REAL,
                custom_price REAL,
                admin_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            logger.info("Created service_price_overrides table")

        # Check if balance_transactions table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='balance_transactions'")
        if not cursor.fetchone():
            logger.info("Creating balance_transactions table")
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS balance_transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                amount REAL,
                type TEXT,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                currency TEXT DEFAULT 'USD',
                original_amount REAL
            )
            ''')
            logger.info("Created balance_transactions table")
        else:
            # Check if we need to add currency columns to existing table
            cursor.execute("PRAGMA table_info(balance_transactions)")
            columns = [column[1] for column in cursor.fetchall()]
            if 'currency' not in columns:
                logger.info("Adding currency column to balance_transactions table")
                cursor.execute("ALTER TABLE balance_transactions ADD COLUMN currency TEXT DEFAULT 'USD'")
            if 'original_amount' not in columns:
                logger.info("Adding original_amount column to balance_transactions table")
                cursor.execute("ALTER TABLE balance_transactions ADD COLUMN original_amount REAL")
            if 'silent' not in columns:
                logger.info("Adding silent column to balance_transactions table")
                cursor.execute("ALTER TABLE balance_transactions ADD COLUMN silent INTEGER DEFAULT 0")

        # Create orders table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                order_id TEXT,
                service_id TEXT,
                service_name TEXT,
                quantity INTEGER,
                link TEXT,
                price REAL,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # Create referrals table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS referrals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                referrer_id INTEGER,
                referred_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (referrer_id) REFERENCES users (user_id),
                FOREIGN KEY (referred_id) REFERENCES users (user_id)
            )
        ''')
        
        self.conn.commit()
    
    def get_user(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        user = cursor.fetchone()
        
        if not user:
            # Create new user if doesn't exist
            cursor.execute(
                'INSERT INTO users (user_id, balance, last_activity, currency_preference, language, referred_by) VALUES (?, 0.0, ?, ?, ?, NULL)',
                (user_id, datetime.now(), 'USD', 'en')
            )
            self.conn.commit()
            return self.get_user(user_id)
        
        return {
            'user_id': user[0],
            'username': user[1],
            'first_name': user[2],
            'last_name': user[3],
            'balance': user[4],
            'last_activity': user[5],
            'created_at': user[6],
            'currency_preference': user[7] if len(user) > 7 else 'USD',
            'language': user[8] if len(user) > 8 else 'en',
            'referred_by': user[9] if len(user) > 9 else None
        }
    
    def update_user_activity(self, user_id):
        """Update user's last activity timestamp and ensure user exists in database"""
        # First, make sure the user exists
        self.get_user(user_id)
        
        # Then update the activity timestamp
        cursor = self.conn.cursor()
        cursor.execute(
            'UPDATE users SET last_activity = ? WHERE user_id = ?',
            (datetime.now(), user_id)
        )
        self.conn.commit()
    
    def get_balance(self, user_id):
        """Get user's balance"""
        # First, make sure the user exists
        user = self.get_user(user_id)
        
        # Return the balance from the user object
        return user.get('balance', 0.0)
    
    def get_currency_preference(self, user_id):
        """Get user's currency preference"""
        # First, make sure the user exists
        user = self.get_user(user_id)
        
        # Return the currency preference from the user object
        return user.get('currency_preference', 'USD')
    
    def get_user_currency_preference(self, user_id):
        """Alias for get_currency_preference"""
        return self.get_currency_preference(user_id)
    
    def set_currency_preference(self, user_id, currency):
        """Set user's currency preference"""
        cursor = self.conn.cursor()
        cursor.execute(
            'UPDATE users SET currency_preference = ? WHERE user_id = ?',
            (currency, user_id)
        )
        self.conn.commit()
        return True
    
    def add_balance(self, user_id, amount, description="Admin balance addition", currency="USD", silent=False):
        cursor = self.conn.cursor()
        try:
            # Start transaction
            cursor.execute('BEGIN TRANSACTION')
            
            # Convert amount if not in USD
            original_amount = amount
            original_currency = currency
            
            if currency.upper() != "USD":
                # Get the currency rate from settings with fallback to constants
                from utils.constants import CURRENCY_RATES
                rate = self.get_currency_rate(currency.lower(), CURRENCY_RATES.get(currency.upper(), 1.0))
                logger.info(f"Converting {amount} {currency} to USD using rate {rate}")
                # Convert to USD for storage
                usd_amount = amount / rate
                logger.info(f"Converted amount: {usd_amount} USD")
            else:
                usd_amount = amount
            
            # Ensure the amount is positive
            if usd_amount <= 0:
                logger.warning(f"Attempted to add non-positive amount {amount} {currency} for user {user_id}")
                cursor.execute('ROLLBACK')
                return False
                
            # Update user balance (stored in USD)
            cursor.execute(
                'UPDATE users SET balance = balance + ? WHERE user_id = ?',
                (usd_amount, user_id)
            )
            
            # Verify the balance was actually updated
            cursor.execute('SELECT balance FROM users WHERE user_id = ?', (user_id,))
            new_balance = cursor.fetchone()
            if not new_balance:
                logger.error(f"Failed to update balance for user {user_id} - user not found")
                cursor.execute('ROLLBACK')
                return False
                
            logger.info(f"Updated balance for user {user_id} to {new_balance[0]}")
            
            # Record transaction with original currency info and silent flag
            cursor.execute(
                'INSERT INTO balance_transactions (user_id, amount, type, description, currency, original_amount, silent) VALUES (?, ?, ?, ?, ?, ?, ?)',
                (user_id, usd_amount, 'credit', description, original_currency, original_amount, silent)
            )
            
            # Log the transaction ID
            transaction_id = cursor.lastrowid
            logger.info(f"Created balance transaction {transaction_id} for user {user_id}")
            
            # Commit transaction
            self.conn.commit()
            
            # Send notification to user if not silent
            if not silent:
                try:
                    from telegram import Bot
                    import os
                    
                    # Initialize bot
                    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
                    if bot_token:
                        bot = Bot(token=bot_token)
                        
                        # Format amount display
                        if currency.upper() == "ETB":
                            amount_display = f"ETB {original_amount:,.2f}"
                        else:
                            amount_display = f"${original_amount:.2f}"
                        
                        # Send notification
                        message = f"💰 <b>Balance Added</b>\n\n" \
                                  f"Amount: <code>{amount_display}</code> has been added to your account.\n" \
                                  f"Reason: {description}\n\n" \
                                  f"Use /balance to check your updated balance."
                        
                        bot.send_message(
                            chat_id=user_id,
                            text=message,
                            parse_mode="HTML"
                        )
                        logger.info(f"Sent balance addition notification to user {user_id}")
                except Exception as e:
                    logger.error(f"Error sending balance notification: {e}")
            
            return True
        except Exception as e:
            logger.error(f"Error adding balance: {e}")
            cursor.execute('ROLLBACK')
            return False
    
    def deduct_balance(self, user_id, amount, description="Order payment", currency="USD", silent=False):
        cursor = self.conn.cursor()
        try:
            # Start transaction
            cursor.execute('BEGIN TRANSACTION')
            
            # Convert amount if not in USD
            original_amount = amount
            original_currency = currency
            
            if currency.upper() != "USD":
                # Get the currency rate from settings with fallback to constants
                from utils.constants import CURRENCY_RATES
                rate = self.get_currency_rate(currency.lower(), CURRENCY_RATES.get(currency.upper(), 1.0))
                logger.info(f"Converting {amount} {currency} to USD using rate {rate}")
                # Convert to USD for storage
                usd_amount = amount / rate
                logger.info(f"Converted amount: {usd_amount} USD")
            else:
                usd_amount = amount
            
            # Check if user has sufficient balance
            current_balance = self.get_balance(user_id)
            if current_balance < usd_amount:
                logger.warning(f"Insufficient balance: user {user_id} has ${current_balance}, tried to deduct ${usd_amount}")
                cursor.execute('ROLLBACK')
                return False
            
            # Update user balance
            cursor.execute(
                'UPDATE users SET balance = balance - ? WHERE user_id = ?',
                (usd_amount, user_id)
            )
            
            # Record transaction with currency info and silent flag
            cursor.execute(
                'INSERT INTO balance_transactions (user_id, amount, type, description, currency, original_amount, silent) VALUES (?, ?, ?, ?, ?, ?, ?)',
                (user_id, -usd_amount, 'debit', description, original_currency, original_amount, silent)
            )
            
            # Commit transaction
            self.conn.commit()
            
            # Send notification to user if not silent
            if not silent and "Admin" in description:  # Only notify for admin deductions, not for regular orders
                try:
                    from telegram import Bot
                    import os
                    
                    # Initialize bot
                    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
                    if bot_token:
                        bot = Bot(token=bot_token)
                        
                        # Format amount display
                        if currency.upper() == "ETB":
                            amount_display = f"ETB {original_amount:,.2f}"
                        else:
                            amount_display = f"${original_amount:.2f}"
                        
                        # Send notification
                        message = f"🔄 <b>Balance Deducted</b>\n\n" \
                                  f"Amount: <code>{amount_display}</code> has been deducted from your account.\n" \
                                  f"Reason: {description}\n\n" \
                                  f"Use /balance to check your updated balance."
                        
                        bot.send_message(
                            chat_id=user_id,
                            text=message,
                            parse_mode="HTML"
                        )
                        logger.info(f"Sent balance deduction notification to user {user_id}")
                except Exception as e:
                    logger.error(f"Error sending balance notification: {e}")
            
            return True
        except Exception as e:
            logger.error(f"Error deducting balance: {e}")
            cursor.execute('ROLLBACK')
            return False
    
    def get_transactions(self, user_id, limit=10):
        """Get a user's recent balance transactions"""
        cursor = self.conn.cursor()
        cursor.execute(
            'SELECT * FROM balance_transactions WHERE user_id = ? ORDER BY created_at DESC LIMIT ?',
            (user_id, limit)
        )
        
        # Convert rows to dictionaries to include all columns including the currency fields
        columns = [column[0] for column in cursor.description]
        transactions = []
        
        for row in cursor.fetchall():
            # Create a dictionary with all column values
            tx = dict(zip(columns, row))
            transactions.append(tx)
            
        return transactions
    
    def add_order(self, user_id, order_id, service_id, service_name, quantity, link, price):
        cursor = self.conn.cursor()
        try:
            cursor.execute(
                '''INSERT INTO orders 
                   (user_id, order_id, service_id, service_name, quantity, link, price)
                   VALUES (?, ?, ?, ?, ?, ?, ?)''',
                (user_id, order_id, service_id, service_name, quantity, link, price)
            )
            self.conn.commit()
            return cursor.lastrowid
        except Exception as e:
            logger.error(f"Error adding order: {e}")
            return None
    
    def get_user_orders(self, user_id, limit=5):
        cursor = self.conn.cursor()
        cursor.execute(
            'SELECT * FROM orders WHERE user_id = ? ORDER BY created_at DESC LIMIT ?',
            (user_id, limit)
        )
        orders = cursor.fetchall()
        return [{
            'id': o[2],  # order_id from the API
            'user_id': o[1],
            'service_id': o[3],
            'service_name': o[4],
            'quantity': o[5],
            'link': o[6],
            'price': o[7],
            'status': o[8],
            'created_at': o[9]
        } for o in orders] if orders else []
    
    def get_user_total_spending(self, user_id):
        """Get the total amount a user has spent on orders and other transactions"""
        cursor = self.conn.cursor()
        
        # First get total from orders
        cursor.execute(
            'SELECT SUM(price) FROM orders WHERE user_id = ?',
            (user_id,)
        )
        result = cursor.fetchone()
        orders_total = result[0] if result and result[0] is not None else 0.0
        
        # Then get total from balance_transactions with debit type (spending)
        cursor.execute(
            'SELECT SUM(amount) FROM balance_transactions WHERE user_id = ? AND type = "debit"',
            (user_id,)
        )
        result = cursor.fetchone()
        transactions_total = result[0] if result and result[0] is not None else 0.0
        
        # Combine both totals
        total_spending = orders_total + transactions_total
        
        return total_spending
    
    def get_order_by_id(self, order_id):
        """Get order details by order_id"""
        cursor = self.conn.cursor()
        cursor.execute(
            'SELECT * FROM orders WHERE order_id = ? LIMIT 1',
            (order_id,)
        )
        order = cursor.fetchone()
        if order:
            return {
                'id': order[2],  # order_id from the API
                'user_id': order[1],
                'service_id': order[3],
                'service_name': order[4],
                'quantity': order[5],
                'link': order[6],
                'price': order[7],
                'status': order[8],
                'created_at': order[9]
            }
        return None
    
    def is_admin(self, user_id):
        """Check if a user is an admin"""
        admin_ids_str = os.getenv("ADMIN_USER_ID", "")
        admin_ids = [id.strip() for id in admin_ids_str.split(",")]
        return str(user_id) in admin_ids
    
    def get_language(self, user_id):
        """Get user's language preference"""
        try:
            conn = sqlite3.connect(os.getenv('DB_FILE', 'data/smm_bot.db'), check_same_thread=False)
            cursor = conn.cursor()
            cursor.execute("SELECT language FROM users WHERE user_id = ?", (user_id,))
            result = cursor.fetchone()
            conn.close()
            
            if result and result[0]:
                return result[0]
            return 'en'  # Default to English
        except Exception as e:
            logger.error(f"Error getting language: {e}")
            return 'en'  # Default to English if there's an error
    
    def set_language(self, user_id, language):
        """Set user's language preference"""
        cursor = self.conn.cursor()
        cursor.execute(
            'UPDATE users SET language = ? WHERE user_id = ?',
            (language, user_id)
        )
        self.conn.commit()
        return True

    def update_user_data(self, user_id, data_dict):
        """Update user data with key-value pairs from data_dict"""
        if not data_dict:
            return False
            
        cursor = self.conn.cursor()
        try:
            # Get column names from users table
            cursor.execute('PRAGMA table_info(users)')
            valid_columns = [column[1] for column in cursor.fetchall()]
            
            # Filter out invalid keys
            valid_data = {k: v for k, v in data_dict.items() if k in valid_columns}
            
            if not valid_data:
                logger.warning(f"No valid columns to update for user {user_id}")
                return False
                
            # Build the SQL query
            set_clause = ', '.join([f"{key} = ?" for key in valid_data.keys()])
            values = list(valid_data.values())
            values.append(user_id)
            
            # Execute the update
            cursor.execute(
                f'UPDATE users SET {set_clause} WHERE user_id = ?',
                values
            )
            self.conn.commit()
            logger.info(f"Updated user data for user {user_id}: {valid_data}")
            return True
        except Exception as e:
            logger.error(f"Error updating user data: {e}")
            return False

    # Add referral methods
    def add_referral(self, referrer_id, referred_id):
        """Record a new referral"""
        cursor = self.conn.cursor()
        transaction_active = False
        try:
            # Check if the referred user already has a referrer
            user = self.get_user(referred_id)
            if user.get('referred_by'):
                logger.info(f"User {referred_id} already has a referrer: {user.get('referred_by')}")
                return False
                
            # Start transaction
            cursor.execute('BEGIN TRANSACTION')
            transaction_active = True
            
            # Update the referred user's record
            cursor.execute(
                'UPDATE users SET referred_by = ? WHERE user_id = ?',
                (referrer_id, referred_id)
            )
            
            # Add entry to referrals table
            cursor.execute(
                'INSERT INTO referrals (referrer_id, referred_id) VALUES (?, ?)',
                (referrer_id, referred_id)
            )
            
            # Commit transaction
            self.conn.commit()
            transaction_active = False
            logger.info(f"Successfully recorded referral: {referrer_id} referred {referred_id}")
            return True
        except Exception as e:
            logger.error(f"Error adding referral: {e}")
            if transaction_active:
                try:
                    cursor.execute('ROLLBACK')
                except sqlite3.Error as rollback_error:
                    logger.error(f"Error during rollback: {rollback_error}")
            return False
    
    def get_referrals(self, user_id):
        """Get list of users referred by the given user"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT u.user_id, u.username, u.first_name, u.last_name, r.created_at
            FROM referrals r
            JOIN users u ON r.referred_id = u.user_id
            WHERE r.referrer_id = ?
            ORDER BY r.created_at DESC
        ''', (user_id,))
        
        referrals = []
        for row in cursor.fetchall():
            referrals.append({
                'user_id': row[0],
                'username': row[1],
                'first_name': row[2],
                'last_name': row[3],
                'created_at': row[4]
            })
        
        return referrals
    
    def get_referral_count(self, user_id):
        """Get the number of users referred by the given user"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM referrals WHERE referrer_id = ?', (user_id,))
        return cursor.fetchone()[0]
    
    def get_valid_referral_count(self, user_id):
        """Get the number of valid users (with username) referred by the given user"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT COUNT(*) 
            FROM referrals r
            JOIN users u ON r.referred_id = u.user_id
            WHERE r.referrer_id = ? AND u.username IS NOT NULL AND u.username != ''
        ''', (user_id,))
        return cursor.fetchone()[0]
    
    def get_referral_bonus_amount(self):
        """Get the referral bonus amount"""
        try:
            amount = float(self.get_setting('referral_bonus_amount', '50.0'))
            return amount
        except (ValueError, TypeError):
            # Default to 50.0 ETB if there's an error
            return 50.0
            
    def set_referral_bonus_amount(self, amount):
        """Set the referral bonus amount"""
        return self.set_setting('referral_bonus_amount', str(amount))

    def check_and_create_referral_bonus(self, user_id):
        """Check if user has reached the referral threshold and create a bonus if needed"""
        cursor = self.conn.cursor()
        transaction_active = False
        try:
            # Get referral threshold from settings
            referral_threshold_str = self.get_setting("referral_threshold", "50")
            try:
                referral_threshold = int(referral_threshold_str)
            except (ValueError, TypeError):
                # Default to 50 if conversion fails
                referral_threshold = 50
                logger.warning(f"Failed to convert referral_threshold to integer. Using default value: {referral_threshold}")
            
            # Get total valid referral count (only users with username)
            referral_count = self.get_valid_referral_count(user_id)
            
            # Get already processed referrals
            cursor.execute('''
                SELECT SUM(referral_count)
                FROM referral_bonuses
                WHERE user_id = ?
            ''', (user_id,))
            
            processed_count = cursor.fetchone()[0] or 0
            
            # Calculate how many new bonuses to create
            new_bonus_count = (referral_count // referral_threshold) - (processed_count // referral_threshold)
            
            if new_bonus_count <= 0:
                # No new bonuses
                return None
            
            # Get the configurable bonus amount
            bonus_amount = self.get_referral_bonus_amount()
            
            # Log the bonus creation
            logger.info(f"Creating referral bonus for user {user_id}: {bonus_amount} ETB for {referral_threshold} referrals")
            
            # Start transaction
            cursor.execute('BEGIN TRANSACTION')
            transaction_active = True
            
            # Insert bonus record
            cursor.execute('''
                INSERT INTO referral_bonuses
                (user_id, referral_count, bonus_amount, status)
                VALUES (?, ?, ?, 'pending')
            ''', (user_id, referral_threshold, bonus_amount))
            
            bonus_id = cursor.lastrowid
            
            # Commit transaction
            self.conn.commit()
            transaction_active = False
            
            # Return bonus info
            return {
                'id': bonus_id,
                'user_id': user_id,
                'referral_count': referral_count,
                'processed_count': processed_count,
                'new_bonus_count': new_bonus_count,
                'bonus_amount': bonus_amount,
                'referral_threshold': referral_threshold
            }
        except Exception as e:
            logger.error(f"Error checking referral bonus: {e}")
            if transaction_active:
                try:
                    cursor.execute('ROLLBACK')
                except sqlite3.Error as rollback_error:
                    logger.error(f"Error during rollback: {rollback_error}")
            return None
    
    def get_pending_referral_bonuses(self, user_id=None):
        """Get pending referral bonuses for a user or all users"""
        cursor = self.conn.cursor()
        
        if user_id:
            cursor.execute('''
                SELECT rb.id, rb.user_id, u.username, u.first_name, u.last_name, 
                       rb.referral_count, rb.bonus_amount, rb.status, rb.created_at
                FROM referral_bonuses rb
                JOIN users u ON rb.user_id = u.user_id
                WHERE rb.user_id = ? AND rb.status = 'pending'
                ORDER BY rb.created_at DESC
            ''', (user_id,))
        else:
            cursor.execute('''
                SELECT rb.id, rb.user_id, u.username, u.first_name, u.last_name, 
                       rb.referral_count, rb.bonus_amount, rb.status, rb.created_at
                FROM referral_bonuses rb
                JOIN users u ON rb.user_id = u.user_id
                WHERE rb.status = 'pending'
                ORDER BY rb.created_at DESC
            ''')
        
        bonuses = []
        for row in cursor.fetchall():
            bonuses.append({
                'id': row[0],
                'user_id': row[1],
                'username': row[2],
                'first_name': row[3],
                'last_name': row[4],
                'referral_count': row[5],
                'bonus_amount': row[6],
                'status': row[7],
                'created_at': row[8]
            })
        
        return bonuses
    
    def get_all_referral_bonuses(self, user_id):
        """Get all referral bonuses for a user (approved, pending, rejected)"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM referral_bonuses 
            WHERE user_id = ? 
            ORDER BY created_at DESC
        ''', (user_id,))
        
        columns = [col[0] for col in cursor.description]
        bonuses = [dict(zip(columns, row)) for row in cursor.fetchall()]
        return bonuses
    
    def process_referral_bonus(self, bonus_id, status, admin_id):
        """Process a referral bonus (approve or decline)"""
        cursor = self.conn.cursor()
        transaction_active = False
        try:
            # Start transaction
            cursor.execute('BEGIN TRANSACTION')
            transaction_active = True
            
            # Get bonus details
            cursor.execute('SELECT user_id, bonus_amount FROM referral_bonuses WHERE id = ?', (bonus_id,))
            bonus = cursor.fetchone()
            
            if not bonus:
                cursor.execute('ROLLBACK')
                transaction_active = False
                return False
            
            user_id, bonus_amount = bonus
            
            # Update bonus status
            cursor.execute('''
                UPDATE referral_bonuses 
                SET status = ?, processed_at = CURRENT_TIMESTAMP, processed_by = ? 
                WHERE id = ?
            ''', (status, admin_id, bonus_id))
            
            # If approved, add balance to user using the add_balance method
            if status == 'approved':
                # Use the add_balance method for proper currency handling
                success = self.add_balance(
                    user_id, 
                    bonus_amount, 
                    f"Referral bonus for reaching referral milestone", 
                    currency="ETB",
                    silent=False
                )
                
                if not success:
                    logger.error(f"Failed to add balance for referral bonus: user_id={user_id}, amount={bonus_amount}")
                    cursor.execute('ROLLBACK')
                    transaction_active = False
                    return False
                
                logger.info(f"Added referral bonus: {bonus_amount} ETB to user {user_id}")
            
            # Commit transaction
            self.conn.commit()
            transaction_active = False
            return True
        except Exception as e:
            logger.error(f"Error processing referral bonus: {e}")
            if transaction_active:
                try:
                    cursor.execute('ROLLBACK')
                except sqlite3.Error as rollback_error:
                    logger.error(f"Error during rollback: {rollback_error}")
            return False

    def get_setting(self, key, default=None):
        """Get a setting from the settings table"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT value FROM settings WHERE key = ?', (key,))
        result = cursor.fetchone()
        if result:
            return result[0]
        return default
        
    def set_setting(self, key, value):
        """Set a setting in the settings table"""
        cursor = self.conn.cursor()
        # Check if the setting already exists
        cursor.execute('SELECT value FROM settings WHERE key = ?', (key,))
        result = cursor.fetchone()
        
        if result:
            # Update existing setting
            cursor.execute('UPDATE settings SET value = ?, updated_at = CURRENT_TIMESTAMP WHERE key = ?', 
                           (value, key))
        else:
            # Insert new setting
            cursor.execute('INSERT INTO settings (key, value) VALUES (?, ?)', (key, value))
            
        self.conn.commit()
        return True
        
    def get_new_user_bonus_status(self):
        """Check if new user bonus is enabled"""
        status = self.get_setting('new_user_bonus_enabled', 'false')
        return status.lower() == 'true'
        
    def set_new_user_bonus_status(self, enabled):
        """Enable or disable new user bonus"""
        return self.set_setting('new_user_bonus_enabled', 'true' if enabled else 'false')
        
    def get_new_user_bonus_amount(self):
        """Get the new user bonus amount"""
        try:
            return float(self.get_setting('new_user_bonus_amount', '0'))
        except (TypeError, ValueError):
            return 0
            
    def set_new_user_bonus_amount(self, amount):
        """Set the new user bonus amount"""
        return self.set_setting('new_user_bonus_amount', str(amount))
        
    def get_new_user_bonus_currency(self):
        """Get the currency for new user bonus"""
        return self.get_setting('new_user_bonus_currency', 'USD')
        
    def set_new_user_bonus_currency(self, currency):
        """Set the currency for new user bonus"""
        return self.set_setting('new_user_bonus_currency', currency)

    def get_new_user_bonus_username_required(self):
        """Check if username is required for new user bonus"""
        status = self.get_setting('new_user_bonus_username_required', 'false')
        return status.lower() == 'true'
        
    def set_new_user_bonus_username_required(self, required):
        """Set whether username is required for new user bonus"""
        return self.set_setting('new_user_bonus_username_required', 'true' if required else 'false')

    def update_currency_rate(self, currency, rate):
        """Update the exchange rate for a currency"""
        # Store currency rates in the settings table with a prefix
        key = f"currency_rate_{currency}"
        return self.set_setting(key, rate)
    
    def get_currency_rate(self, currency, default=None):
        """Get the exchange rate for a currency"""
        # Get currency rate from settings table
        key = f"currency_rate_{currency}"
        rate_str = self.get_setting(key)
        
        if rate_str:
            try:
                return float(rate_str)
            except (ValueError, TypeError):
                return default
        return default
    
    def get_all_currency_rates(self):
        """Get all currency exchange rates"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT key, value FROM settings WHERE key LIKE ?', ('currency_rate_%',))
        results = cursor.fetchall()
        
        rates = {}
        for key, value in results:
            currency = key.replace('currency_rate_', '')
            try:
                rates[currency] = float(value)
            except (ValueError, TypeError):
                continue
        
        return rates

    # Add statistics methods
    def get_total_users(self):
        """Get the total number of users"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM users')
        return cursor.fetchone()[0]
    
    def get_active_users(self, days=7):
        """Get the number of active users in the last X days"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT COUNT(*) FROM users 
            WHERE last_activity >= datetime('now', ?) AND last_activity IS NOT NULL
        ''', (f'-{days} days',))
        return cursor.fetchone()[0]
    
    def get_total_orders(self):
        """Get the total number of orders"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM orders')
        return cursor.fetchone()[0]
    
    def get_recent_orders(self, days=7):
        """Get the number of orders in the last X days"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT COUNT(*) FROM orders 
            WHERE created_at >= datetime('now', ?)
        ''', (f'-{days} days',))
        return cursor.fetchone()[0]
    
    def get_all_users_list(self, limit=1000):
        """Get a list of all users with details"""
        cursor = self.conn.cursor()
        
        # If limit is None, don't include LIMIT clause to get all users
        if limit is None:
            cursor.execute('''
                SELECT user_id, username, first_name, last_name, balance, last_activity, created_at
                FROM users
                ORDER BY created_at DESC
            ''')
        else:
            cursor.execute('''
                SELECT user_id, username, first_name, last_name, balance, last_activity, created_at
                FROM users
                ORDER BY created_at DESC
                LIMIT ?
            ''', (limit,))
        
        users = []
        for row in cursor.fetchall():
            users.append({
                'user_id': row[0],
                'username': row[1],
                'first_name': row[2],
                'last_name': row[3],
                'balance': row[4],
                'last_activity': row[5],
                'created_at': row[6]
            })
        
        return users
    
    def get_active_users_list(self, days=7, limit=1000):
        """Get a list of active users in the last X days"""
        cursor = self.conn.cursor()
        
        # If limit is None, don't include LIMIT clause to get all active users
        if limit is None:
            cursor.execute('''
                SELECT user_id, username, first_name, last_name, balance, last_activity, created_at
                FROM users
                WHERE last_activity >= datetime('now', ?) AND last_activity IS NOT NULL
                ORDER BY last_activity DESC
            ''', (f'-{days} days',))
        else:
            cursor.execute('''
                SELECT user_id, username, first_name, last_name, balance, last_activity, created_at
                FROM users
                WHERE last_activity >= datetime('now', ?) AND last_activity IS NOT NULL
                ORDER BY last_activity DESC
                LIMIT ?
            ''', (f'-{days} days', limit))
        
        users = []
        for row in cursor.fetchall():
            users.append({
                'user_id': row[0],
                'username': row[1],
                'first_name': row[2],
                'last_name': row[3],
                'balance': row[4],
                'last_activity': row[5],
                'created_at': row[6]
            })
        
        return users
    
    def get_all_orders(self, limit=1000):
        """Get a list of all orders with details"""
        cursor = self.conn.cursor()
        
        # If limit is None, don't include LIMIT clause to get all orders
        if limit is None:
            cursor.execute('''
                SELECT id, user_id, order_id, service_id, service_name, quantity, link, price, status, created_at
                FROM orders
                ORDER BY created_at DESC
            ''')
        else:
            cursor.execute('''
                SELECT id, user_id, order_id, service_id, service_name, quantity, link, price, status, created_at
                FROM orders
                ORDER BY created_at DESC
                LIMIT ?
            ''', (limit,))
        
        orders = []
        for row in cursor.fetchall():
            orders.append({
                'id': row[0],
                'user_id': row[1],
                'order_id': row[2],
                'service_id': row[3],
                'service_name': row[4],
                'quantity': row[5],
                'link': row[6],
                'price': row[7],
                'status': row[8],
                'created_at': row[9]
            })
        
        return orders
    
    def get_recent_orders_list(self, days=7, limit=1000):
        """Get a list of orders in the last X days"""
        cursor = self.conn.cursor()
        
        # If limit is None, don't include LIMIT clause to get all recent orders
        if limit is None:
            cursor.execute('''
                SELECT id, user_id, order_id, service_id, service_name, quantity, link, price, status, created_at
                FROM orders
                WHERE created_at >= datetime('now', ?)
                ORDER BY created_at DESC
            ''', (f'-{days} days',))
        else:
            cursor.execute('''
                SELECT id, user_id, order_id, service_id, service_name, quantity, link, price, status, created_at
                FROM orders
                WHERE created_at >= datetime('now', ?)
                ORDER BY created_at DESC
                LIMIT ?
            ''', (f'-{days} days', limit))
        
        orders = []
        for row in cursor.fetchall():
            orders.append({
                'id': row[0],
                'user_id': row[1],
                'order_id': row[2],
                'service_id': row[3],
                'service_name': row[4],
                'quantity': row[5],
                'link': row[6],
                'price': row[7],
                'status': row[8],
                'created_at': row[9]
            })
        
        return orders

    def set_service_price_override(self, service_id, original_price, custom_price, admin_id):
        """Set a custom price for a service"""
        cursor = self.conn.cursor()
        try:
            cursor.execute(
                '''INSERT OR REPLACE INTO service_price_overrides 
                   (service_id, original_price, custom_price, updated_at, updated_by)
                   VALUES (?, ?, ?, ?, ?)''',
                (service_id, original_price, custom_price, datetime.now(), admin_id)
            )
            self.conn.commit()
            
            # Invalidate services cache
            self.invalidate_services_cache()
            
            return True
        except Exception as e:
            logger.error(f"Error setting service price override: {e}")
            return False
    
    def get_service_price_override(self, service_id):
        """Get the custom price for a service if it exists"""
        cursor = self.conn.cursor()
        cursor.execute(
            'SELECT custom_price FROM service_price_overrides WHERE service_id = ?',
            (service_id,)
        )
        result = cursor.fetchone()
        return result[0] if result else None
    
    def get_all_service_price_overrides(self):
        """Get all service price overrides"""
        cursor = self.conn.cursor()
        cursor.execute(
            '''SELECT service_id, original_price, custom_price, updated_at, updated_by 
               FROM service_price_overrides
               ORDER BY updated_at DESC'''
        )
        overrides = cursor.fetchall()
        return [{
            'service_id': o[0],
            'original_price': o[1],
            'custom_price': o[2],
            'updated_at': o[3],
            'updated_by': o[4]
        } for o in overrides]
    
    def delete_service_price_override(self, service_id):
        """Delete a service price override"""
        cursor = self.conn.cursor()
        try:
            cursor.execute(
                'DELETE FROM service_price_overrides WHERE service_id = ?',
                (service_id,)
            )
            self.conn.commit()
            
            # Invalidate services cache
            self.invalidate_services_cache()
            
            return True
        except Exception as e:
            logger.error(f"Error deleting service price override: {e}")
            return False
    
    def update_service_prices_by_range(self, min_price, max_price, percentage, admin_id):
        """Update prices for services within a price range by a percentage"""
        # This will be implemented in the API client
        # We'll just record the range adjustment in the database for reference
        cursor = self.conn.cursor()
        try:
            # Create a record of the bulk update
            cursor.execute(
                '''INSERT INTO settings 
                   (key, value, updated_at) 
                   VALUES (?, ?, ?)''',
                (f"price_range_update_{datetime.now().strftime('%Y%m%d%H%M%S')}", 
                 json.dumps({
                     'min_price': min_price,
                     'max_price': max_price,
                     'percentage': percentage,
                     'admin_id': admin_id,
                     'timestamp': datetime.now().isoformat()
                 }),
                 datetime.now())
            )
            self.conn.commit()
            
            # Invalidate services cache
            self.invalidate_services_cache()
            
            return True
        except Exception as e:
            logger.error(f"Error recording price range update: {e}")
            return False
    
    def invalidate_services_cache(self):
        """Invalidate the services cache to ensure fresh data is fetched"""
        try:
            # Import here to avoid circular imports
            from handlers.services import invalidate_services_cache
            invalidate_services_cache()
            logger.info("Services cache invalidated after price change")
            return True
        except Exception as e:
            logger.error(f"Error invalidating services cache: {e}")
            return False

    # Tutorial system functions
    def get_tutorial_content(self, tutorial_id):
        """Get tutorial content from database"""
        try:
            conn = sqlite3.connect(os.getenv('DB_FILE', 'data/smm_bot.db'), check_same_thread=False)
            cursor = conn.cursor()
            cursor.execute("SELECT text FROM tutorials WHERE tutorial_id = ?", (tutorial_id,))
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return {'text': result[0]}
            return None
        except Exception as e:
            logger.error(f"Error getting tutorial content: {e}")
            return None
    
    def update_tutorial_text(self, tutorial_id, new_text):
        """Update the text content of a tutorial"""
        try:
            conn = sqlite3.connect(os.getenv('DB_FILE', 'data/smm_bot.db'), check_same_thread=False)
            cursor = conn.cursor()
            cursor.execute("UPDATE tutorials SET text = ? WHERE tutorial_id = ?", (new_text, tutorial_id))
            conn.commit()
            conn.close()
            logger.info(f"Updated tutorial {tutorial_id} with new text")
            return True
        except Exception as e:
            logger.error(f"Error updating tutorial content: {e}")
            return False
    
    def get_tutorial_media(self, tutorial_id):
        """Get all media files associated with a tutorial"""
        try:
            conn = sqlite3.connect(os.getenv('DB_FILE', 'data/smm_bot.db'), check_same_thread=False)
            cursor = conn.cursor()
            cursor.execute("SELECT type, file_id, caption, id FROM tutorial_media WHERE tutorial_id = ? ORDER BY id ASC", (tutorial_id,))
            results = cursor.fetchall()
            conn.close()
            
            media_files = []
            for row in results:
                media_files.append({
                    'type': row[0],
                    'file_id': row[1],
                    'caption': row[2] if row[2] else '',
                    'id': row[3]
                })
            
            return media_files
        except Exception as e:
            logger.error(f"Error getting tutorial media: {e}")
            return []
    
    def add_tutorial_media(self, tutorial_id, media_type, file_id, caption=""):
        """Add a media file to a tutorial"""
        try:
            conn = sqlite3.connect(os.getenv('DB_FILE', 'data/smm_bot.db'), check_same_thread=False)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO tutorial_media (tutorial_id, type, file_id, caption) VALUES (?, ?, ?, ?)",
                (tutorial_id, media_type, file_id, caption)
            )
            conn.commit()
            conn.close()
            logger.info(f"Added {media_type} media to tutorial {tutorial_id}")
            return True
        except Exception as e:
            logger.error(f"Error adding tutorial media: {e}")
            return False
    
    def delete_tutorial_media(self, tutorial_id, media_index):
        """Delete a media file from a tutorial by index"""
        try:
            conn = sqlite3.connect(os.getenv('DB_FILE', 'data/smm_bot.db'), check_same_thread=False)
            cursor = conn.cursor()
            
            # Get all media for this tutorial
            cursor.execute("SELECT id FROM tutorial_media WHERE tutorial_id = ? ORDER BY id ASC", (tutorial_id,))
            media_ids = cursor.fetchall()
            
            if media_index < 0 or media_index >= len(media_ids):
                return False
            
            # Get the actual media ID
            media_id = media_ids[media_index][0]
            
            # Delete the media
            cursor.execute("DELETE FROM tutorial_media WHERE id = ?", (media_id,))
            conn.commit()
            conn.close()
            
            logger.info(f"Deleted media from tutorial {tutorial_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting tutorial media: {e}")
            return False
    
    def initialize_tutorials(self):
        """Initialize tutorials with default content"""
        default_tutorials = {
            "account": """<b>Account Management Tutorial</b>

This tutorial will show you how to manage your account settings.

<b>Available Settings:</b>
• Change your language preference
• View your profile information
• Check your referral link and statistics

To access your account settings, use the /account command or click on the "👤 Account" button in the main menu.""",

            "balance": """<b>💰 Balance Tutorial</b>

This tutorial will show you how to check your balance and manage your account funds.

<b>Step 1: Access the Balance Menu</b>
• From the main menu, click on the "💰 Balance" button
• Alternatively, use the /balance command

<b>Step 2: View Your Balance</b>
• Your current balance will be displayed in your preferred currency (USD or ETB)
• You'll see your total spending history below your current balance

<b>Step 3: Balance Menu Options</b>
• <b>💳 Add Funds</b>: Recharge your account balance
• <b>📊 Transaction History</b>: View your recent transactions
• <b>💱 Change Currency</b>: Switch between USD and ETB

<b>Step 4: Managing Your Balance</b>
• Your balance is used automatically when placing orders
• You can view your transaction history to track all account activity
• Balance can be topped up at any time using various payment methods

<b>Tips:</b>
• Keep track of your transaction history to monitor your spending
• Make sure to maintain sufficient balance for your orders
• Contact support if you have any issues with your balance""",

            "recharge": """<b>💳 Recharge Account Tutorial</b>

This tutorial will guide you through the process of adding funds to your account.

<b>Step 1: Access Recharge Options</b>
• From the main menu, tap "💰 Balance"
• Then select "💳 Add Funds" button
• Alternatively, use the /recharge command

<b>Step 2: Choose Payment Method</b>
• <b>🌐 Wise (International)</b>: For international bank transfers
• <b>🇪🇹 Ethiopian Banks</b>: For local Ethiopian bank transfers
• <b>🌍 International Options</b>: For various international payment methods
• <b>💰 Cryptocurrency</b>: For crypto payments

<b>Step 3: Select Amount</b>
• Choose from preset amounts or select "Custom Amount"
• For international payments, the minimum amount is $10
• For Ethiopian banks, select amount in ETB (min. 100 ETB)

<b>Step 4: Complete Payment</b>
• Follow the payment instructions for your chosen method
• Transfer the exact amount shown
• Take a screenshot of your payment confirmation

<b>Step 5: Submit Payment Proof</b>
• Click "I've Paid" after completing the payment
• Send the screenshot of your payment confirmation
• Admin will verify your payment and credit your account

<b>Important Notes:</b>
• Always include your user ID in payment references when possible
• Make sure to send clear screenshots of payment confirmations
• Your account will be credited once payment is verified
• Processing time depends on the payment method used""",

            "services": """<b>Browse Services Tutorial</b>

This tutorial will show you how to browse and select services.

<b>Browsing Services:</b>
• Use the /services command or click on the "🛒 Services" button in the main menu
• Browse through the available service categories
• Select a category to see the services within it
• Click on a service to view its details and pricing

<b>Service Details:</b>
• Each service shows its name, description, and price
• You can see the minimum and maximum quantity allowed
• Some services may have additional information or requirements""",

            "status": """<b>📊 Order Status Tutorial</b>

This tutorial will show you how to check and manage your orders.

<b>Step 1: Access Order Status</b>
• From the main menu, click on the "📊 Order Status" button
• Alternatively, use the /status command

<b>Step 2: View Your Orders</b>
• You'll see a list of your recent orders with their IDs
• Your total spending will be displayed at the top
• Orders are sorted by date with the most recent first

<b>Step 3: Check Specific Order Details</b>
• Click on any order ID to view detailed information
• You'll see complete details including:
  - Order ID
  - Service name
  - Quantity
  - Link
  - Price
  - Current status
  - Start count and remaining (if applicable)

<b>Step 4: Understanding Order Statuses</b>
• <b>Pending</b>: Order has been submitted but not yet processed
• <b>In Progress</b>: Order is currently being fulfilled
• <b>Completed</b>: Order has been successfully completed
• <b>Partial</b>: Order was partially completed
• <b>Cancelled</b>: Order was cancelled (refund may be issued)
• <b>Failed</b>: Order could not be completed

<b>Tips:</b>
• Copy and send any order ID to check its current status
• Regular status checks help you monitor progress of your orders
• Contact support if you have questions about a specific order""",

            "referral": """<b>👥 Referral Program Tutorial</b>

This tutorial will show you how to use and benefit from our referral program.

<b>Step 1: Access Your Referral Link</b>
• From the main menu, click on the "👥 Referrals" button
• Alternatively, use the /referrals command
• Your unique referral link will be displayed

<b>Step 2: Share Your Referral Link</b>
• Click the "Share" button to easily share your link
• Send your referral link to friends, followers, or colleagues
• When someone joins using your link, they become your referral

<b>Step 3: Track Your Referrals</b>
• View your total referral count on the referral page
• Check which referrals are valid (have usernames)
• Monitor your progress toward earning bonuses

<b>Step 4: Earn Referral Bonuses</b>
• For every 50 valid referrals, you earn ETB 50.0
• Valid referrals are users who have set a Telegram username
• Bonus requests are automatically created when you reach the threshold

<b>Step 5: Receive Your Bonuses</b>
• Bonuses will be reviewed by admin
• Once approved, the bonus amount is added to your balance
• You can track pending and approved bonuses on your referral page

<b>Tips for Successful Referrals:</b>
• Ensure referrals set a Telegram username to be counted as valid
• Share your link with people who are likely to use the service
• Check your referral statistics regularly to track your progress
• The more active referrals you bring, the more bonuses you can earn""",

            "support": """<b>Contact Support Tutorial</b>

This tutorial will show you how to contact our support team.

<b>Contacting Support:</b>
• Use the /support command or click on the "📞 Support" button in the main menu
• Type your message and send it to our support team
• Our team will respond to your inquiry as soon as possible

<b>Tips for Faster Support:</b>
• Be clear and specific about your issue
• Include relevant details such as order IDs if applicable
• Attach screenshots if they help explain your issue"""
        }
        
        cursor = self.conn.cursor()
        
        # Check if tutorials already exist
        cursor.execute('SELECT tutorial_id FROM tutorials')
        existing_tutorials = [t[0] for t in cursor.fetchall()]
        
        # Add default tutorials if they don't exist
        for tutorial_id, text in default_tutorials.items():
            if tutorial_id not in existing_tutorials:
                cursor.execute(
                    'INSERT INTO tutorials (tutorial_id, text, created_at, updated_at) VALUES (?, ?, datetime("now"), datetime("now"))',
                    (tutorial_id, text)
                )
            else:
                # Update existing tutorials with new content
                cursor.execute(
                    'UPDATE tutorials SET text = ?, updated_at = datetime("now") WHERE tutorial_id = ?',
                    (text, tutorial_id)
                )
        
        self.conn.commit()

    def get_user_by_username(self, username):
        """Get user by username"""
        if not username:
            return None
            
        cursor = self.conn.cursor()
        # Case-insensitive search to be more user-friendly
        cursor.execute('SELECT * FROM users WHERE LOWER(username) = LOWER(?)', (username,))
        user = cursor.fetchone()
        
        if not user:
            return None
            
        return {
            'user_id': user[0],
            'username': user[1],
            'first_name': user[2],
            'last_name': user[3],
            'balance': user[4],
            'last_activity': user[5],
            'created_at': user[6],
            'currency_preference': user[7] if len(user) > 7 else 'USD',
            'language': user[8] if len(user) > 8 else 'en',
            'referred_by': user[9] if len(user) > 9 else None
        }

    def update_user_info(self, user_id, username, first_name, last_name):
        """Update user information in the database"""
        cursor = self.conn.cursor()
        try:
            cursor.execute(
                'UPDATE users SET username = ?, first_name = ?, last_name = ? WHERE user_id = ?',
                (username, first_name, last_name, user_id)
            )
            self.conn.commit()
            logger.info(f"Updated user data for user {user_id}: {{'username': {username}, 'first_name': {first_name}, 'last_name': {last_name}}}")
            return True
        except Exception as e:
            logger.error(f"Error updating user info: {e}")
            return False

    # Custom Messages System
    def migrate_custom_messages_table(self):
        """Create custom_messages table if it doesn't exist"""
        cursor = self.conn.cursor()
        
        # Check if custom_messages table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='custom_messages'")
        if not cursor.fetchone():
            # Create custom_messages table
            cursor.execute('''
            CREATE TABLE custom_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_key TEXT NOT NULL,
                message_text TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(message_key)
            )
            ''')
            
            # Create custom_message_media table for storing media
            cursor.execute('''
            CREATE TABLE custom_message_media (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_key TEXT NOT NULL,
                media_type TEXT NOT NULL,
                file_id TEXT NOT NULL,
                position INTEGER DEFAULT 0,
                caption TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (message_key) REFERENCES custom_messages(message_key)
            )
            ''')
            
            # Create custom_message_buttons table for storing buttons/links
            cursor.execute('''
            CREATE TABLE custom_message_buttons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_key TEXT NOT NULL,
                button_text TEXT NOT NULL,
                button_url TEXT NOT NULL,
                position INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (message_key) REFERENCES custom_messages(message_key)
            )
            ''')
            
            # Add default welcome message
            default_welcome = "🌉 Welcome to KabirBridge!\nYour gateway to quick and efficient online services.\n✅ How to Use:\n1️⃣ Tap Services to browse available options.\n2️⃣ Select your desired service and follow the process.\n3️⃣ Complete your order and let the bot do the rest!\n💵 Payments: Safe and convenient payment options.\n📞 Support: +251907806267, @muay011\n🔹 Start now and experience instant results!"
            cursor.execute(
                "INSERT INTO custom_messages (message_key, message_text) VALUES (?, ?)",
                ("welcome", default_welcome)
            )
            
            self.conn.commit()
            logger.info("Created custom_messages tables and added default welcome message")
            return True
        
        return False
    
    def get_custom_message(self, message_key):
        """Get a custom message by key"""
        # Make sure the tables exist
        self.migrate_custom_messages_table()
        
        cursor = self.conn.cursor()
        try:
            # Get the message text
            cursor.execute(
                "SELECT message_text FROM custom_messages WHERE message_key = ?",
                (message_key,)
            )
            result = cursor.fetchone()
            message_text = result[0] if result else None
            
            # Get all media associated with this message
            cursor.execute(
                "SELECT media_type, file_id, caption, position FROM custom_message_media WHERE message_key = ? ORDER BY position ASC",
                (message_key,)
            )
            media = cursor.fetchall()
            media_list = [
                {
                    "type": m[0],
                    "file_id": m[1],
                    "caption": m[2],
                    "position": m[3]
                } for m in media
            ]
            
            # If we found a message or media, return the data
            if message_text or media_list:
                logger.info(f"Found custom message for key: {message_key}, text length: {len(message_text) if message_text else 0}, media items: {len(media_list)}")
                return {
                    "message_key": message_key,
                    "message_text": message_text,
                    "media": media_list
                }
            
            logger.info(f"No custom message found for key: {message_key}")
            return None
        except Exception as e:
            logger.error(f"Error fetching custom message: {e}")
            return None
    
    def update_custom_message_text(self, message_key, message_text):
        """Update or create a custom message"""
        # Make sure the tables exist
        self.migrate_custom_messages_table()
        
        cursor = self.conn.cursor()
        try:
            # Check if the message exists
            cursor.execute(
                "SELECT id FROM custom_messages WHERE message_key = ?",
                (message_key,)
            )
            result = cursor.fetchone()
            
            if result:
                # Update existing message
                cursor.execute(
                    "UPDATE custom_messages SET message_text = ?, updated_at = CURRENT_TIMESTAMP WHERE message_key = ?",
                    (message_text, message_key)
                )
            else:
                # Create new message
                cursor.execute(
                    "INSERT INTO custom_messages (message_key, message_text) VALUES (?, ?)",
                    (message_key, message_text)
                )
            
            self.conn.commit()
            logger.info(f"Updated custom message text for key: {message_key}")
            return True
        except Exception as e:
            logger.error(f"Error updating custom message: {e}")
            return False
    
    def add_custom_message_media(self, message_key, media_type, file_id, caption=None):
        """Add media to a custom message"""
        # Make sure the tables exist
        self.migrate_custom_messages_table()
        
        cursor = self.conn.cursor()
        try:
            # Get the next position value
            cursor.execute(
                "SELECT COALESCE(MAX(position), -1) + 1 FROM custom_message_media WHERE message_key = ?",
                (message_key,)
            )
            next_position = cursor.fetchone()[0]
            
            # Add the media
            cursor.execute(
                "INSERT INTO custom_message_media (message_key, media_type, file_id, caption, position) VALUES (?, ?, ?, ?, ?)",
                (message_key, media_type, file_id, caption, next_position)
            )
            
            # Make sure the message key exists in custom_messages
            cursor.execute(
                "SELECT id FROM custom_messages WHERE message_key = ?",
                (message_key,)
            )
            if not cursor.fetchone():
                # Create empty message if it doesn't exist
                cursor.execute(
                    "INSERT INTO custom_messages (message_key, message_text) VALUES (?, '')",
                    (message_key,)
                )
            
            self.conn.commit()
            logger.info(f"Added media to custom message: {message_key}, type: {media_type}")
            return True
        except Exception as e:
            logger.error(f"Error adding media to custom message: {e}")
            return False
    
    def delete_custom_message_media(self, media_id):
        """Delete media from a custom message"""
        cursor = self.conn.cursor()
        try:
            # Get message key for logging
            cursor.execute(
                "SELECT message_key FROM custom_message_media WHERE id = ?",
                (media_id,)
            )
            result = cursor.fetchone()
            message_key = result[0] if result else "unknown"
            
            # Delete the media
            cursor.execute(
                "DELETE FROM custom_message_media WHERE id = ?",
                (media_id,)
            )
            
            self.conn.commit()
            logger.info(f"Deleted media ID {media_id} from custom message: {message_key}")
            return True
        except Exception as e:
            logger.error(f"Error deleting media from custom message: {e}")
            return False
    
    def add_custom_message_button(self, message_key, button_text, button_url):
        """Add a button to a custom message"""
        # Make sure the tables exist
        self.migrate_custom_messages_table()
        
        cursor = self.conn.cursor()
        try:
            # Get the next position value
            cursor.execute(
                "SELECT COALESCE(MAX(position), -1) + 1 FROM custom_message_buttons WHERE message_key = ?",
                (message_key,)
            )
            next_position = cursor.fetchone()[0]
            
            # Add the button
            cursor.execute(
                "INSERT INTO custom_message_buttons (message_key, button_text, button_url, position) VALUES (?, ?, ?, ?)",
                (message_key, button_text, button_url, next_position)
            )
            
            # Make sure the message key exists in custom_messages
            cursor.execute(
                "SELECT id FROM custom_messages WHERE message_key = ?",
                (message_key,)
            )
            if not cursor.fetchone():
                # Create empty message if it doesn't exist
                cursor.execute(
                    "INSERT INTO custom_messages (message_key, message_text) VALUES (?, '')",
                    (message_key,)
                )
            
            self.conn.commit()
            logger.info(f"Added button to custom message: {message_key}, text: {button_text}")
            return True
        except Exception as e:
            logger.error(f"Error adding button to custom message: {e}")
            return False
    
    def delete_custom_message_button(self, button_id):
        """Delete a button from a custom message"""
        cursor = self.conn.cursor()
        try:
            # Get message key for logging
            cursor.execute(
                "SELECT message_key FROM custom_message_buttons WHERE id = ?",
                (button_id,)
            )
            result = cursor.fetchone()
            message_key = result[0] if result else "unknown"
            
            # Delete the button
            cursor.execute(
                "DELETE FROM custom_message_buttons WHERE id = ?",
                (button_id,)
            )
            
            self.conn.commit()
            logger.info(f"Deleted button ID {button_id} from custom message: {message_key}")
            return True
        except Exception as e:
            logger.error(f"Error deleting button from custom message: {e}")
            return False
            
    def count_custom_message_media(self, message_key):
        """Count the number of media items for a custom message"""
        cursor = self.conn.cursor()
        try:
            cursor.execute(
                "SELECT COUNT(*) FROM custom_message_media WHERE message_key = ?",
                (message_key,)
            )
            count = cursor.fetchone()[0]
            return count
        except Exception as e:
            logger.error(f"Error counting media for custom message: {e}")
            return 0
            
    def count_custom_message_buttons(self, message_key):
        """Count the number of buttons for a custom message"""
        cursor = self.conn.cursor()
        try:
            cursor.execute(
                "SELECT COUNT(*) FROM custom_message_buttons WHERE message_key = ?",
                (message_key,)
            )
            count = cursor.fetchone()[0]
            return count
        except Exception as e:
            logger.error(f"Error counting buttons for custom message: {e}")
            return 0
            
    def clear_custom_message_media(self, message_key):
        """Remove all media for a custom message"""
        cursor = self.conn.cursor()
        try:
            cursor.execute(
                "DELETE FROM custom_message_media WHERE message_key = ?",
                (message_key,)
            )
            self.conn.commit()
            logger.info(f"Cleared all media for message key: {message_key}")
            return True
        except Exception as e:
            logger.error(f"Error clearing media for custom message: {e}")
            return False

    def add_refund(self, user_id, order_id, amount, reason="Order Refund"):
        """Add a refund to user's balance and record the refund transaction"""
        try:
            conn = sqlite3.connect(os.getenv('DB_FILE', 'data/smm_bot.db'), check_same_thread=False)
            cursor = conn.cursor()
            
            # Add the refund amount to user's balance
            cursor.execute("""
                UPDATE users 
                SET balance = balance + ? 
                WHERE user_id = ?
            """, (amount, user_id))
            
            # Record the refund transaction
            cursor.execute("""
                INSERT INTO transactions 
                (user_id, type, amount, description, order_id) 
                VALUES (?, 'refund', ?, ?, ?)
            """, (user_id, amount, reason, order_id))
            
            # Update order status to refunded
            cursor.execute("""
                UPDATE orders
                SET status = 'refunded', refunded_at = CURRENT_TIMESTAMP
                WHERE id = ? AND user_id = ?
            """, (order_id, user_id))
            
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error adding refund: {e}")
            return False
        finally:
            conn.close()

    def get_order_details(self, order_id):
        """Get order details including user_id and amount"""
        try:
            conn = sqlite3.connect(os.getenv('DB_FILE', 'data/smm_bot.db'), check_same_thread=False)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT user_id, price, status, service_name
                FROM orders
                WHERE id = ?
            """, (order_id,))
            
            result = cursor.fetchone()
            if result:
                return {
                    'user_id': result[0],
                    'price': result[1],
                    'status': result[2],
                    'service_name': result[3]
                }
            return None
        except Exception as e:
            logger.error(f"Error getting order details: {e}")
            return None
        finally:
            conn.close()

    def mark_order_refunded(self, order_id):
        """Mark an order as refunded"""
        try:
            conn = sqlite3.connect(os.getenv('DB_FILE', 'data/smm_bot.db'), check_same_thread=False)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE orders
                SET status = 'refunded', refunded_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (order_id,))
            
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error marking order as refunded: {e}")
            return False
        finally:
            conn.close()

    def has_user_valid_bonus(self, user_id):
        """Check if a user has any valid bonus codes"""
        cursor = self.conn.cursor()
        
        # Check for any active bonus codes in the bonus_codes table
        cursor.execute('''
            SELECT COUNT(*) FROM bonus_codes 
            WHERE user_id = ? AND used = 0 AND expires_at > datetime('now')
        ''', (user_id,))
        
        bonus_count = cursor.fetchone()[0]
        
        # Also check for any pending referral bonuses
        cursor.execute('''
            SELECT COUNT(*) FROM referral_bonuses 
            WHERE user_id = ? AND status = 'pending'
        ''', (user_id,))
        
        pending_bonuses = cursor.fetchone()[0]
        
        # Return True if the user has either valid bonus codes or pending referral bonuses
        return bonus_count > 0 or pending_bonuses > 0

# Create global database instance
db = Database() 