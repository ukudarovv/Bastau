"""Support handlers"""
from aiogram import Router, F
from aiogram.types import Message, BotCommand
from aiogram.fsm.context import FSMContext

from bot.services.api_client import APIClient
from bot.keyboards.inline import get_cancel_keyboard
from bot.keyboards.reply import get_main_menu
from bot.states.support import SupportForm
from bot.utils.formatters import format_support_ticket_summary
from bot.config import ADMIN_TELEGRAM_ID, BOT_TOKEN
from aiogram import Bot

router = Router()


@router.message(F.text == "Тех поддержка")
async def show_support_menu(message: Message, state: FSMContext):
    """Show support menu"""
    await message.answer(
        "<b>Техническая поддержка</b>\n\n"
        "Опишите вашу проблему или вопрос.\n\n"
        "Пожалуйста, укажите тему обращения (кратко):",
        reply_markup=get_cancel_keyboard(),
        parse_mode="HTML"
    )
    await state.set_state(SupportForm.subject)


@router.message(SupportForm.subject, F.text)
async def process_support_subject(message: Message, state: FSMContext):
    """Process support subject"""
    subject = message.text.strip()
    
    if len(subject) < 3:
        await message.answer(
            "Тема обращения слишком короткая (минимум 3 символа). Попробуйте еще раз:",
            reply_markup=get_cancel_keyboard()
        )
        return
    
    if len(subject) > 100:
        await message.answer(
            "Тема обращения слишком длинная (максимум 100 символов). Сократите и попробуйте еще раз:",
            reply_markup=get_cancel_keyboard()
        )
        return
    
    await state.update_data(subject=subject)
    
    await message.answer(
        f"<b>Тема:</b> {subject}\n\n"
        "Теперь опишите вашу проблему или вопрос подробнее:",
        reply_markup=get_cancel_keyboard(),
        parse_mode="HTML"
    )
    await state.set_state(SupportForm.message)


@router.message(SupportForm.message, F.text)
async def process_support_message(message: Message, state: FSMContext):
    """Process support message and create ticket"""
    support_text = message.text.strip()
    
    if len(support_text) < 10:
        await message.answer(
            "Сообщение слишком короткое (минимум 10 символов). Попробуйте еще раз:",
            reply_markup=get_cancel_keyboard()
        )
        return
    
    if len(support_text) > 2000:
        await message.answer(
            "Сообщение слишком длинное (максимум 2000 символов). Сократите и попробуйте еще раз:",
            reply_markup=get_cancel_keyboard()
        )
        return
    
    data = await state.get_data()
    subject = data.get('subject', 'Без темы')
    
    # Combine subject and message
    full_message = f"Тема: {subject}\n\n{support_text}"
    
    api_client = APIClient()
    try:
        # Get user
        user = await api_client.get_user_by_telegram_id(message.from_user.id)
        if not user:
            await message.answer(
                "Сначала зарегистрируйтесь через /start",
                reply_markup=get_main_menu()
            )
            await state.clear()
            return
        
        # Create support request
        ticket = await api_client.create_support_request(
            user_id=user['id'],
            detail=full_message
        )
        
        # Format and send confirmation
        summary = format_support_ticket_summary(ticket)
        await message.answer(
            summary,
            reply_markup=get_main_menu(),
            parse_mode="HTML"
        )
        
        # Notify admin
        if ADMIN_TELEGRAM_ID:
            try:
                bot = Bot(token=BOT_TOKEN)
                admin_message = (
                    f"<b>Новое обращение в поддержку</b>\n\n"
                    f"<b>Номер:</b> #{ticket.get('id')}\n"
                    f"<b>Пользователь:</b> {user.get('detail', 'N/A')} (ID: {user.get('telegram_id')})\n"
                    f"<b>Сообщение:</b>\n{full_message}"
                )
                await bot.send_message(
                    chat_id=ADMIN_TELEGRAM_ID,
                    text=admin_message,
                    parse_mode="HTML"
                )
                await bot.session.close()
            except Exception as e:
                # Log error but don't fail the request
                print(f"Failed to notify admin: {str(e)}")
        
        await state.clear()
    except Exception as e:
        await message.answer(
            f"Ошибка при создании обращения: {str(e)}\n\n"
            "Попробуйте позже или обратитесь напрямую к администратору.",
            reply_markup=get_main_menu()
        )
    finally:
        await api_client.close()

