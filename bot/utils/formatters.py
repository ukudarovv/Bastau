"""Message formatters for Telegram bot"""
from typing import Dict, Optional


def format_doctor_card(doctor: Dict) -> str:
    """Format doctor card message"""
    full_name = doctor.get('detail', 'Не указано')
    category = doctor.get('category', {}).get('title', 'Не указано') if doctor.get('category') else 'Не указано'
    clinic = doctor.get('clinic')
    clinic_name = clinic.get('title', 'Не указано') if clinic else 'Не указано'
    clinic_address = clinic.get('address', '') if clinic else ''
    clinic_phone = clinic.get('phone', '') if clinic else ''
    clinic_email = clinic.get('email', '') if clinic else ''
    clinic_work_time = clinic.get('work_time', '') if clinic else ''
    
    rating = doctor.get('rating')
    reviews_count = doctor.get('reviews_count', 0)
    
    text = f"<b>{full_name}</b>\n\n"
    text += f"<b>Специализация:</b> {category}\n"
    
    if rating:
        text += f"<b>Рейтинг:</b> {rating:.1f} ({reviews_count} отзывов)\n"
    else:
        text += f"<b>Рейтинг:</b> Нет отзывов\n"
    
    text += f"\n<b>Клиника:</b> {clinic_name}\n"
    if clinic_address:
        text += f"<b>Адрес:</b> {clinic_address}\n"
    if clinic_phone:
        text += f"<b>Телефон:</b> {clinic_phone}\n"
    if clinic_email:
        text += f"<b>Email:</b> {clinic_email}\n"
    if clinic_work_time:
        text += f"<b>Время работы:</b> {clinic_work_time}\n"
    
    return text


def format_clinic_card(clinic: Dict) -> str:
    """Format clinic card message"""
    title = clinic.get('title', 'Не указано')
    address = clinic.get('address', 'Не указано')
    phone = clinic.get('phone', 'Не указано')
    email = clinic.get('email', '')
    work_time = clinic.get('work_time', '')
    
    rating = clinic.get('rating')
    reviews_count = clinic.get('reviews_count', 0)
    
    text = f"<b>{title}</b>\n\n"
    text += f"<b>Адрес:</b> {address}\n"
    text += f"<b>Телефон:</b> {phone}\n"
    
    if email:
        text += f"<b>Email:</b> {email}\n"
    if work_time:
        text += f"<b>Время работы:</b> {work_time}\n"
    
    if rating:
        text += f"\n<b>Рейтинг:</b> {rating:.1f} ({reviews_count} отзывов)\n"
    else:
        text += f"\n<b>Рейтинг:</b> Нет отзывов\n"
    
    return text


def format_review(review: Dict, include_doctor: bool = False) -> str:
    """Format review message"""
    rating = review.get('rating', 0)
    text_review = review.get('detail', '')
    created_at = review.get('created_at', '')
    
    formatted = f"<b>Оценка: {rating}/5</b>\n\n"
    formatted += f"{text_review}\n"
    
    if created_at:
        # Format date if needed
        formatted += f"\n{created_at}"
    
    if include_doctor:
        doctor = review.get('doctor', {})
        if doctor:
            doctor_name = doctor.get('detail', 'Врач')
            formatted += f"\nВрач: {doctor_name}"
    
    return formatted


def format_reviews_list(reviews: list, title: str = "Отзывы") -> str:
    """Format list of reviews"""
    if not reviews:
        return f"<b>{title}</b>\n\nПока нет отзывов."
    
    text = f"<b>{title}</b>\n\n"
    for i, review in enumerate(reviews, 1):
        rating = review.get('rating', 0)
        text_review = review.get('detail', '')
        # Truncate long reviews
        if len(text_review) > 100:
            text_review = text_review[:100] + "..."
        
        text += f"{i}. Оценка: {rating}/5\n"
        text += f"   {text_review}\n\n"
    
    return text


def format_user_review(review: Dict) -> str:
    """Format user's own review"""
    doctor = review.get('doctor', {})
    doctor_name = doctor.get('detail', 'Врач') if doctor else 'Врач'
    rating = review.get('rating', 0)
    text_review = review.get('detail', '')
    created_at = review.get('created_at', '')
    
    formatted = f"<b>Врач:</b> {doctor_name}\n"
    formatted += f"<b>Оценка: {rating}/5</b>\n\n"
    formatted += f"{text_review}\n"
    
    if created_at:
        formatted += f"\n{created_at}"
    
    return formatted


def format_registration_summary(data: Dict) -> str:
    """Format registration data summary"""
    text = "<b>Проверьте введенные данные:</b>\n\n"
    text += f"<b>ФИО:</b> {data.get('full_name', 'Не указано')}\n"
    text += f"<b>Город:</b> {data.get('city_name', 'Не указано')}\n"
    
    phone = data.get('phone')
    if phone:
        text += f"<b>Телефон:</b> {phone}\n"
    else:
        text += f"<b>Телефон:</b> Не указан\n"
    
    return text


def format_support_ticket_summary(ticket: Dict) -> str:
    """Format support ticket summary"""
    ticket_id = ticket.get('id', 'N/A')
    detail = ticket.get('detail', '')
    created_at = ticket.get('created_at', '')
    
    text = f"<b>Ваше обращение принято!</b>\n\n"
    text += f"<b>Номер обращения:</b> #{ticket_id}\n"
    text += f"<b>Сообщение:</b> {detail}\n"
    
    if created_at:
        text += f"\n{created_at}\n"
    
    text += "\nМы свяжемся с вами в ближайшее время."
    
    return text

