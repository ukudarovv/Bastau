from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CategoryViewSet,
    GeoPositionViewSet,
    ClinicViewSet,
    UserViewSet,
    SupportRequestViewSet,
    ReviewViewSet
)

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'geopositions', GeoPositionViewSet, basename='geoposition')
router.register(r'clinics', ClinicViewSet, basename='clinic')
router.register(r'users', UserViewSet, basename='user')
router.register(r'support-requests', SupportRequestViewSet, basename='support-request')
router.register(r'reviews', ReviewViewSet, basename='review')

urlpatterns = [
    path('', include(router.urls)),
]

