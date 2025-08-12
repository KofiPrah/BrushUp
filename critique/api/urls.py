from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet, ProfileViewSet, ArtWorkViewSet, 
    CritiqueViewSet, health_check,
    ReactionViewSet, NotificationViewSet, FolderViewSet,
    create_artwork_version, get_artwork_version, 
    delete_artwork_version, archive_artwork_version, unarchive_artwork_version, switch_artwork_version, ArtworkVersionViewSet,
    ArtworkVersionCompareView, ArtworkVersionRestoreView, ArtworkVersionReorderView,
    hide_critique, unhide_critique, delete_critique_reply,
    AchievementBadgeViewSet, UserAchievementViewSet, user_badge_overview, trigger_badge_check, badge_leaderboard
)
from .move_artwork import move_artwork_to_folder
from .feed_views import feed_next_pair, QuickCritViewSet, TagViewSet

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'profiles', ProfileViewSet, basename='profile')
router.register(r'artworks', ArtWorkViewSet, basename='artwork')
router.register(r'critiques', CritiqueViewSet, basename='critique')
router.register(r'reactions', ReactionViewSet, basename='reaction')
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'folders', FolderViewSet, basename='folder')
router.register(r'versions', ArtworkVersionViewSet, basename='version')
router.register(r'badges', AchievementBadgeViewSet, basename='badge')
router.register(r'achievements', UserAchievementViewSet, basename='achievement')
router.register(r'quick-crits', QuickCritViewSet, basename='quick-crit')
router.register(r'tags', TagViewSet, basename='tag')

# The API URLs are determined automatically by the router
urlpatterns = [
    # Custom endpoints that need to be before the router
    path('artworks/move-to-folder/', move_artwork_to_folder, name='artwork-move-to-folder'),
    
    # Two-at-a-time critique feed endpoints
    path('feed/next/', feed_next_pair, name='feed-next'),
    
    # Achievement system endpoints - must be before router to prevent conflicts
    path('badges/overview/', user_badge_overview, name='user-badge-overview'),
    path('badges/overview/<int:user_id>/', user_badge_overview, name='user-badge-overview-by-id'),
    path('badges/trigger-check/', trigger_badge_check, name='trigger-badge-check'),
    path('badges/leaderboard/', badge_leaderboard, name='badge-leaderboard'),
    
    path('', include(router.urls)),
    path('auth/', include('critique.api.auth_urls')),  # Authentication endpoints
    path('health/', health_check, name='api-health-check'),
    
    # Artwork versioning endpoints
    path('artworks/<int:artwork_id>/versions/', create_artwork_version, name='artwork-versions'),
    path('artworks/<int:artwork_id>/versions/<int:version_id>/', get_artwork_version, name='artwork-version-detail'),
    path('artworks/<int:artwork_id>/switch-version/<int:version_id>/', switch_artwork_version, name='artwork-switch-version'),
    path('artworks/<int:artwork_id>/versions/compare/', ArtworkVersionCompareView.as_view(), name='artwork-versions-compare'),
    path('artworks/<int:artwork_id>/versions/<int:version_id>/restore/', ArtworkVersionRestoreView.as_view(), name='artwork-version-restore'),
    path('artworks/<int:artwork_id>/versions/reorder/', ArtworkVersionReorderView.as_view(), name='artwork-version-reorder'),
    path('artworks/versions/<int:version_id>/delete/', delete_artwork_version, name='artwork-version-delete'),
    path('versions/<int:version_id>/archive/', archive_artwork_version, name='version-archive'),
    path('versions/<int:version_id>/unarchive/', unarchive_artwork_version, name='version-unarchive'),
    path('critiques/<int:critique_id>/hide/', hide_critique, name='critique-hide'),
    path('critiques/<int:critique_id>/unhide/', unhide_critique, name='critique-unhide'),
    path('replies/<int:reply_id>/', delete_critique_reply, name='critique-reply-delete'),
]