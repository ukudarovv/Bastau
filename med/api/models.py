from django.db import models
from django.contrib.auth.models import User as AuthUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Avg, Count


class Category(models.Model):
    """Категории пользователей"""
    title = models.CharField(max_length=255, verbose_name="Название")

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ['title']

    def __str__(self):
        return self.title


class GeoPosition(models.Model):
    """Географические позиции"""
    title = models.CharField(max_length=255, verbose_name="Название")

    class Meta:
        verbose_name = "Геопозиция"
        verbose_name_plural = "Геопозиции"
        ordering = ['title']

    def __str__(self):
        return self.title


class Clinic(models.Model):
    """Клиники"""
    title = models.CharField(max_length=255, verbose_name="Название")
    address = models.TextField(verbose_name="Адрес")
    phone = models.CharField(max_length=100, verbose_name="Телефон")
    email = models.EmailField(verbose_name="Email")
    work_time = models.TextField(verbose_name="Время работы")

    class Meta:
        verbose_name = "Клиника"
        verbose_name_plural = "Клиники"
        ordering = ['title']

    def get_rating(self):
        """Получить средний рейтинг клиники (на основе отзывов к врачам этой клиники)"""
        doctors = self.users.filter(doctor=True)
        if not doctors.exists():
            return None
        
        all_reviews = Review.objects.filter(doctor__in=doctors)
        avg_rating = all_reviews.aggregate(Avg('rating'))['rating__avg']
        return round(avg_rating, 2) if avg_rating else None

    def get_reviews_count(self):
        """Получить количество отзывов о клинике (сумма отзывов к врачам клиники)"""
        doctors = self.users.filter(doctor=True)
        if not doctors.exists():
            return 0
        return Review.objects.filter(doctor__in=doctors).count()

    def __str__(self):
        return self.title


class User(models.Model):
    """Пользователи системы"""
    user = models.OneToOneField(
        AuthUser,
        on_delete=models.CASCADE,
        related_name='profile',
        null=True,
        blank=True,
        verbose_name="Пользователь Django"
    )
    telegram_id = models.IntegerField(unique=True, db_index=True, verbose_name="Telegram ID")
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users',
        verbose_name="Категория"
    )
    phone_number = models.TextField(null=True, blank=True, verbose_name="Номер телефона")
    detail = models.TextField(null=True, blank=True, verbose_name="Детали")
    geo_position = models.ForeignKey(
        GeoPosition,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users',
        verbose_name="Геопозиция"
    )
    clinic = models.ForeignKey(
        Clinic,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users',
        verbose_name="Клиника"
    )
    patient = models.BooleanField(default=False, verbose_name="Пациент")
    doctor = models.BooleanField(default=False, verbose_name="Врач")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['telegram_id']),
        ]

    def get_rating(self):
        """Получить средний рейтинг врача"""
        if not self.doctor:
            return None
        avg_rating = self.reviews_received.aggregate(Avg('rating'))['rating__avg']
        return round(avg_rating, 2) if avg_rating else None

    def get_reviews_count(self):
        """Получить количество отзывов о враче"""
        if not self.doctor:
            return 0
        return self.reviews_received.count()

    def __str__(self):
        return f"{self.user.username if self.user else 'N/A'} (Telegram: {self.telegram_id})"


class SupportRequest(models.Model):
    """Запросы в поддержку"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='support_requests',
        verbose_name="Пользователь"
    )
    detail = models.TextField(verbose_name="Детали запроса")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Запрос в поддержку"
        verbose_name_plural = "Запросы в поддержку"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user']),
        ]

    def __str__(self):
        return f"Запрос от {self.user.telegram_id}"


class Review(models.Model):
    """Отзывы"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews_written',
        verbose_name="Автор отзыва"
    )
    doctor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews_received',
        verbose_name="Врач"
    )
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="Оценка",
        help_text="Оценка от 1 до 5",
        default=3
    )
    detail = models.TextField(verbose_name="Текст отзыва")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['doctor']),
        ]

    def __str__(self):
        return f"Отзыв от {self.user.telegram_id} для врача {self.doctor.telegram_id}"
