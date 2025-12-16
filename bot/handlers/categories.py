"""Categories and doctors handlers"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from bot.services.api_client import APIClient
from bot.keyboards.inline import (
    get_categories_keyboard,
    get_doctors_keyboard,
    get_doctor_card_keyboard,
    get_back_to_menu_keyboard
)
from bot.keyboards.reply import get_main_menu
from bot.utils.formatters import format_doctor_card
from bot.states.review import ReviewForm
from bot.config import ITEMS_PER_PAGE

router = Router()


@router.message(F.text == "Категории")
async def show_categories(message: Message, state: FSMContext):
    """Show categories list"""
    api_client = APIClient()
    
    try:
        categories = await api_client.get_categories()
        
        if not categories:
            await message.answer(
                "Категории врачей\n\n"
                "К сожалению, категории пока не добавлены.",
                reply_markup=get_main_menu()
            )
            return
        
        await message.answer(
            "<b>Выберите категорию врача:</b>",
            reply_markup=get_categories_keyboard(categories, page=0, items_per_page=ITEMS_PER_PAGE),
            parse_mode="HTML"
        )
    except Exception as e:
        await message.answer(
            f"Ошибка при загрузке категорий: {str(e)}",
            reply_markup=get_main_menu()
        )
    finally:
        await api_client.close()


@router.callback_query(F.data.startswith("categories_page_"))
async def process_categories_pagination(callback: CallbackQuery):
    """Process categories pagination"""
    page = int(callback.data.split("_")[2])
    
    api_client = APIClient()
    try:
        categories = await api_client.get_categories()
        await callback.message.edit_reply_markup(
            reply_markup=get_categories_keyboard(categories, page=page, items_per_page=ITEMS_PER_PAGE)
        )
        await callback.answer()
    except Exception as e:
        await callback.answer(f"Ошибка: {str(e)}", show_alert=True)
    finally:
        await api_client.close()


@router.callback_query(F.data.startswith("category_"))
async def show_doctors_by_category(callback: CallbackQuery, state: FSMContext):
    """Show doctors by category"""
    category_id = int(callback.data.split("_")[1])
    
    api_client = APIClient()
    try:
        doctors = await api_client.get_doctors_by_category(category_id)
        
        if not doctors:
            await callback.message.edit_text(
                "Врачи\n\n"
                "В этой категории пока нет врачей.",
                reply_markup=get_back_to_menu_keyboard()
            )
            await callback.answer()
            return
        
        # Store category_id in state for pagination
        await state.update_data(category_id=category_id)
        
        category_name = doctors[0].get('category', {}).get('title', 'Категория') if doctors and doctors[0].get('category') else 'Категория'
        
        await callback.message.edit_text(
            f"<b>Врачи категории: {category_name}</b>\n\n"
            "Выберите врача:",
            reply_markup=get_doctors_keyboard(doctors, page=0, items_per_page=ITEMS_PER_PAGE, category_id=category_id),
            parse_mode="HTML"
        )
        await callback.answer()
    except Exception as e:
        await callback.answer(f"Ошибка: {str(e)}", show_alert=True)
    finally:
        await api_client.close()


@router.callback_query(F.data.startswith("doctors_page_"))
async def process_doctors_pagination(callback: CallbackQuery, state: FSMContext):
    """Process doctors pagination"""
    parts = callback.data.split("_")
    page = int(parts[2])
    category_id = None
    
    # Check if category_id is in callback data
    if len(parts) > 3 and parts[3] == "cat":
        category_id = int(parts[4])
    
    api_client = APIClient()
    try:
        if category_id:
            doctors = await api_client.get_doctors_by_category(category_id)
        else:
            doctors = await api_client.get_all_doctors()
        
        await callback.message.edit_reply_markup(
            reply_markup=get_doctors_keyboard(doctors, page=page, items_per_page=ITEMS_PER_PAGE, category_id=category_id)
        )
        await callback.answer()
    except Exception as e:
        await callback.answer(f"Ошибка: {str(e)}", show_alert=True)
    finally:
        await api_client.close()


@router.callback_query(F.data.startswith("doctor_"))
async def show_doctor_card(callback: CallbackQuery, state: FSMContext):
    """Show doctor card"""
    doctor_id = int(callback.data.split("_")[1])
    
    api_client = APIClient()
    try:
        doctor = await api_client.get_doctor(doctor_id)
        
        if not doctor or not doctor.get('doctor'):
            await callback.answer("Врач не найден", show_alert=True)
            return
        
        # Add rating and reviews count
        doctor['rating'] = doctor.get('rating')
        doctor['reviews_count'] = doctor.get('reviews_count', 0)
        
        card_text = format_doctor_card(doctor)
        
        await state.update_data(current_doctor_id=doctor_id)
        
        await callback.message.edit_text(
            card_text,
            reply_markup=get_doctor_card_keyboard(doctor_id),
            parse_mode="HTML"
        )
        await callback.answer()
    except Exception as e:
        await callback.answer(f"Ошибка: {str(e)}", show_alert=True)
    finally:
        await api_client.close()


@router.callback_query(F.data.startswith("review_doctor_"))
async def start_review(callback: CallbackQuery, state: FSMContext):
    """Start review creation process"""
    doctor_id = int(callback.data.split("_")[2])
    
    api_client = APIClient()
    try:
        # Check if user exists
        user = await api_client.get_user_by_telegram_id(callback.from_user.id)
        if not user:
            await callback.answer("Сначала зарегистрируйтесь через /start", show_alert=True)
            return
        
        # Check if review already exists
        review_exists = await api_client.check_review_exists(user['id'], doctor_id)
        if review_exists:
            await callback.answer(
                "Вы уже оставляли отзыв этому врачу. Можно оставить только один отзыв.",
                show_alert=True
            )
            return
        
        await state.update_data(doctor_id=doctor_id, user_id=user['id'])
        
        from bot.keyboards.inline import get_rating_keyboard
        
        await callback.message.edit_text(
            "<b>Оставить отзыв</b>\n\n"
            "Выберите оценку (1-5 звезд):",
            reply_markup=get_rating_keyboard(),
            parse_mode="HTML"
        )
        await state.set_state(ReviewForm.rating)
        await callback.answer()
    except Exception as e:
        await callback.answer(f"Ошибка: {str(e)}", show_alert=True)
    finally:
        await api_client.close()


@router.callback_query(F.data.startswith("view_reviews_"))
async def view_doctor_reviews(callback: CallbackQuery):
    """View reviews for a doctor"""
    doctor_id = int(callback.data.split("_")[2])
    
    api_client = APIClient()
    try:
        reviews = await api_client.get_reviews_by_doctor(doctor_id)
        
        if not reviews:
            await callback.message.edit_text(
                "<b>Отзывы о враче</b>\n\n"
                "Пока нет отзывов.",
                reply_markup=get_back_to_menu_keyboard(),
                parse_mode="HTML"
            )
            await callback.answer()
            return
        
        from bot.utils.formatters import format_reviews_list
        
        text = format_reviews_list(reviews, "Отзывы о враче")
        
        await callback.message.edit_text(
            text,
            reply_markup=get_back_to_menu_keyboard(),
            parse_mode="HTML"
        )
        await callback.answer()
    except Exception as e:
        await callback.answer(f"Ошибка: {str(e)}", show_alert=True)
    finally:
        await api_client.close()


@router.callback_query(F.data == "back_to_categories")
async def back_to_categories(callback: CallbackQuery, state: FSMContext):
    """Go back to categories"""
    await state.clear()
    
    api_client = APIClient()
    try:
        categories = await api_client.get_categories()
        await callback.message.edit_text(
            "<b>Выберите категорию врача:</b>",
            reply_markup=get_categories_keyboard(categories, page=0, items_per_page=ITEMS_PER_PAGE),
            parse_mode="HTML"
        )
        await callback.answer()
    except Exception as e:
        await callback.answer(f"Ошибка: {str(e)}", show_alert=True)
    finally:
        await api_client.close()


@router.callback_query(F.data == "back_to_doctors")
async def back_to_doctors(callback: CallbackQuery, state: FSMContext):
    """Go back to doctors list"""
    data = await state.get_data()
    category_id = data.get('category_id')
    
    api_client = APIClient()
    try:
        if category_id:
            doctors = await api_client.get_doctors_by_category(category_id)
            category_name = doctors[0].get('category', {}).get('title', 'Категория') if doctors and doctors[0].get('category') else 'Категория'
            await callback.message.edit_text(
                f"<b>Врачи категории: {category_name}</b>\n\n"
                "Выберите врача:",
                reply_markup=get_doctors_keyboard(doctors, page=0, items_per_page=ITEMS_PER_PAGE, category_id=category_id),
                parse_mode="HTML"
            )
        else:
            await callback.answer("Не удалось вернуться к списку врачей", show_alert=True)
        await callback.answer()
    except Exception as e:
        await callback.answer(f"Ошибка: {str(e)}", show_alert=True)
    finally:
        await api_client.close()

