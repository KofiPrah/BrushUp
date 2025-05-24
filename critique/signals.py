"""
Signal handlers for the critique app.
This module contains Django signal handlers to track user actions and award karma points.
"""

from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver

from .models import ArtWork, Comment, Critique, KarmaEvent
from .karma import (
    award_artwork_upload_karma, 
    award_comment_karma, 
    award_like_karma,
    award_critique_karma
)


@receiver(post_save, sender=ArtWork)
def award_karma_for_artwork_upload(sender, instance, created, **kwargs):
    """Award karma points when a user uploads a new artwork."""
    if created and instance.author:
        award_artwork_upload_karma(instance)


@receiver(post_save, sender=Comment)
def award_karma_for_comment(sender, instance, created, **kwargs):
    """Award karma points when a user comments on an artwork."""
    if created:
        award_comment_karma(instance)


@receiver(m2m_changed, sender=ArtWork.likes.through)
def handle_artwork_likes(sender, instance, action, pk_set, **kwargs):
    """Award karma points when artwork is liked or unliked."""
    # Only process when likes are added
    if action == 'post_add' and pk_set:
        from django.contrib.auth.models import User
        for user_id in pk_set:
            try:
                user = User.objects.get(id=user_id)
                award_like_karma(instance, user)
            except User.DoesNotExist:
                continue


@receiver(post_save, sender=Critique)
def award_karma_for_critique(sender, instance, created, **kwargs):
    """Award karma points when a user creates a critique."""
    if created:
        award_critique_karma(instance)


