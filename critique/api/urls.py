from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet, ProfileViewSet, ArtWorkViewSet, 
    CritiqueViewSet, health_check,
    ReactionViewSet, NotificationViewSet, FolderViewSet,
    ArtworkVersionViewSet, ArtworkVersionCompareView, ArtworkVersionRestoreView
)

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'profiles', ProfileViewSet, basename='profile')
router.register(r'artworks', ArtWorkViewSet, basename='artwork')
router.register(r'critiques', CritiqueViewSet, basename='critique')
router.register(r'reactions', ReactionViewSet, basename='reaction')
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'folders', FolderViewSet, basename='folder')

# The API URLs are determined automatically by the router
urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('critique.api.auth_urls')),  # Authentication endpoints
    path('health/', health_check, name='api-health-check'),
    
    # Artwork versioning endpoints
    path('artworks/<int:artwork_id>/versions/', ArtworkVersionViewSet.as_view(), name='artwork-versions'),
    path('artworks/<int:artwork_id>/versions/compare/', ArtworkVersionCompareView.as_view(), name='artwork-versions-compare'),
    path('artworks/<int:artwork_id>/versions/<int:version_id>/restore/', ArtworkVersionRestoreView.as_view(), name='artwork-version-restore'),
]