"""
WebSocket consumers for real-time functionality.

This module contains WebSocket consumers that handle real-time
communication for notifications and other live features.
"""

import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import Notification

logger = logging.getLogger(__name__)

class NotificationConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time notifications.
    
    When a user connects, they join a group specific to their user ID.
    When notifications are created, they are sent to the appropriate user group.
    """

    async def connect(self):
        """Accept WebSocket connection and add user to their notification group."""
        # Get user from Django session
        self.user = self.scope["user"]
        
        if self.user.is_anonymous:
            # Reject connection for anonymous users
            await self.close()
            return

        # Create unique group name for this user
        self.user_group_name = f'user_notifications_{self.user.id}'

        # Join user notification group
        await self.channel_layer.group_add(
            self.user_group_name,
            self.channel_name
        )

        await self.accept()
        
        # Send connection confirmation
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': f'Connected to notifications for user {self.user.username}',
            'user_id': self.user.id
        }))
        
        # Send initial unread notification count
        unread_count = await self.get_unread_notification_count()
        await self.send(text_data=json.dumps({
            'type': 'unread_count',
            'count': unread_count
        }))
        
        logger.info(f"User {self.user.username} connected to notifications WebSocket")

    async def disconnect(self, close_code):
        """Leave notification group when WebSocket disconnects."""
        if hasattr(self, 'user_group_name'):
            await self.channel_layer.group_discard(
                self.user_group_name,
                self.channel_name
            )
            logger.info(f"User {self.user.username} disconnected from notifications WebSocket")

    async def receive(self, text_data):
        """Handle messages from WebSocket."""
        try:
            text_data_json = json.loads(text_data)
            message_type = text_data_json.get('type')
            
            if message_type == 'mark_read':
                # Mark specific notification as read
                notification_id = text_data_json.get('notification_id')
                if notification_id:
                    await self.mark_notification_read(notification_id)
                    await self.send(text_data=json.dumps({
                        'type': 'notification_marked_read',
                        'notification_id': notification_id
                    }))
            
            elif message_type == 'mark_all_read':
                # Mark all notifications as read
                await self.mark_all_notifications_read()
                await self.send(text_data=json.dumps({
                    'type': 'all_notifications_marked_read'
                }))
                
            elif message_type == 'get_notifications':
                # Send recent notifications
                notifications = await self.get_recent_notifications()
                await self.send(text_data=json.dumps({
                    'type': 'notifications_list',
                    'notifications': notifications
                }))
                
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON received'
            }))

    # Message handlers for different notification types
    async def notification_message(self, event):
        """Send notification to WebSocket."""
        await self.send(text_data=json.dumps({
            'type': 'new_notification',
            'notification': event['notification']
        }))

    async def unread_count_update(self, event):
        """Send updated unread count to WebSocket."""
        await self.send(text_data=json.dumps({
            'type': 'unread_count',
            'count': event['count']
        }))

    # Database operations
    @database_sync_to_async
    def get_unread_notification_count(self):
        """Get count of unread notifications for the user."""
        return Notification.objects.filter(
            recipient=self.user,
            is_read=False
        ).count()

    @database_sync_to_async
    def get_recent_notifications(self, limit=20):
        """Get recent notifications for the user."""
        notifications = Notification.objects.filter(
            recipient=self.user
        ).order_by('-created_at')[:limit]
        
        return [{
            'id': notification.id,
            'type': 'notification',  # Generic type since model doesn't have a type field
            'title': 'Notification',  # Generic title
            'message': notification.message,
            'read': notification.is_read,
            'created_at': notification.created_at.isoformat(),
            'url': notification.url,
            'target_id': notification.target_object_id,
        } for notification in notifications]

    @database_sync_to_async
    def mark_notification_read(self, notification_id):
        """Mark a specific notification as read."""
        try:
            notification = Notification.objects.get(
                id=notification_id,
                recipient=self.user
            )
            notification.is_read = True
            notification.save()
            return True
        except Notification.DoesNotExist:
            return False

    @database_sync_to_async
    def mark_all_notifications_read(self):
        """Mark all notifications as read for the user."""
        Notification.objects.filter(
            recipient=self.user,
            is_read=False
        ).update(is_read=True)


class NotificationBroadcastConsumer(AsyncWebsocketConsumer):
    """
    Optional: Admin/system-wide notification broadcaster.
    
    This can be used for system announcements or maintenance notifications.
    """
    
    async def connect(self):
        # Only allow staff users to connect to broadcast channel
        if not self.scope["user"].is_staff:
            await self.close()
            return

        self.group_name = 'system_broadcast'
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )

    async def system_message(self, event):
        """Send system-wide message."""
        await self.send(text_data=json.dumps({
            'type': 'system_announcement',
            'message': event['message']
        }))