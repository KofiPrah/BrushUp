from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from .models import Critique, Reaction, ArtWork
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

def award_karma_points(user, points):
    """
    Award karma points to a user.
    
    Args:
        user: The User instance to award points to
        points: The number of points to award
    """
    if user and points > 0:
        try:
            with transaction.atomic():
                # Safely update karma points in the user's profile
                profile = user.profile
                profile.karma += points
                profile.save(update_fields=['karma'])
                print(f"[KARMA] Awarded {points} karma points to {user.username}")
        except Exception as e:
            print(f"[ERROR] Failed to award karma points: {str(e)}")

@receiver(post_save, sender=ArtWork)
def award_karma_for_new_artwork(sender, instance, created, **kwargs):
    """
    Signal handler to award karma points when a user uploads a new artwork.
    
    Args:
        sender: The model class (ArtWork)
        instance: The actual ArtWork instance being saved
        created: Boolean indicating if this is a new ArtWork (True) or an update (False)
    """
    if created:  # Only award karma on new artworks, not updates
        # Award 1 point for sharing a new artwork
        award_karma_points(instance.author, 1)

@receiver(post_save, sender=Critique)
def award_karma_for_new_critique(sender, instance, created, **kwargs):
    """
    Signal handler to award karma points when a user posts a new critique.
    
    Args:
        sender: The model class (Critique)
        instance: The actual Critique instance being saved
        created: Boolean indicating if this is a new Critique (True) or an update (False)
    """
    if created:  # Only award karma on new critiques, not updates
        # Award 1 point for providing a critique
        award_karma_points(instance.author, 1)

@receiver(post_save, sender=Reaction)
def notify_critique_author_on_reaction(sender, instance, created, **kwargs):
    """
    Signal handler to notify a critique author when someone reacts to their critique.
    Also awards karma points based on the reaction type.
    
    Creates a notification for the critique author when their critique receives a reaction.
    
    Args:
        sender: The model class (Reaction)
        instance: The actual Reaction instance being saved
        created: Boolean indicating if this is a new Reaction (True) or an update (False)
    """
    if created:  # Only process new reactions, not updates
        try:
            # Send notification through our notification module
            create_reaction_notification(instance)
            
            # Award karma points based on reaction type
            critique_author = instance.critique.author
            
            # Don't award karma if the user is reacting to their own critique
            if instance.user == critique_author:
                return
                
            # Define karma points for different reaction types
            karma_points = {
                'HELPFUL': 2,     # Most valuable reaction
                'INSPIRING': 1,   # Medium value
                'DETAILED': 1     # Medium value
            }
            
            # Award points based on reaction type
            reaction_type = instance.reaction_type
            if reaction_type in karma_points:
                points = karma_points[reaction_type]
                award_karma_points(critique_author, points)
                
        except Exception as e:
            # Log errors but don't stop the reaction from being created
            print(f"[ERROR] Failed to process reaction: {str(e)}")