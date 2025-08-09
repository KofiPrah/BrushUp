"""
Notification functionality for the Art Critique application.
This module contains functions for creating notifications for various events.
"""
from django.contrib.contenttypes.models import ContentType
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json
from .models import Notification

def create_critique_notification(critique):
    """
    Create a notification for the artwork author when a new critique is posted.
    Also sends real-time WebSocket notification.
    
    Args:
        critique: The Critique instance that triggered this notification
    """
    # Skip if author is critiquing their own work
    if critique.author == critique.artwork.author:
        return
        
    # Get the users involved
    artwork_author = critique.artwork.author
    critique_author = critique.author
    
    # Create notification for artwork author
    message = f"{critique_author.username} posted a critique on your artwork: '{critique.artwork.title}'"
    
    # Get content type for the critique object
    content_type = ContentType.objects.get_for_model(critique)
    
    # Create notification in database
    notification = Notification.objects.create(
        recipient=artwork_author,
        message=message,
        target_content_type=content_type,
        target_object_id=critique.id,
        url=f"/artworks/{critique.artwork.id}/"  # URL to the artwork detail page
    )
    
    # Send real-time WebSocket notification
    send_websocket_notification(artwork_author, notification, 'critique_posted')

def create_reaction_notification(reaction):
    """
    Create notification when someone reacts to a critique.
    
    Args:
        reaction: The Reaction instance that triggered this notification
    """
    # Skip if user is reacting to their own critique
    if reaction.user == reaction.critique.author:
        return
    
    critique_author = reaction.critique.author
    reactor_user = reaction.user
    
    # Create notification message based on reaction type
    reaction_display = {
        'helpful': 'found helpful',
        'inspiring': 'found inspiring', 
        'detailed': 'appreciated the detail in'
    }.get(reaction.type, 'reacted to')
    
    message = f"{reactor_user.username} {reaction_display} your critique on '{reaction.critique.artwork.title}'"
    
    # Get content type for the reaction object
    content_type = ContentType.objects.get_for_model(reaction)
    
    # Create notification in database
    notification = Notification.objects.create(
        recipient=critique_author,
        message=message,
        target_content_type=content_type,
        target_object_id=reaction.id,
        url=f"/artworks/{reaction.critique.artwork.id}/"
    )
    
    # Send real-time WebSocket notification
    send_websocket_notification(critique_author, notification, 'reaction_received')

def create_like_notification(artwork, user):
    """
    Create notification when someone likes an artwork.
    
    Args:
        artwork: The ArtWork instance that was liked
        user: The User who liked the artwork
    """
    # Skip if user is liking their own artwork
    if user == artwork.author:
        return
    
    artwork_author = artwork.author
    
    message = f"{user.username} liked your artwork: '{artwork.title}'"
    
    # Get content type for the artwork object
    content_type = ContentType.objects.get_for_model(artwork)
    
    # Create notification in database
    notification = Notification.objects.create(
        recipient=artwork_author,
        message=message,
        target_content_type=content_type,
        target_object_id=artwork.id,
        url=f"/artworks/{artwork.id}/"
    )
    
    # Send real-time WebSocket notification
    send_websocket_notification(artwork_author, notification, 'artwork_liked')

def send_websocket_notification(user, notification, notification_type):
    """
    Send real-time notification via WebSocket.
    
    Args:
        user: The User to send the notification to
        notification: The Notification instance
        notification_type: String indicating the type of notification
    """
    channel_layer = get_channel_layer()
    
    if channel_layer is None:
        # Channel layer not configured, skip WebSocket notification
        return
    
    # Prepare notification data
    notification_data = {
        'id': notification.id,
        'type': notification_type,
        'title': f"New {notification_type.replace('_', ' ').title()}",
        'message': notification.message,
        'url': notification.url,
        'read': notification.read,
        'created_at': notification.created_at.isoformat(),
        'artwork_id': getattr(notification.artwork, 'id', None) if hasattr(notification, 'artwork') else None,
        'critique_id': getattr(notification.critique, 'id', None) if hasattr(notification, 'critique') else None,
    }
    
    # Send to user's WebSocket group
    group_name = f'user_notifications_{user.id}'
    
    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            'type': 'notification_message',
            'notification': notification_data
        }
    )
    
    # Also send updated unread count
    unread_count = Notification.objects.filter(recipient=user, is_read=False).count()
    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            'type': 'unread_count_update',
            'count': unread_count
        }
    )

def create_reaction_notification(reaction):
    """
    Create a notification for the critique author when someone reacts to their critique.
    
    Args:
        reaction: The Reaction instance that triggered this notification
    """
    # Skip if user is reacting to their own critique
    if reaction.user == reaction.critique.author:
        return
        
    # Get the users involved
    critique_author = reaction.critique.author
    reaction_user = reaction.user
    
    # Get human-readable reaction type
    reaction_type_display = reaction.get_reaction_type_display()
    
    # Create notification message
    message = f"{reaction_user.username} found your critique on '{reaction.critique.artwork.title}' {reaction_type_display.lower()}"
    
    # Get content type for the reaction object
    content_type = ContentType.objects.get_for_model(reaction)
    
    # Create notification in database
    Notification.objects.create(
        recipient=critique_author,
        message=message,
        target_content_type=content_type,
        target_object_id=reaction.id,
        url=f"/artworks/{reaction.critique.artwork.id}/"  # URL to the artwork page
    )