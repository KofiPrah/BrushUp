from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.
class Profile(models.Model):
    """
    Extended user profile model with additional information about the user.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=100, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    profile_picture_url = models.URLField(max_length=1000, blank=True)  # Legacy URL field
    website = models.URLField(max_length=200, blank=True)
    
    def __str__(self):
        return f"{self.user.username}'s profile"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create a Profile instance when a new User is created."""
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save the Profile instance when the User is saved."""
    instance.profile.save()

class ArtWork(models.Model):
    """
    Model representing an artwork submitted by a user.
    """
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='artworks/', blank=True, null=True)  # Image file
    image_url = models.URLField(max_length=1000, blank=True)  # Legacy URL field for backwards compatibility
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    author = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='artworks',
        null=True,  # Allow null for migration purposes
    )
    
    # Additional optional fields
    medium = models.CharField(max_length=100, blank=True)  # e.g., "Oil painting", "Digital art"
    dimensions = models.CharField(max_length=100, blank=True)  # e.g., "24x36 inches"
    tags = models.CharField(max_length=200, blank=True)  # Comma-separated tags
    
    # Users who liked this artwork
    likes = models.ManyToManyField(
        User,
        related_name='liked_artworks',
        blank=True,
    )
    
    def __str__(self):
        return self.title
        
    def total_likes(self):
        """Return the total number of likes for this artwork."""
        return self.likes.count()

class Review(models.Model):
    artwork = models.ForeignKey(ArtWork, on_delete=models.CASCADE, related_name='reviews')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review for {self.artwork.title} by {self.reviewer.username}"
        
class Comment(models.Model):
    """
    Model representing a comment on an artwork.
    """
    artwork = models.ForeignKey(ArtWork, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Comment by {self.author.username} on {self.artwork.title}"
