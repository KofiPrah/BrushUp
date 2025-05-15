from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet, ProfileViewSet, ArtWorkViewSet, 
    ReviewViewSet, health_check
)

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'profiles', ProfileViewSet)
router.register(r'artworks', ArtWorkViewSet)
router.register(r'reviews', ReviewViewSet)

# The API URLs are determined automatically by the router
urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('critique.api.auth_urls')),  # Authentication endpoints
    path('health/', health_check, name='api-health-check'),
]