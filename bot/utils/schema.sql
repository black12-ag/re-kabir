-- Add refunded_at column to orders table if it doesn't exist
ALTER TABLE orders ADD COLUMN refunded_at TIMESTAMP;

-- Make sure transactions table has order_id field
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    type TEXT NOT NULL,  -- 'deposit', 'order', 'refund'
    amount REAL NOT NULL,
    description TEXT,
    order_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (order_id) REFERENCES orders(id)
);

-- Create index for faster refund checking
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
CREATE INDEX IF NOT EXISTS idx_transactions_type ON transactions(type); 