"""Throttling middleware to prevent spam"""
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery

from bot.config import REVIEW_COOLDOWN_HOURS


class ThrottlingMiddleware(BaseMiddleware):
    """Middleware to throttle user requests"""
    
    def __init__(self):
        self.user_last_message = defaultdict(lambda: datetime.min)
        self.user_review_timestamps = defaultdict(dict)  # {user_id: {doctor_id: timestamp}}
        self.message_throttle_seconds = 1  # Minimum seconds between messages
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        """Process middleware"""
        if isinstance(event, (Message, CallbackQuery)):
            user_id = event.from_user.id if hasattr(event, 'from_user') else None
            
            if user_id:
                # Check message throttling
                now = datetime.now()
                last_message_time = self.user_last_message[user_id]
                
                if (now - last_message_time).total_seconds() < self.message_throttle_seconds:
                    # Too frequent messages, skip
                    if isinstance(event, Message):
                        await event.answer("Пожалуйста, подождите немного перед следующим действием.")
                    elif isinstance(event, CallbackQuery):
                        await event.answer("Подождите немного", show_alert=False)
                    return
                
                self.user_last_message[user_id] = now
        
        return await handler(event, data)
    
    def can_user_review_doctor(self, user_id: int, doctor_id: int) -> bool:
        """Check if user can review a doctor (cooldown check)"""
        user_reviews = self.user_review_timestamps[user_id]
        
        if doctor_id in user_reviews:
            last_review_time = user_reviews[doctor_id]
            hours_passed = (datetime.now() - last_review_time).total_seconds() / 3600
            
            if hours_passed < REVIEW_COOLDOWN_HOURS:
                return False
        
        return True
    
    def record_review(self, user_id: int, doctor_id: int):
        """Record that user left a review for a doctor"""
        self.user_review_timestamps[user_id][doctor_id] = datetime.now()

