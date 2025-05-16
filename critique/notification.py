"""
Simplified placeholder for notification functionality.
This will be fully implemented in Phase 8.
"""

def send_critique_notification(critique):
    """
    Send a notification about a new critique.
    This is a placeholder that will be fully implemented in Phase 8.
    
    Args:
        critique: The Critique instance that triggered this notification
    """
    # Skip if author is critiquing their own work
    if critique.author == critique.artwork.author:
        return
        
    # Get the users involved
    artwork_author = critique.artwork.author
    critique_author = critique.author
    
    # For now, just print to console for testing/demonstration
    print(f"[NOTIFICATION] User {critique_author.username} left a critique on {artwork_author.username}'s artwork '{critique.artwork.title}'")