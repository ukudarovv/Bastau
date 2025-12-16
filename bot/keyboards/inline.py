"""Inline keyboards for Telegram bot"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List, Dict, Optional


def get_rating_keyboard() -> InlineKeyboardMarkup:
    """Get rating selection keyboard (1-5 stars)"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="1", callback_data="rating_1"),
                InlineKeyboardButton(text="2", callback_data="rating_2"),
                InlineKeyboardButton(text="3", callback_data="rating_3"),
            ],
            [
                InlineKeyboardButton(text="4", callback_data="rating_4"),
                InlineKeyboardButton(text="5", callback_data="rating_5"),
            ],
            [InlineKeyboardButton(text="Отмена", callback_data="cancel_review")]
        ]
    )
    return keyboard


def get_categories_keyboard(
    categories: List[Dict],
    page: int = 0,
    items_per_page: int = 10
) -> InlineKeyboardMarkup:
    """Get categories list keyboard with pagination"""
    start_idx = page * items_per_page
    end_idx = start_idx + items_per_page
    page_categories = categories[start_idx:end_idx]
    
    keyboard_buttons = []
    for category in page_categories:
        keyboard_buttons.append([
            InlineKeyboardButton(
                text=category.get('title', 'Категория'),
                callback_data=f"category_{category.get('id')}"
            )
        ])
    
    # Pagination buttons
    nav_buttons = []
    if page > 0:
        nav_buttons.append(
            InlineKeyboardButton(text="Назад", callback_data=f"categories_page_{page - 1}")
        )
    if end_idx < len(categories):
        nav_buttons.append(
            InlineKeyboardButton(text="Далее", callback_data=f"categories_page_{page + 1}")
        )
    
    if nav_buttons:
        keyboard_buttons.append(nav_buttons)
    
    keyboard_buttons.append([
        InlineKeyboardButton(text="В меню", callback_data="main_menu")
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)


def get_doctors_keyboard(
    doctors: List[Dict],
    page: int = 0,
    items_per_page: int = 10,
    category_id: Optional[int] = None
) -> InlineKeyboardMarkup:
    """Get doctors list keyboard with pagination"""
    start_idx = page * items_per_page
    end_idx = start_idx + items_per_page
    page_doctors = doctors[start_idx:end_idx]
    
    keyboard_buttons = []
    for doctor in page_doctors:
        doctor_name = doctor.get('detail', 'Врач')
        clinic_name = doctor.get('clinic', {}).get('title', '') if doctor.get('clinic') else ''
        rating = doctor.get('rating')
        
        text = doctor_name
        if clinic_name:
            text += f" ({clinic_name})"
        if rating:
            text += f" Рейтинг: {rating:.1f}"
        
        keyboard_buttons.append([
            InlineKeyboardButton(
                text=text,
                callback_data=f"doctor_{doctor.get('id')}"
            )
        ])
    
    # Pagination buttons
    nav_buttons = []
    if page > 0:
        callback_data = f"doctors_page_{page - 1}"
        if category_id:
            callback_data += f"_cat_{category_id}"
        nav_buttons.append(
            InlineKeyboardButton(text="Назад", callback_data=callback_data)
        )
    if end_idx < len(doctors):
        callback_data = f"doctors_page_{page + 1}"
        if category_id:
            callback_data += f"_cat_{category_id}"
        nav_buttons.append(
            InlineKeyboardButton(text="Далее", callback_data=callback_data)
        )
    
    if nav_buttons:
        keyboard_buttons.append(nav_buttons)
    
    keyboard_buttons.append([
        InlineKeyboardButton(text="Назад к категориям", callback_data="back_to_categories"),
        InlineKeyboardButton(text="В меню", callback_data="main_menu")
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)


def get_clinics_keyboard(
    clinics: List[Dict],
    page: int = 0,
    items_per_page: int = 10
) -> InlineKeyboardMarkup:
    """Get clinics list keyboard with pagination"""
    start_idx = page * items_per_page
    end_idx = start_idx + items_per_page
    page_clinics = clinics[start_idx:end_idx]
    
    keyboard_buttons = []
    for clinic in page_clinics:
        clinic_name = clinic.get('title', 'Клиника')
        rating = clinic.get('rating')
        
        text = clinic_name
        if rating:
            text += f" Рейтинг: {rating:.1f}"
        
        keyboard_buttons.append([
            InlineKeyboardButton(
                text=text,
                callback_data=f"clinic_{clinic.get('id')}"
            )
        ])
    
    # Pagination buttons
    nav_buttons = []
    if page > 0:
        nav_buttons.append(
            InlineKeyboardButton(text="Назад", callback_data=f"clinics_page_{page - 1}")
        )
    if end_idx < len(clinics):
        nav_buttons.append(
            InlineKeyboardButton(text="Далее", callback_data=f"clinics_page_{page + 1}")
        )
    
    if nav_buttons:
        keyboard_buttons.append(nav_buttons)
    
    keyboard_buttons.append([
        InlineKeyboardButton(text="В меню", callback_data="main_menu")
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)


def get_doctor_card_keyboard(doctor_id: int) -> InlineKeyboardMarkup:
    """Get doctor card action keyboard"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Оставить отзыв", callback_data=f"review_doctor_{doctor_id}"),
                InlineKeyboardButton(text="Смотреть отзывы", callback_data=f"view_reviews_{doctor_id}")
            ],
            [InlineKeyboardButton(text="Назад", callback_data="back_to_doctors")]
        ]
    )
    return keyboard


def get_clinic_card_keyboard(clinic_id: int) -> InlineKeyboardMarkup:
    """Get clinic card action keyboard"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Отзывы о клинике", callback_data=f"view_clinic_reviews_{clinic_id}")
            ],
            [InlineKeyboardButton(text="Назад", callback_data="back_to_clinics")]
        ]
    )
    return keyboard


def get_cities_keyboard(
    cities: List[Dict],
    page: int = 0,
    items_per_page: int = 10
) -> InlineKeyboardMarkup:
    """Get cities list keyboard for registration"""
    start_idx = page * items_per_page
    end_idx = start_idx + items_per_page
    page_cities = cities[start_idx:end_idx]
    
    keyboard_buttons = []
    for city in page_cities:
        keyboard_buttons.append([
            InlineKeyboardButton(
                text=city.get('title', 'Город'),
                callback_data=f"city_{city.get('id')}"
            )
        ])
    
    # Pagination buttons
    nav_buttons = []
    if page > 0:
        nav_buttons.append(
            InlineKeyboardButton(text="Назад", callback_data=f"cities_page_{page - 1}")
        )
    if end_idx < len(cities):
        nav_buttons.append(
            InlineKeyboardButton(text="Далее", callback_data=f"cities_page_{page + 1}")
        )
    
    if nav_buttons:
        keyboard_buttons.append(nav_buttons)
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)


def get_back_to_menu_keyboard() -> InlineKeyboardMarkup:
    """Get simple back to menu keyboard"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="В меню", callback_data="main_menu")]
        ]
    )
    return keyboard


def get_cancel_keyboard() -> InlineKeyboardMarkup:
    """Get cancel action keyboard"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Отмена", callback_data="cancel")]
        ]
    )
    return keyboard

