#!/usr/bin/env python
"""
Karma Recalculation Script
Recalculates all karma scores based on actual user activities.
"""

import os
import sys
import django

# Add the project root to the Python path
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'artcritique.settings')
django.setup()

from django.contrib.auth.models import User
from critique.models import Profile, ArtWork, Critique, KarmaEvent
from critique.karma import (
    award_artwork_upload_karma, 
    award_critique_karma, 
    award_daily_visit_karma,
    award_like_karma
)
from django.utils import timezone
from datetime import datetime, timedelta

def recalculate_all_karma():
    """Recalculate karma for all users based on their activities."""
    
    print("Starting karma recalculation...")
    
    # Get all users
    users = User.objects.all()
    total_users = users.count()
    
    print(f"Processing {total_users} users...")
    
    for i, user in enumerate(users, 1):
        print(f"\nProcessing user {i}/{total_users}: {user.username}")
        
        # Ensure user has a profile
        profile, created = Profile.objects.get_or_create(user=user)
        if created:
            print(f"  Created profile for {user.username}")
        
        # Reset karma to 0
        profile.karma = 0
        profile.save()
        
        # Award karma for artwork uploads
        artworks = ArtWork.objects.filter(author=user)
        artwork_count = artworks.count()
        if artwork_count > 0:
            print(f"  Found {artwork_count} artworks")
            for artwork in artworks:
                # Award 10 points per artwork upload
                KarmaEvent.objects.create(
                    user=user,
                    action='artwork_upload',
                    points=10,
                    reason=f'Uploaded artwork: {artwork.title}',
                    created_at=artwork.created_at
                )
                profile.karma += 10
        
        # Award karma for critiques given
        critiques = Critique.objects.filter(author=user)
        critique_count = critiques.count()
        if critique_count > 0:
            print(f"  Found {critique_count} critiques given")
            for critique in critiques:
                # Award 15 points per critique given
                KarmaEvent.objects.create(
                    user=user,
                    action='critique_given',
                    points=15,
                    reason=f'Gave critique on: {critique.artwork.title}',
                    created_at=critique.created_at
                )
                profile.karma += 15
        
        # Award karma for critiques received (5 points each)
        critiques_received = Critique.objects.filter(artwork__author=user)
        critiques_received_count = critiques_received.count()
        if critiques_received_count > 0:
            print(f"  Found {critiques_received_count} critiques received")
            for critique in critiques_received:
                KarmaEvent.objects.create(
                    user=user,
                    action='critique_received',
                    points=5,
                    reason=f'Received critique on: {critique.artwork.title}',
                    created_at=critique.created_at
                )
                profile.karma += 5
        
        # Award karma for artwork likes received
        total_likes = sum(artwork.total_likes() for artwork in artworks)
        if total_likes > 0:
            print(f"  Found {total_likes} total likes received")
            # Award 2 points per like received
            KarmaEvent.objects.create(
                user=user,
                action='likes_received',
                points=total_likes * 2,
                reason=f'Received {total_likes} likes on artworks'
            )
            profile.karma += (total_likes * 2)
        
        # Award daily visit karma (simulate some daily visits)
        # Award karma for being an active member (based on account age)
        if user.date_joined:
            days_since_joined = (timezone.now() - user.date_joined).days
            if days_since_joined > 0:
                # Award 1 point per day of membership (up to 30 days max)
                visit_days = min(days_since_joined, 30)
                KarmaEvent.objects.create(
                    user=user,
                    action='daily_visit',
                    points=visit_days,
                    reason=f'Active member for {visit_days} days'
                )
                profile.karma += visit_days
        
        # Save the updated karma
        profile.save()
        
        print(f"  Final karma for {user.username}: {profile.karma}")
    
    print("\nKarma recalculation completed!")
    
    # Print summary statistics
    print("\n=== KARMA SUMMARY ===")
    total_karma_events = KarmaEvent.objects.count()
    total_karma_points = sum(profile.karma for profile in Profile.objects.all())
    
    print(f"Total karma events created: {total_karma_events}")
    print(f"Total karma points awarded: {total_karma_points}")
    
    # Show top users by karma
    top_users = Profile.objects.select_related('user').order_by('-karma')[:5]
    print("\nTop 5 users by karma:")
    for i, profile in enumerate(top_users, 1):
        print(f"{i}. {profile.user.username}: {profile.karma} points")
    
    print("\n=== RECALCULATION COMPLETE ===")

if __name__ == '__main__':
    recalculate_all_karma()