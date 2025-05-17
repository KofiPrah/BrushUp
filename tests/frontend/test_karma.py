"""
Test script for the karma point system in the Art Critique application.

This script demonstrates how karma is awarded when:
1. A user uploads a new artwork
2. A user creates a critique on an artwork
3. A user reacts to a critique (with different reaction types)

Run this script to verify that the karma point system is working correctly.
"""
import os
import sys
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'artcritique.settings')
django.setup()

# Import models after Django setup
from django.contrib.auth import get_user_model
from critique.models import ArtWork, Critique, Reaction, Profile

User = get_user_model()

def reset_karma_for_testing(users):
    """Reset karma to zero for testing purposes."""
    for user in users:
        user.profile.karma = 0
        user.profile.save(update_fields=['karma'])
        print(f"Reset karma for {user.username} to 0")

def create_test_users_and_content():
    """Create test users and content for demonstration."""
    # Create test users
    artist = User.objects.get_or_create(
        username='karma_artist',
        email='karma.artist@example.com',
    )[0]
    artist.set_password('testpassword')
    artist.save()
    
    critic = User.objects.get_or_create(
        username='karma_critic',
        email='karma.critic@example.com',
    )[0]
    critic.set_password('testpassword')
    critic.save()
    
    reactor = User.objects.get_or_create(
        username='karma_reactor',
        email='karma.reactor@example.com',
    )[0]
    reactor.set_password('testpassword')
    reactor.save()
    
    # Reset karma for testing
    reset_karma_for_testing([artist, critic, reactor])
    
    # Delete any previous test artwork, critique, and reactions
    ArtWork.objects.filter(title='Karma Test Artwork').delete()
    
    return artist, critic, reactor

def test_artwork_karma():
    """Test karma points for uploading an artwork."""
    artist, critic, reactor = create_test_users_and_content()
    
    # Check initial karma
    artist_karma_before = artist.profile.karma
    print(f"{artist.username}'s initial karma: {artist_karma_before}")
    
    # Create a test artwork
    artwork = ArtWork.objects.create(
        title='Karma Test Artwork',
        author=artist,
        description='An artwork to test the karma system',
        medium='Digital',
    )
    
    # Refresh user from database
    artist.refresh_from_db()
    
    # Check karma after creating artwork
    artist_karma_after = artist.profile.karma
    print(f"{artist.username}'s karma after uploading artwork: {artist_karma_after}")
    print(f"Karma points earned: {artist_karma_after - artist_karma_before}")
    
    return artwork

def test_critique_karma(artwork):
    """Test karma points for creating a critique."""
    critic = User.objects.get(username='karma_critic')
    
    # Check initial karma
    critic_karma_before = critic.profile.karma
    print(f"\n{critic.username}'s initial karma: {critic_karma_before}")
    
    # Create a test critique
    critique = Critique.objects.create(
        artwork=artwork,
        author=critic,
        text='This is a test critique to demonstrate karma points',
        composition_score=4,
        technique_score=5,
        originality_score=4,
    )
    
    # Refresh user from database
    critic.refresh_from_db()
    
    # Check karma after creating critique
    critic_karma_after = critic.profile.karma
    print(f"{critic.username}'s karma after posting critique: {critic_karma_after}")
    print(f"Karma points earned: {critic_karma_after - critic_karma_before}")
    
    return critique

def test_reaction_karma(critique):
    """Test karma points for receiving reactions."""
    critic = critique.author
    reactor = User.objects.get(username='karma_reactor')
    
    # Check initial karma
    critic_karma_before = critic.profile.karma
    print(f"\n{critic.username}'s initial karma: {critic_karma_before}")
    
    # Test different reaction types
    reaction_types = ['HELPFUL', 'INSPIRING', 'DETAILED']
    
    for reaction_type in reaction_types:
        # Create a reaction
        reaction = Reaction.objects.create(
            critique=critique,
            user=reactor,
            reaction_type=reaction_type
        )
        
        # Refresh user from database
        critic.refresh_from_db()
        
        # Check karma after receiving reaction
        critic_karma_after = critic.profile.karma
        karma_earned = critic_karma_after - critic_karma_before
        print(f"After {reaction_type} reaction: {critic.username}'s karma = {critic_karma_after} (earned {karma_earned} points)")
        
        # Update before karma for next iteration
        critic_karma_before = critic_karma_after
        
        # Delete the reaction to allow for testing other types
        reaction.delete()

def main():
    """Run the karma system test."""
    print("Starting karma point system test...")
    
    # Test karma for uploading artwork
    artwork = test_artwork_karma()
    
    # Test karma for creating a critique
    critique = test_critique_karma(artwork)
    
    # Test karma for receiving reactions
    test_reaction_karma(critique)
    
    print("\nKarma point test completed successfully!")
        
if __name__ == "__main__":
    main()