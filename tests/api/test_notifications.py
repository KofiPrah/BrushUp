"""
Test script for the notification system in the Art Critique application.

This script demonstrates how notifications are generated when:
1. A user creates a critique on an artwork
2. A user reacts to a critique

Run this script to verify that the notification signals are working correctly.
"""
import os
import sys
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'artcritique.settings')
django.setup()

# Import models after Django setup
from django.contrib.auth import get_user_model
from critique.models import ArtWork, Critique, Reaction, Notification

User = get_user_model()

def create_test_users_and_content():
    """Create test users and content for demonstration."""
    # Create test users
    artist = User.objects.get_or_create(
        username='artist_user',
        email='artist@example.com',
    )[0]
    artist.set_password('testpassword')
    artist.save()
    
    critic = User.objects.get_or_create(
        username='critic_user',
        email='critic@example.com',
    )[0]
    critic.set_password('testpassword')
    critic.save()
    
    reactor = User.objects.get_or_create(
        username='reaction_user',
        email='reactor@example.com',
    )[0]
    reactor.set_password('testpassword')
    reactor.save()
    
    # Create a test artwork
    artwork = ArtWork.objects.get_or_create(
        title='Test Notification Artwork',
        author=artist,
        description='An artwork to test the notification system',
        medium='Digital',
    )[0]
    
    # Create a test critique
    critique = Critique.objects.get_or_create(
        artwork=artwork,
        author=critic,
        text='This is a test critique to demonstrate notifications',
        composition_score=4,
        technique_score=5,
        originality_score=4,
    )[0]
    
    return artist, critic, reactor, artwork, critique

def verify_notifications():
    """Check if notifications were created and display them."""
    all_notifications = Notification.objects.all().order_by('-created_at')
    
    if not all_notifications:
        print("No notifications found. Something may be wrong with the signal handlers.")
        return False
    
    print(f"\nFound {all_notifications.count()} notifications:")
    for i, notification in enumerate(all_notifications, 1):
        print(f"{i}. To: {notification.recipient.username} - {notification.message}")
        print(f"   Type: {notification.target_content_type}")
        print(f"   Created: {notification.created_at}")
        print(f"   Read: {'Yes' if notification.is_read else 'No'}")
        print("")
    
    return True

def create_reaction(critique, user):
    """Create a reaction on a critique."""
    # First remove any existing reactions from this user
    Reaction.objects.filter(critique=critique, user=user).delete()
    
    # Create a helpful reaction
    reaction = Reaction.objects.create(
        critique=critique,
        user=user,
        reaction_type='HELPFUL'
    )
    
    return reaction

def main():
    """Run the notification test."""
    print("Starting notification system test...")
    
    # Clear existing notifications for a clean test
    Notification.objects.all().delete()
    print("Cleared existing notifications.")
    
    # Create test data
    artist, critic, reactor, artwork, critique = create_test_users_and_content()
    print(f"Created test users: {artist.username}, {critic.username}, {reactor.username}")
    print(f"Created artwork: '{artwork.title}' by {artwork.author.username}")
    print(f"Created critique by {critique.author.username} on '{critique.artwork.title}'")
    
    # Create a reaction to trigger the reaction notification
    reaction = create_reaction(critique, reactor)
    print(f"Created {reaction.get_reaction_type_display()} reaction by {reaction.user.username}")
    
    # Verify that notifications were created by our signals
    success = verify_notifications()
    
    if success:
        print("Notification test completed successfully!")
    else:
        print("Notification test failed - no notifications were found.")
        
if __name__ == "__main__":
    main()