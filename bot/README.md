# SMM Services Telegram Bot

A Telegram bot that sells Social Media Marketing (SMM) services using the AmazingSMM API.

## Features

- Browse available SMM services
- Place orders for social media services
- Check account balance
- View order status
- Admin panel with statistics and broadcast functionality

## Requirements

- Python 3.7+
- Telegram Bot Token
- AmazingSMM API credentials

## Installation

1. Clone this repository
2. Install the requirements:
   ```
   pip install -r requirements.txt
   ```
3. Create a `.env` file with the following configuration:
   ```
   TELEGRAM_BOT_TOKEN=your_bot_token
   API_KEY=your_api_key
   API_URL=your_api_url
   ADMIN_USER_ID=your_telegram_user_id
   ```

## Usage

Run the bot:
```
python bot.py
```

## Bot Commands

- `/start` - Start the bot and show main menu
- `/services` - Show available services
- `/order` - Place a new order
- `/balance` - Check your account balance
- `/status` - Check order status
- `/help` - Show help message
- `/admin` - Access admin panel (admin only)

## Admin Commands

- **Stats** - View bot statistics
- **Broadcast** - Send a message to all users
- **Balance** - Check account balance

## License

This project is licensed under the MIT License. 