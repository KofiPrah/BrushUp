"""
Karma system for Art Critique platform.

This module handles the logic for awarding and tracking karma points
based on user actions and contributions to the community.
"""

from django.db import transaction
from django.contrib.auth.models import User
from django.utils import timezone

from .models import Profile, ArtWork, Comment, Critique

# Karma point values for different actions
KARMA_VALUES = {
    'artwork_upload': 5,       # Uploading new artwork
    'comment_received': 2,     # Someone comments on your artwork
    'comment_posted': 1,       # Posting a comment on someone's artwork
    'artwork_liked': 3,        # Someone likes your artwork
    'like_given': 1,           # Liking someone's artwork
    'critique_received': 5,    # Someone provides a detailed critique
    'critique_posted': 3,      # Providing a detailed critique
    'daily_visit': 1,          # Daily visit bonus
}

def award_karma(user, action, reason=None):
    """
    Award karma points to a user for a specific action.
    
    Args:
        user: User object to award karma to
        action: String identifying the action (must be a key in KARMA_VALUES)
        reason: Optional string with additional context about why karma was awarded
        
    Returns:
        Boolean indicating success
    """
    if action not in KARMA_VALUES:
        return False
    
    points = KARMA_VALUES[action]
    
    with transaction.atomic():
        # Create a KarmaEvent record
        from .models import KarmaEvent
        
        event = KarmaEvent.objects.create(
            user=user,
            action=action,
            points=points,
            reason=reason
        )
        
        # Update user's total karma
        profile = user.profile
        profile.karma += points
        profile.save(update_fields=['karma'])
        
    return True

def award_artwork_upload_karma(artwork):
    """Award karma for uploading a new artwork"""
    return award_karma(
        artwork.author, 
        'artwork_upload', 
        f"Uploaded artwork: {artwork.title}"
    )

def award_comment_karma(comment):
    """Award karma for commenting and receiving comments"""
    # Award comment poster
    award_karma(
        comment.author, 
        'comment_posted', 
        f"Commented on artwork: {comment.artwork.title}"
    )
    
    # Award artwork author for receiving comment (if not self-commenting)
    if comment.author != comment.artwork.author:
        award_karma(
            comment.artwork.author, 
            'comment_received', 
            f"Received comment from {comment.author.username}"
        )

def award_like_karma(artwork, user):
    """Award karma for liking and receiving likes"""
    # Award the person giving the like
    award_karma(
        user, 
        'like_given', 
        f"Liked artwork: {artwork.title}"
    )
    
    # Award the artwork owner for receiving a like (if not self-liking)
    if user != artwork.author:
        award_karma(
            artwork.author, 
            'artwork_liked', 
            f"Artwork liked by {user.username}: {artwork.title}"
        )

def award_critique_karma(critique):
    """Award karma for giving and receiving critiques"""
    # Award critique author
    award_karma(
        critique.author, 
        'critique_posted', 
        f"Posted critique on artwork: {critique.artwork.title}"
    )
    
    # Award artwork author for receiving critique (if not self-critique)
    if critique.author != critique.artwork.author:
        award_karma(
            critique.artwork.author, 
            'critique_received', 
            f"Received critique from {critique.author.username}"
        )



def award_daily_visit_karma(user):
    """Award karma for daily site visits"""
    # Check if user already received daily visit karma today
    from .models import KarmaEvent
    today = timezone.now().date()
    
    already_awarded = KarmaEvent.objects.filter(
        user=user,
        action='daily_visit',
        created_at__date=today
    ).exists()
    
    if not already_awarded:
        return award_karma(
            user, 
            'daily_visit', 
            f"Daily visit on {today}"
        )
    
    return False

def get_karma_leaderboard(limit=10):
    """Get the top users by karma points"""
    return Profile.objects.order_by('-karma')[:limit]

def get_user_karma_history(user, limit=20):
    """Get recent karma events for a user"""
    from .models import KarmaEvent
    return KarmaEvent.objects.filter(user=user).order_by('-created_at')[:limit]

def deduct_critique_karma(user, critique):
    """
    Deduct karma points when a critique is deleted.
    This reverses the karma awarded for posting the critique.
    
    Args:
        user: User who is deleting the critique
        critique: Critique object being deleted
        
    Returns:
        Boolean indicating success
    """
    points_to_deduct = -KARMA_VALUES['critique_posted']  # Negative to deduct
    
    with transaction.atomic():
        # Create a negative KarmaEvent record
        from .models import KarmaEvent
        
        event = KarmaEvent.objects.create(
            user=user,
            action='critique_deleted',
            points=points_to_deduct,
            reason=f"Deleted critique on artwork: {critique.artwork.title}",
            created_at=timezone.now()
        )
        
        # Update user's total karma
        profile, created = Profile.objects.get_or_create(user=user)
        profile.karma += points_to_deduct
        profile.save()
        
        return True