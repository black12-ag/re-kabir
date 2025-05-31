# Telegram Bot - Kabir Bridge

A Telegram bot for managing orders and services on social media platforms.

## Setup Instructions

### Local Development

1. Clone this repository:
   ```bash
   git clone https://github.com/black12-ag/re-kabir.git
   cd re-kabir
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file with your bot token:
   ```
   TELEGRAM_BOT_TOKEN=your_bot_token
   ADMIN_USER_ID=your_admin_id
   ```

5. Run the bot:
   ```bash
   python run.py
   ```

### Railway Deployment

This bot is configured for Railway deployment with webhook support:

1. Push the code to GitHub
2. Create a new project on Railway
3. Connect to this GitHub repository
4. Set these environment variables:
   - `TELEGRAM_BOT_TOKEN`
   - `ADMIN_USER_ID`
   - `WEBHOOK_MODE=true`
   - `PORT=8080`

## Features

- Multi-language support
- Order management
- Balance tracking
- Admin management panel
- Webhook support for Railway

## Overview

Kabir Bridge is a feature-rich Telegram bot that serves as a gateway to various online services. It provides a user-friendly interface with multilingual support, making it accessible to users worldwide.

## Features

- **Multilingual Support**: Available in English, Amharic, Arabic, Hindi, Spanish, Chinese, and Turkish
- **Command Menu**: Easy-to-use persistent keyboard with common commands
- **Service Catalog**: Browse and order from a wide range of online services
- **Order Management**: Place orders and track their status
- **Account Management**: Check balance and recharge your account
- **Referral System**: Invite friends and earn rewards
- **Admin Panel**: Comprehensive tools for administrators

## Commands

- `/start` - Start the bot and see the welcome message
- `/services` - Browse available services
- `/order` - Place a new order
- `/status` - Check order status
- `/balance` - Check your balance
- `/recharge` - Add funds to your account
- `/help` - Get help and support
- `/menu` - Show/hide the command menu
- `/my_orders` - View your orders
- `/check_order` - Check a specific order
- `/referrals` - Access the referral program
- `/more` - See additional options
- `/customer_service` - Contact support

## Support

For support, contact:
- Phone: +251907806267
- Telegram: @muay011

## License

This project is proprietary software. All rights reserved.

---

© 2025 Kabir Bridge. All rights reserved. 