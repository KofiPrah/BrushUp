"""
Notification functionality for the Art Critique application.
This module contains functions for creating notifications for various events.
"""
from django.contrib.contenttypes.models import ContentType
from .models import Notification

def create_critique_notification(critique):
    """
    Create a notification for the artwork author when a new critique is posted.
    
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
    Notification.objects.create(
        recipient=artwork_author,
        message=message,
        target_content_type=content_type,
        target_object_id=critique.id,
        url=f"/artworks/{critique.artwork.id}/"  # URL to the artwork detail page
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