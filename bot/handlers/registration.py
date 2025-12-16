"""Registration handlers"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from bot.services.api_client import APIClient
from bot.keyboards.reply import (
    get_main_menu,
    get_phone_keyboard,
    get_confirm_keyboard
)
from bot.keyboards.inline import get_cities_keyboard, get_back_to_menu_keyboard
from bot.states.registration import RegistrationForm
from bot.utils.formatters import format_registration_summary
from bot.config import ITEMS_PER_PAGE

router = Router()


@router.message(RegistrationForm.waiting_consent, F.text == "Согласен")
async def process_consent(message: Message, state: FSMContext):
    """Process consent to data processing"""
    await message.answer(
        "Спасибо за согласие!\n\n"
        "Пожалуйста, введите ваше ФИО (полное имя):",
        reply_markup=None
    )
    await state.set_state(RegistrationForm.full_name)


@router.message(RegistrationForm.waiting_consent, F.text == "Отказ")
async def process_refusal(message: Message, state: FSMContext):
    """Process refusal to data processing"""
    await message.answer(
        "Для использования бота необходимо дать согласие на обработку персональных данных.\n\n"
        "Если передумаете, отправьте /start",
        reply_markup=None
    )
    await state.clear()


@router.message(RegistrationForm.full_name)
async def process_full_name(message: Message, state: FSMContext):
    """Process full name input"""
    full_name = message.text.strip()
    
    # Validate full name (minimum 3 characters, not just spaces)
    if len(full_name) < 3:
        await message.answer(
            "ФИО должно содержать минимум 3 символа. Пожалуйста, введите еще раз:"
        )
        return
    
    if not full_name.replace(" ", ""):
        await message.answer(
            "ФИО не может состоять только из пробелов. Пожалуйста, введите еще раз:"
        )
        return
    
    await state.update_data(full_name=full_name)
    
    # Get cities list
    api_client = APIClient()
    try:
        cities = await api_client.get_geo_positions()
        if cities:
            await message.answer(
                "Выберите ваш город:",
                reply_markup=get_cities_keyboard(cities, page=0, items_per_page=ITEMS_PER_PAGE)
            )
            await state.update_data(cities=cities)
            await state.set_state(RegistrationForm.city)
        else:
            await message.answer(
                "Введите название вашего города:",
                reply_markup=None
            )
            await state.set_state(RegistrationForm.city)
    except Exception as e:
        await message.answer(
            f"Ошибка при загрузке списка городов. Введите название города вручную:",
            reply_markup=None
        )
        await state.set_state(RegistrationForm.city)
    finally:
        await api_client.close()


@router.callback_query(RegistrationForm.city, F.data.startswith("city_"))
async def process_city_selection(callback: CallbackQuery, state: FSMContext):
    """Process city selection from inline keyboard"""
    city_id = int(callback.data.split("_")[1])
    
    api_client = APIClient()
    try:
        cities = (await state.get_data()).get('cities', [])
        city = next((c for c in cities if c.get('id') == city_id), None)
        
        if city:
            city_name = city.get('title', 'Город')
            await state.update_data(city_id=city_id, city_name=city_name)
            await callback.message.edit_text(
                f"Город выбран: {city_name}\n\n"
                "Теперь укажите ваш номер телефона (необязательно):",
                reply_markup=None
            )
            await callback.message.answer(
                "Вы можете отправить номер телефона или пропустить этот шаг:",
                reply_markup=get_phone_keyboard()
            )
            await state.set_state(RegistrationForm.phone)
        else:
            await callback.answer("Город не найден", show_alert=True)
    except Exception as e:
        await callback.answer(f"Ошибка: {str(e)}", show_alert=True)
    finally:
        await api_client.close()


@router.callback_query(RegistrationForm.city, F.data.startswith("cities_page_"))
async def process_cities_pagination(callback: CallbackQuery, state: FSMContext):
    """Process cities pagination"""
    page = int(callback.data.split("_")[2])
    data = await state.get_data()
    cities = data.get('cities', [])
    
    await callback.message.edit_reply_markup(
        reply_markup=get_cities_keyboard(cities, page=page, items_per_page=ITEMS_PER_PAGE)
    )
    await callback.answer()


@router.message(RegistrationForm.city)
async def process_city_text(message: Message, state: FSMContext):
    """Process city text input (fallback if no cities in list)"""
    city_name = message.text.strip()
    
    if len(city_name) < 2:
        await message.answer(
            "Название города слишком короткое. Введите еще раз:"
        )
        return
    
    await state.update_data(city_name=city_name, city_id=None)
    await message.answer(
        f"Город сохранен: {city_name}\n\n"
        "Теперь укажите ваш номер телефона (необязательно):",
        reply_markup=get_phone_keyboard()
    )
    await state.set_state(RegistrationForm.phone)


@router.message(RegistrationForm.phone, F.contact)
async def process_phone_contact(message: Message, state: FSMContext):
    """Process phone number from contact"""
    phone = message.contact.phone_number
    await state.update_data(phone=phone)
    await show_registration_summary(message, state)


@router.message(RegistrationForm.phone, F.text == "Пропустить")
async def process_phone_skip(message: Message, state: FSMContext):
    """Process phone skip"""
    await state.update_data(phone=None)
    await show_registration_summary(message, state)


@router.message(RegistrationForm.phone)
async def process_phone_text(message: Message, state: FSMContext):
    """Process phone number text input"""
    phone = message.text.strip()
    # Basic phone validation (just check it's not empty)
    if phone:
        await state.update_data(phone=phone)
        await show_registration_summary(message, state)
    else:
        await message.answer(
            "Пожалуйста, введите номер телефона или нажмите 'Пропустить':",
            reply_markup=get_phone_keyboard()
        )


async def show_registration_summary(message: Message, state: FSMContext):
    """Show registration summary for confirmation"""
    data = await state.get_data()
    summary = format_registration_summary(data)
    
    await message.answer(
        summary,
        reply_markup=get_confirm_keyboard(),
        parse_mode="HTML"
    )
    await state.set_state(RegistrationForm.confirm)


@router.message(RegistrationForm.confirm, F.text == "Подтвердить")
async def process_confirmation(message: Message, state: FSMContext):
    """Process registration confirmation"""
    data = await state.get_data()
    
    api_client = APIClient()
    try:
        # Create user via API
        user = await api_client.create_user(
            telegram_id=message.from_user.id,
            detail=data.get('full_name'),
            geo_position_id=data.get('city_id'),
            phone_number=data.get('phone')
        )
        
        await message.answer(
            "Регистрация успешно завершена!\n\n"
            "Теперь вы можете пользоваться всеми функциями бота.",
            reply_markup=get_main_menu()
        )
        await state.clear()
    except Exception as e:
        await message.answer(
            f"Ошибка при регистрации: {str(e)}\n\n"
            "Попробуйте позже или обратитесь в поддержку.",
            reply_markup=None
        )
    finally:
        await api_client.close()


@router.message(RegistrationForm.confirm, F.text == "Изменить")
async def process_edit(message: Message, state: FSMContext):
    """Process edit request - restart registration"""
    await message.answer(
        "Пожалуйста, введите ваше ФИО (полное имя):",
        reply_markup=None
    )
    await state.set_state(RegistrationForm.full_name)

