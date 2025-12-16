from django.contrib import admin
from .models import Category, GeoPosition, Clinic, User, SupportRequest, Review


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'title')
    search_fields = ('title',)


@admin.register(GeoPosition)
class GeoPositionAdmin(admin.ModelAdmin):
    list_display = ('id', 'title')
    search_fields = ('title',)


@admin.register(Clinic)
class ClinicAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'phone', 'email')
    search_fields = ('title', 'phone', 'email', 'address')
    list_filter = ('title',)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'telegram_id', 'category', 'patient', 'doctor', 'clinic', 'created_at')
    list_filter = ('patient', 'doctor', 'category', 'clinic', 'geo_position')
    search_fields = ('telegram_id', 'phone_number', 'user__username', 'user__email')
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('user',)


@admin.register(SupportRequest)
class SupportRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__telegram_id', 'detail')
    readonly_fields = ('created_at',)
    raw_id_fields = ('user',)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'doctor', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__telegram_id', 'doctor__telegram_id', 'detail')
    readonly_fields = ('created_at',)
    raw_id_fields = ('user', 'doctor')
