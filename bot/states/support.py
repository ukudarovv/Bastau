"""FSM states for support requests"""
from aiogram.fsm.state import State, StatesGroup


class SupportForm(StatesGroup):
    """Support form states"""
    subject = State()  # Waiting for subject/topic
    message = State()  # Waiting for message text
    # media = State()  # Optional: waiting for media (not implemented yet)

