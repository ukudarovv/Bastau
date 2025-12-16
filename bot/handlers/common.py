"""Common handlers for errors and unknown commands"""
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from bot.keyboards.reply import get_main_menu

router = Router()


@router.message(F.text)
async def handle_unknown_message(message: Message, state: FSMContext):
    """Handle unknown text messages"""
    current_state = await state.get_state()
    
    # If user is in some FSM state, don't show error
    if current_state:
        # Let other handlers process it
        return
    
    # Check if it's a known menu command (should be handled by other routers)
    known_commands = [
        "Категории", "Рейтинг врачей", "Рейтинг клиник",
        "Мои отзывы", "Тех поддержка", "В меню", "Главное меню", "Меню"
    ]
    
    if message.text in known_commands:
        # Let other handlers process it
        return
    
    # Unknown command/message
    await message.answer(
        "Неизвестная команда.\n\n"
        "Используйте меню для навигации или отправьте /start",
        reply_markup=get_main_menu()
    )


@router.message()
async def handle_unknown_content(message: Message):
    """Handle unknown content types (media, etc.)"""
    await message.answer(
        "Я не понимаю этот тип сообщения.\n\n"
        "Пожалуйста, используйте текстовые команды или меню.",
        reply_markup=get_main_menu()
    )

