"""
WebSocket URL routing for the critique app.

This module defines URL patterns for WebSocket connections,
particularly for real-time notifications.
"""

from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # WebSocket endpoint for real-time notifications
    re_path(r'ws/notifications/$', consumers.NotificationConsumer.as_asgi()),
    
    # Optional: User-specific notification channel
    re_path(r'ws/notifications/(?P<user_id>\d+)/$', consumers.NotificationConsumer.as_asgi()),
]