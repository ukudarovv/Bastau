"""Ratings handlers for doctors and clinics"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from bot.services.api_client import APIClient
from bot.keyboards.inline import (
    get_doctors_keyboard,
    get_clinics_keyboard,
    get_doctor_card_keyboard,
    get_clinic_card_keyboard,
    get_back_to_menu_keyboard
)
from bot.keyboards.reply import get_main_menu
from bot.utils.formatters import format_doctor_card, format_clinic_card
from bot.config import ITEMS_PER_PAGE

router = Router()


@router.message(F.text == "Рейтинг врачей")
async def show_doctors_rating(message: Message, state: FSMContext):
    """Show top doctors by rating"""
    api_client = APIClient()
    
    try:
        doctors = await api_client.get_doctors_rating()
        
        if not doctors:
            await message.answer(
                "<b>Рейтинг врачей</b>\n\n"
                "Пока нет врачей с отзывами.",
                reply_markup=get_main_menu(),
                parse_mode="HTML"
            )
            return
        
        # Format top doctors list
        text = "<b>Топ врачей по рейтингу</b>\n\n"
        for i, doctor in enumerate(doctors[:10], 1):  # Show top 10 in message
            name = doctor.get('detail', 'Врач')
            category = doctor.get('category', {}).get('title', '') if doctor.get('category') else ''
            clinic = doctor.get('clinic', {}).get('title', '') if doctor.get('clinic') else ''
            rating = doctor.get('rating', 0)
            reviews_count = doctor.get('reviews_count', 0)
            
            text += f"{i}. {name}"
            if category:
                text += f" ({category})"
            if clinic:
                text += f" - {clinic}"
            text += f" Рейтинг: {rating:.1f} ({reviews_count} отзывов)\n"
        
        await message.answer(
            text,
            reply_markup=get_doctors_keyboard(doctors, page=0, items_per_page=ITEMS_PER_PAGE),
            parse_mode="HTML"
        )
    except Exception as e:
        await message.answer(
            f"Ошибка при загрузке рейтинга врачей: {str(e)}",
            reply_markup=get_main_menu()
        )
    finally:
        await api_client.close()


@router.message(F.text == "Рейтинг клиник")
async def show_clinics_rating(message: Message, state: FSMContext):
    """Show top clinics by rating"""
    api_client = APIClient()
    
    try:
        clinics = await api_client.get_clinics_rating()
        
        if not clinics:
            await message.answer(
                "<b>Рейтинг клиник</b>\n\n"
                "Пока нет клиник с отзывами.",
                reply_markup=get_main_menu(),
                parse_mode="HTML"
            )
            return
        
        # Format top clinics list
        text = "<b>Топ клиник по рейтингу</b>\n\n"
        for i, clinic in enumerate(clinics[:10], 1):  # Show top 10 in message
            name = clinic.get('title', 'Клиника')
            address = clinic.get('address', '')
            rating = clinic.get('rating', 0)
            reviews_count = clinic.get('reviews_count', 0)
            
            text += f"{i}. {name}"
            if address:
                text += f" ({address[:30]}...)" if len(address) > 30 else f" ({address})"
            text += f" Рейтинг: {rating:.1f} ({reviews_count} отзывов)\n"
        
        await message.answer(
            text,
            reply_markup=get_clinics_keyboard(clinics, page=0, items_per_page=ITEMS_PER_PAGE),
            parse_mode="HTML"
        )
    except Exception as e:
        await message.answer(
            f"Ошибка при загрузке рейтинга клиник: {str(e)}",
            reply_markup=get_main_menu()
        )
    finally:
        await api_client.close()


@router.callback_query(F.data.startswith("clinics_page_"))
async def process_clinics_pagination(callback: CallbackQuery):
    """Process clinics pagination"""
    page = int(callback.data.split("_")[2])
    
    api_client = APIClient()
    try:
        clinics = await api_client.get_clinics_rating()
        await callback.message.edit_reply_markup(
            reply_markup=get_clinics_keyboard(clinics, page=page, items_per_page=ITEMS_PER_PAGE)
        )
        await callback.answer()
    except Exception as e:
        await callback.answer(f"Ошибка: {str(e)}", show_alert=True)
    finally:
        await api_client.close()


@router.callback_query(F.data.startswith("clinic_"))
async def show_clinic_card(callback: CallbackQuery, state: FSMContext):
    """Show clinic card"""
    clinic_id = int(callback.data.split("_")[1])
    
    api_client = APIClient()
    try:
        clinic = await api_client.get_clinic(clinic_id)
        
        if not clinic:
            await callback.answer("Клиника не найдена", show_alert=True)
            return
        
        # Add rating and reviews count
        clinic['rating'] = clinic.get('rating')
        clinic['reviews_count'] = clinic.get('reviews_count', 0)
        
        card_text = format_clinic_card(clinic)
        
        await state.update_data(current_clinic_id=clinic_id)
        
        await callback.message.edit_text(
            card_text,
            reply_markup=get_clinic_card_keyboard(clinic_id),
            parse_mode="HTML"
        )
        await callback.answer()
    except Exception as e:
        await callback.answer(f"Ошибка: {str(e)}", show_alert=True)
    finally:
        await api_client.close()


@router.callback_query(F.data.startswith("view_clinic_reviews_"))
async def view_clinic_reviews(callback: CallbackQuery):
    """View reviews for a clinic (through its doctors)"""
    clinic_id = int(callback.data.split("_")[3])
    
    api_client = APIClient()
    try:
        # Get all doctors of the clinic
        doctors = await api_client.get_all_doctors(clinic_id=clinic_id)
        
        if not doctors:
            await callback.message.edit_text(
                "<b>Отзывы о клинике</b>\n\n"
                "В этой клинике пока нет врачей.",
                reply_markup=get_back_to_menu_keyboard(),
                parse_mode="HTML"
            )
            await callback.answer()
            return
        
        # Get all reviews for doctors of this clinic
        all_reviews = []
        for doctor in doctors:
            reviews = await api_client.get_reviews_by_doctor(doctor['id'])
            all_reviews.extend(reviews)
        
        if not all_reviews:
            await callback.message.edit_text(
                "<b>Отзывы о клинике</b>\n\n"
                "Пока нет отзывов.",
                reply_markup=get_back_to_menu_keyboard(),
                parse_mode="HTML"
            )
            await callback.answer()
            return
        
        from bot.utils.formatters import format_reviews_list
        
        text = format_reviews_list(all_reviews, "Отзывы о клинике")
        
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


@router.callback_query(F.data == "back_to_clinics")
async def back_to_clinics(callback: CallbackQuery):
    """Go back to clinics list"""
    api_client = APIClient()
    try:
        clinics = await api_client.get_clinics_rating()
        
        text = "<b>Топ клиник по рейтингу</b>\n\n"
        for i, clinic in enumerate(clinics[:10], 1):
            name = clinic.get('title', 'Клиника')
            address = clinic.get('address', '')
            rating = clinic.get('rating', 0)
            reviews_count = clinic.get('reviews_count', 0)
            
            text += f"{i}. {name}"
            if address:
                text += f" ({address[:30]}...)" if len(address) > 30 else f" ({address})"
            text += f" Рейтинг: {rating:.1f} ({reviews_count} отзывов)\n"
        
        await callback.message.edit_text(
            text,
            reply_markup=get_clinics_keyboard(clinics, page=0, items_per_page=ITEMS_PER_PAGE),
            parse_mode="HTML"
        )
        await callback.answer()
    except Exception as e:
        await callback.answer(f"Ошибка: {str(e)}", show_alert=True)
    finally:
        await api_client.close()

