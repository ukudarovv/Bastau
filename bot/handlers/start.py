"""Start command handler"""
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from bot.services.api_client import APIClient
from bot.keyboards.reply import get_main_menu, get_consent_keyboard
from bot.states.registration import RegistrationForm

router = Router()


@router.message(F.text == "/start")
async def cmd_start(message: Message, state: FSMContext):
    """Handle /start command"""
    api_client = APIClient()
    
    try:
        # Check if user already exists
        user = await api_client.get_user_by_telegram_id(message.from_user.id)
        
        if user:
            # User already registered, show main menu
            await message.answer(
                f"Добро пожаловать обратно, {user.get('detail', 'пользователь')}!\n\n"
                "Выберите действие из меню:",
                reply_markup=get_main_menu()
            )
            await state.clear()
        else:
            # New user, start registration
            await message.answer(
                "Добро пожаловать в бот \"Рейтинг врачей и клиник\"!\n\n"
                "Этот бот поможет вам:\n"
                "• Найти врачей по категориям\n"
                "• Посмотреть рейтинги врачей и клиник\n"
                "• Оставить отзывы о врачах\n"
                "• Получить помощь в техподдержке\n\n"
                "Для использования бота необходимо дать согласие на обработку персональных данных.",
                reply_markup=get_consent_keyboard()
            )
            await state.set_state(RegistrationForm.waiting_consent)
    except Exception as e:
        await message.answer(
            f"Произошла ошибка при проверке регистрации. Попробуйте позже.\n\n"
            f"Ошибка: {str(e)}"
        )
    finally:
        await api_client.close()

