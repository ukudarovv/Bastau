"""Main menu handlers"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from bot.services.api_client import APIClient
from bot.keyboards.reply import get_main_menu
from bot.keyboards.inline import get_back_to_menu_keyboard

router = Router()


@router.message(F.text.in_(["В меню", "Главное меню", "Меню"]))
@router.callback_query(F.data == "main_menu")
async def show_main_menu(message_or_callback: Message | CallbackQuery, state: FSMContext):
    """Show main menu"""
    await state.clear()
    
    text = "<b>Главное меню</b>\n\nВыберите действие:"
    
    if isinstance(message_or_callback, CallbackQuery):
        await message_or_callback.message.edit_text(
            text,
            reply_markup=None,
            parse_mode="HTML"
        )
        await message_or_callback.message.answer(
            text,
            reply_markup=get_main_menu(),
            parse_mode="HTML"
        )
        await message_or_callback.answer()
    else:
        await message_or_callback.answer(
            text,
            reply_markup=get_main_menu(),
            parse_mode="HTML"
        )



