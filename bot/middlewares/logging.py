"""Logging middleware"""
import logging
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery, Update

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseMiddleware):
    """Middleware for logging user actions"""
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        """Process middleware"""
        if isinstance(event, Message):
            user_id = event.from_user.id if event.from_user else None
            username = event.from_user.username if event.from_user else None
            text = event.text or event.caption or "[media]"
            
            logger.info(
                f"Message from user {user_id} (@{username}): {text[:100]}"
            )
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id if event.from_user else None
            username = event.from_user.username if event.from_user else None
            data_text = event.data or "[no data]"
            
            logger.info(
                f"Callback from user {user_id} (@{username}): {data_text}"
            )
        
        try:
            result = await handler(event, data)
            return result
        except Exception as e:
            logger.error(
                f"Error in handler: {str(e)}",
                exc_info=True
            )
            raise

