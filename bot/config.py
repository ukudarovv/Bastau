"""Configuration module for Telegram bot"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Bot configuration
BOT_TOKEN = "7716388596:AAEjJMs8kpKxMEpSBvMTpquqH9eMcoZq2V4"
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable is not set")

# API configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8001/api")

# Admin configuration
ADMIN_TELEGRAM_ID = os.getenv("ADMIN_TELEGRAM_ID")
if ADMIN_TELEGRAM_ID:
    try:
        ADMIN_TELEGRAM_ID = int(ADMIN_TELEGRAM_ID)
    except ValueError:
        ADMIN_TELEGRAM_ID = None

# Pagination settings
ITEMS_PER_PAGE = 10

# Throttling settings
REVIEW_COOLDOWN_HOURS = 24  # Hours between reviews for the same doctor

