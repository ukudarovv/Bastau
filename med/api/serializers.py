from rest_framework import serializers
from .models import Category, GeoPosition, Clinic, User, SupportRequest, Review


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для Category"""
    
    class Meta:
        model = Category
        fields = ['id', 'title']


class GeoPositionSerializer(serializers.ModelSerializer):
    """Сериализатор для GeoPosition"""
    
    class Meta:
        model = GeoPosition
        fields = ['id', 'title']


class ClinicSerializer(serializers.ModelSerializer):
    """Сериализатор для Clinic"""
    rating = serializers.SerializerMethodField()
    reviews_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Clinic
        fields = ['id', 'title', 'address', 'phone', 'email', 'work_time', 'rating', 'reviews_count']
    
    def get_rating(self, obj):
        return obj.get_rating()
    
    def get_reviews_count(self, obj):
        return obj.get_reviews_count()


class UserListSerializer(serializers.ModelSerializer):
    """Упрощенный сериализатор для списка пользователей"""
    category = CategorySerializer(read_only=True)
    clinic = ClinicSerializer(read_only=True)
    geo_position = GeoPositionSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'telegram_id', 'category', 'clinic', 'geo_position', 'phone_number', 
                  'patient', 'doctor', 'created_at']


class UserDetailSerializer(serializers.ModelSerializer):
    """Детальный сериализатор для User"""
    category = CategorySerializer(read_only=True)
    clinic = ClinicSerializer(read_only=True)
    geo_position = GeoPositionSerializer(read_only=True)
    rating = serializers.SerializerMethodField()
    reviews_count = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'telegram_id', 'category', 'clinic', 'geo_position', 'phone_number',
                  'detail', 'patient', 'doctor', 'rating', 'reviews_count', 'created_at', 'updated_at']
    
    def get_rating(self, obj):
        return obj.get_rating()
    
    def get_reviews_count(self, obj):
        return obj.get_reviews_count()


class UserCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания User"""
    
    class Meta:
        model = User
        fields = ['telegram_id', 'category', 'phone_number', 'detail', 'geo_position', 
                  'clinic', 'patient', 'doctor']
    
    def validate_telegram_id(self, value):
        """Проверка уникальности telegram_id"""
        if User.objects.filter(telegram_id=value).exists():
            raise serializers.ValidationError("Пользователь с таким telegram_id уже существует")
        return value


class SupportRequestSerializer(serializers.ModelSerializer):
    """Сериализатор для SupportRequest"""
    user = UserListSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = SupportRequest
        fields = ['id', 'user', 'user_id', 'detail', 'created_at']
        read_only_fields = ['created_at']


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для Review"""
    user = UserListSerializer(read_only=True)
    doctor = UserListSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True)
    doctor_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Review
        fields = ['id', 'user', 'user_id', 'doctor', 'doctor_id', 'rating', 'detail', 'created_at']
        read_only_fields = ['created_at']
    
    def validate_rating(self, value):
        """Валидация рейтинга"""
        if not (1 <= value <= 5):
            raise serializers.ValidationError("Рейтинг должен быть от 1 до 5")
        return value

