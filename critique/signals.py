from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Critique
from .notification import send_critique_notification

@receiver(post_save, sender=Critique)
def notify_artwork_author_on_critique(sender, instance, created, **kwargs):
    """
    Signal handler to notify an artwork author when a new critique is created on their artwork.
    
    This signal handler will be fully implemented in Phase 8 to include
    real-time notifications and email delivery.
    
    Args:
        sender: The model class (Critique)
        instance: The actual Critique instance being saved
        created: Boolean indicating if this is a new Critique (True) or an update (False)
    """
    if created:  # Only send notification on new critiques, not updates
        try:
            # Send notification through our notification module
            send_critique_notification(instance)
        except Exception as e:
            # Log errors but don't stop the critique from being created
            print(f"[ERROR] Failed to send notification for critique: {str(e)}")