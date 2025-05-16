from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Critique, Reaction
from .notification import create_critique_notification, create_reaction_notification

@receiver(post_save, sender=Critique)
def notify_artwork_author_on_critique(sender, instance, created, **kwargs):
    """
    Signal handler to notify an artwork author when a new critique is created on their artwork.
    
    Creates a notification for the artwork owner when someone critiques their work.
    
    Args:
        sender: The model class (Critique)
        instance: The actual Critique instance being saved
        created: Boolean indicating if this is a new Critique (True) or an update (False)
    """
    if created:  # Only send notification on new critiques, not updates
        try:
            # Send notification through our notification module
            create_critique_notification(instance)
        except Exception as e:
            # Log errors but don't stop the critique from being created
            print(f"[ERROR] Failed to send notification for critique: {str(e)}")

@receiver(post_save, sender=Reaction)
def notify_critique_author_on_reaction(sender, instance, created, **kwargs):
    """
    Signal handler to notify a critique author when someone reacts to their critique.
    
    Creates a notification for the critique author when their critique receives a reaction.
    
    Args:
        sender: The model class (Reaction)
        instance: The actual Reaction instance being saved
        created: Boolean indicating if this is a new Reaction (True) or an update (False)
    """
    if created:  # Only send notification on new reactions, not updates
        try:
            # Send notification through our notification module
            create_reaction_notification(instance)
        except Exception as e:
            # Log errors but don't stop the reaction from being created
            print(f"[ERROR] Failed to send notification for reaction: {str(e)}")