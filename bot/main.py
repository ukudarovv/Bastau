"""Main entry point for Telegram bot"""
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from bot.config import BOT_TOKEN
from bot.middlewares.logging import LoggingMiddleware
from bot.middlewares.throttling import ThrottlingMiddleware

# Import handlers
from bot.handlers import (
    start,
    registration,
    menu,
    categories,
    ratings,
    reviews,
    support,
    common
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """Main function to run the bot"""
    # Initialize bot and dispatcher
    bot = Bot(token=BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    # Register middlewares
    dp.message.middleware(LoggingMiddleware())
    dp.callback_query.middleware(LoggingMiddleware())
    dp.message.middleware(ThrottlingMiddleware())
    dp.callback_query.middleware(ThrottlingMiddleware())
    
    # Register routers (handlers)
    # Order matters: more specific handlers should be registered first
    # Common handler should be last to catch unknown messages
    dp.include_router(start.router)
    dp.include_router(registration.router)
    dp.include_router(categories.router)
    dp.include_router(ratings.router)
    dp.include_router(reviews.router)
    dp.include_router(support.router)
    dp.include_router(menu.router)
    dp.include_router(common.router)
    
    # Set bot commands
    await bot.set_my_commands([
        {"command": "start", "description": "Начать работу с ботом"}
    ])
    
    logger.info("Bot started")
    
    # Start polling
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot error: {str(e)}", exc_info=True)

