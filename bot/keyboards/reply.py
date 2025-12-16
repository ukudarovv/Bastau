"""Reply keyboards for Telegram bot"""
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_main_menu() -> ReplyKeyboardMarkup:
    """Get main menu keyboard"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Категории")],
            [KeyboardButton(text="Рейтинг врачей")],
            [KeyboardButton(text="Рейтинг клиник")],
            [KeyboardButton(text="Мои отзывы")],
            [KeyboardButton(text="Тех поддержка")]
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите действие из меню"
    )
    return keyboard


def get_consent_keyboard() -> ReplyKeyboardMarkup:
    """Get consent keyboard for registration"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Согласен")],
            [KeyboardButton(text="Отказ")]
        ],
        resize_keyboard=True
    )
    return keyboard


def get_phone_keyboard() -> ReplyKeyboardMarkup:
    """Get phone number keyboard"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Отправить номер", request_contact=True)],
            [KeyboardButton(text="Пропустить")]
        ],
        resize_keyboard=True
    )
    return keyboard


def get_confirm_keyboard() -> ReplyKeyboardMarkup:
    """Get confirmation keyboard"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Подтвердить")],
            [KeyboardButton(text="Изменить")]
        ],
        resize_keyboard=True
    )
    return keyboard

