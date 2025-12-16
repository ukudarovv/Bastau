"""FSM states for user registration"""
from aiogram.fsm.state import State, StatesGroup


class RegistrationForm(StatesGroup):
    """Registration form states"""
    waiting_consent = State()  # Waiting for consent to process data
    full_name = State()  # Waiting for full name
    city = State()  # Waiting for city selection
    phone = State()  # Waiting for phone number (optional)
    confirm = State()  # Waiting for confirmation

