from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Avg, Count
from django.shortcuts import get_object_or_404

from .models import Category, GeoPosition, Clinic, User, SupportRequest, Review
from .serializers import (
    CategorySerializer,
    GeoPositionSerializer,
    ClinicSerializer,
    UserListSerializer,
    UserDetailSerializer,
    UserCreateSerializer,
    SupportRequestSerializer,
    ReviewSerializer
)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для Category (только GET)"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['title']
    ordering_fields = ['title']


class GeoPositionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для GeoPosition (только GET)"""
    queryset = GeoPosition.objects.all()
    serializer_class = GeoPositionSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['title']
    ordering_fields = ['title']


class ClinicViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для Clinic (только GET)"""
    queryset = Clinic.objects.all()
    serializer_class = ClinicSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['title', 'address', 'phone', 'email']
    ordering_fields = ['title', 'id']

    @action(detail=False, methods=['get'])
    def rating(self, request):
        """Топ клиник по рейтингу"""
        clinics = Clinic.objects.all()
        # Добавляем рейтинг и количество отзывов
        clinic_data = []
        for clinic in clinics:
            rating = clinic.get_rating()
            reviews_count = clinic.get_reviews_count()
            if rating is not None:  # Показываем только клиники с отзывами
                clinic_data.append({
                    'clinic': clinic,
                    'rating': rating,
                    'reviews_count': reviews_count
                })
        
        # Сортируем по рейтингу (desc), затем по количеству отзывов (desc)
        clinic_data.sort(key=lambda x: (x['rating'], x['reviews_count']), reverse=True)
        
        # Сериализуем
        serializer = self.get_serializer([item['clinic'] for item in clinic_data], many=True)
        return Response(serializer.data)


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet для User (GET, POST)"""
    queryset = User.objects.all()
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['telegram_id', 'phone_number', 'detail']
    ordering_fields = ['created_at', 'telegram_id']

    def get_serializer_class(self):
        if self.action == 'list':
            return UserListSerializer
        elif self.action == 'create':
            return UserCreateSerializer
        return UserDetailSerializer

    @action(detail=False, methods=['get'], url_path='telegram/(?P<telegram_id>[^/.]+)')
    def by_telegram_id(self, request, telegram_id=None):
        """Получение пользователя по telegram_id"""
        try:
            user = User.objects.get(telegram_id=telegram_id)
            serializer = UserDetailSerializer(user)
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response(
                {'detail': 'Пользователь не найден'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['get'])
    def doctors(self, request):
        """Список врачей (doctor=True)"""
        doctors = User.objects.filter(doctor=True)
        
        # Фильтрация по категории
        category_id = request.query_params.get('category', None)
        if category_id:
            doctors = doctors.filter(category_id=category_id)
        
        # Фильтрация по геопозиции
        geo_position_id = request.query_params.get('geo_position', None)
        if geo_position_id:
            doctors = doctors.filter(geo_position_id=geo_position_id)
        
        # Фильтрация по клинике
        clinic_id = request.query_params.get('clinic', None)
        if clinic_id:
            doctors = doctors.filter(clinic_id=clinic_id)
        
        # Поиск
        search = request.query_params.get('search', None)
        if search:
            doctors = doctors.filter(detail__icontains=search)
        
        serializer = UserListSerializer(doctors, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='doctors/rating')
    def doctors_rating(self, request):
        """Топ врачей по рейтингу"""
        doctors = User.objects.filter(doctor=True)
        
        # Добавляем рейтинг и количество отзывов
        doctor_data = []
        for doctor in doctors:
            rating = doctor.get_rating()
            reviews_count = doctor.get_reviews_count()
            if rating is not None:  # Показываем только врачей с отзывами
                doctor_data.append({
                    'doctor': doctor,
                    'rating': rating,
                    'reviews_count': reviews_count
                })
        
        # Сортируем по рейтингу (desc), затем по количеству отзывов (desc)
        doctor_data.sort(key=lambda x: (x['rating'], x['reviews_count']), reverse=True)
        
        # Сериализуем
        serializer = UserListSerializer([item['doctor'] for item in doctor_data], many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='doctors/category/(?P<category_id>[^/.]+)')
    def doctors_by_category(self, request, category_id=None):
        """Врачи по категории"""
        doctors = User.objects.filter(doctor=True, category_id=category_id)
        serializer = UserListSerializer(doctors, many=True)
        return Response(serializer.data)


class SupportRequestViewSet(viewsets.ModelViewSet):
    """ViewSet для SupportRequest (GET, POST)"""
    queryset = SupportRequest.objects.all()
    serializer_class = SupportRequestSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['detail']
    ordering_fields = ['created_at']

    def get_queryset(self):
        queryset = SupportRequest.objects.all()
        # Фильтрация по пользователю
        user_id = self.request.query_params.get('user', None)
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        return queryset

    def perform_create(self, serializer):
        # Получаем user_id из запроса
        user_id = serializer.validated_data.get('user_id')
        user = get_object_or_404(User, id=user_id)
        serializer.save(user=user)


class ReviewViewSet(viewsets.ModelViewSet):
    """ViewSet для Review (GET, POST)"""
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['detail']
    ordering_fields = ['created_at', 'rating']

    def get_queryset(self):
        queryset = Review.objects.all()
        # Фильтрация по врачу
        doctor_id = self.request.query_params.get('doctor', None)
        if doctor_id:
            queryset = queryset.filter(doctor_id=doctor_id)
        # Фильтрация по пользователю (автору отзыва)
        user_id = self.request.query_params.get('user', None)
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        return queryset

    def perform_create(self, serializer):
        # Получаем user_id и doctor_id из запроса
        user_id = serializer.validated_data.get('user_id')
        doctor_id = serializer.validated_data.get('doctor_id')
        user = get_object_or_404(User, id=user_id)
        doctor = get_object_or_404(User, id=doctor_id)
        serializer.save(user=user, doctor=doctor)

    @action(detail=False, methods=['get'], url_path='doctor/(?P<doctor_id>[^/.]+)')
    def by_doctor(self, request, doctor_id=None):
        """Отзывы к конкретному врачу"""
        reviews = Review.objects.filter(doctor_id=doctor_id)
        serializer = self.get_serializer(reviews, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='user/(?P<user_id>[^/.]+)')
    def by_user(self, request, user_id=None):
        """Отзывы конкретного пользователя"""
        reviews = Review.objects.filter(user_id=user_id)
        serializer = self.get_serializer(reviews, many=True)
        return Response(serializer.data)
