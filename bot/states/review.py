"""FSM states for review creation"""
from aiogram.fsm.state import State, StatesGroup


class ReviewForm(StatesGroup):
    """Review form states"""
    rating = State()  # Waiting for rating selection (1-5)
    text = State()  # Waiting for review text
    # media = State()  # Optional: waiting for media (not implemented yet)

