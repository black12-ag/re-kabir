#!/bin/bash

# Activate virtual environment if exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Install requirements if needed
pip3 install --user -r requirements.txt

# Start the bot
python3 bot.py