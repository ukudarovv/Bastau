"""Reviews handlers"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from bot.services.api_client import APIClient
from bot.keyboards.inline import (
    get_rating_keyboard,
    get_cancel_keyboard,
    get_back_to_menu_keyboard
)
from bot.keyboards.reply import get_main_menu
from bot.states.review import ReviewForm
from bot.utils.formatters import format_user_review, format_reviews_list

router = Router()


@router.callback_query(ReviewForm.rating, F.data.startswith("rating_"))
async def process_rating_selection(callback: CallbackQuery, state: FSMContext):
    """Process rating selection"""
    rating = int(callback.data.split("_")[1])
    
    await state.update_data(rating=rating)
    
    await callback.message.edit_text(
        f"<b>Оценка: {rating}/5</b>\n\n"
        "Теперь напишите текст отзыва (до 1000 символов):",
        reply_markup=get_cancel_keyboard(),
        parse_mode="HTML"
    )
    await state.set_state(ReviewForm.text)
    await callback.answer()


@router.callback_query(ReviewForm.rating, F.data == "cancel_review")
async def cancel_review(callback: CallbackQuery, state: FSMContext):
    """Cancel review creation"""
    await state.clear()
    await callback.message.edit_text(
        "Создание отзыва отменено.",
        reply_markup=get_back_to_menu_keyboard()
    )
    await callback.answer()


@router.message(ReviewForm.text, F.text)
async def process_review_text(message: Message, state: FSMContext):
    """Process review text"""
    text = message.text.strip()
    
    if len(text) < 10:
        await message.answer(
            "Текст отзыва должен содержать минимум 10 символов. Попробуйте еще раз:",
            reply_markup=get_cancel_keyboard()
        )
        return
    
    if len(text) > 1000:
        await message.answer(
            "Текст отзыва слишком длинный (максимум 1000 символов). Сократите и попробуйте еще раз:",
            reply_markup=get_cancel_keyboard()
        )
        return
    
    data = await state.get_data()
    doctor_id = data.get('doctor_id')
    user_id = data.get('user_id')
    rating = data.get('rating')
    
    api_client = APIClient()
    try:
        # Create review
        review = await api_client.create_review(
            user_id=user_id,
            doctor_id=doctor_id,
            rating=rating,
            detail=text
        )
        
        await message.answer(
            "<b>Отзыв успешно добавлен!</b>\n\n"
            "Спасибо за ваш отзыв. Он поможет другим пользователям сделать правильный выбор.",
            reply_markup=get_main_menu(),
            parse_mode="HTML"
        )
        await state.clear()
    except Exception as e:
        error_msg = str(e)
        if "already exists" in error_msg.lower() or "уже" in error_msg.lower():
            await message.answer(
                "Вы уже оставляли отзыв этому врачу. Можно оставить только один отзыв.",
                reply_markup=get_main_menu()
            )
        else:
            await message.answer(
                f"Ошибка при создании отзыва: {error_msg}",
                reply_markup=get_main_menu()
            )
    finally:
        await api_client.close()


@router.callback_query(F.data == "cancel")
async def cancel_action(callback: CallbackQuery, state: FSMContext):
    """Cancel current action"""
    await state.clear()
    await callback.message.edit_text(
        "Действие отменено.",
        reply_markup=get_back_to_menu_keyboard()
    )
    await callback.answer()


@router.message(F.text == "Мои отзывы")
async def show_my_reviews(message: Message, state: FSMContext):
    """Show user's reviews"""
    api_client = APIClient()
    
    try:
        # Get user
        user = await api_client.get_user_by_telegram_id(message.from_user.id)
        if not user:
            await message.answer(
                "Сначала зарегистрируйтесь через /start",
                reply_markup=get_main_menu()
            )
            return
        
        # Get user's reviews
        reviews = await api_client.get_reviews_by_user(user['id'])
        
        if not reviews:
            await message.answer(
                "<b>Мои отзывы</b>\n\n"
                "Вы еще не оставляли отзывов.",
                reply_markup=get_main_menu(),
                parse_mode="HTML"
            )
            return
        
        # Format reviews list
        text = "<b>Мои отзывы</b>\n\n"
        for i, review in enumerate(reviews, 1):
            doctor = review.get('doctor', {})
            doctor_name = doctor.get('detail', 'Врач') if doctor else 'Врач'
            rating = review.get('rating', 0)
            review_text = review.get('detail', '')
            created_at = review.get('created_at', '')
            
            # Truncate long reviews
            if len(review_text) > 150:
                review_text = review_text[:150] + "..."
            
            text += f"{i}. <b>{doctor_name}</b>\n"
            text += f"   Оценка: {rating}/5\n"
            text += f"   {review_text}\n"
            if created_at:
                text += f"   {created_at}\n"
            text += "\n"
        
        await message.answer(
            text,
            reply_markup=get_main_menu(),
            parse_mode="HTML"
        )
    except Exception as e:
        await message.answer(
            f"Ошибка при загрузке отзывов: {str(e)}",
            reply_markup=get_main_menu()
        )
    finally:
        await api_client.close()

