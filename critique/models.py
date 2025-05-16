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

class Critique(models.Model):
    """
    Model representing a structured critique on an artwork, 
    with focus on constructive feedback and analysis.
    """
    artwork = models.ForeignKey(ArtWork, on_delete=models.CASCADE, related_name='critiques')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='critiques')
    text = models.TextField(help_text="Critique content - analysis of the artwork")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Optional rating fields to provide numeric evaluation
    composition_score = models.PositiveSmallIntegerField(
        choices=[(i, i) for i in range(1, 11)], 
        null=True, 
        blank=True,
        help_text="Rating for composition (1-10)"
    )
    technique_score = models.PositiveSmallIntegerField(
        choices=[(i, i) for i in range(1, 11)], 
        null=True,
        blank=True,
        help_text="Rating for technique execution (1-10)"
    )
    originality_score = models.PositiveSmallIntegerField(
        choices=[(i, i) for i in range(1, 11)], 
        null=True,
        blank=True,
        help_text="Rating for originality/creativity (1-10)"
    )
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Critique'
        verbose_name_plural = 'Critiques'
    
    def __str__(self):
        return f"Critique by {self.author.username} on {self.artwork.title}"
    
    def get_average_score(self):
        """Calculate the average score across all rating dimensions that have values."""
        scores = [s for s in [self.composition_score, self.technique_score, self.originality_score] if s is not None]
        if not scores:
            return None
        return sum(scores) / len(scores)


class Reaction(models.Model):
    """
    Model to represent a user's reaction to a critique.
    Each user can only give one reaction of each type to a specific critique.
    """
    # Reaction type choices using TextChoices for better organization
    class ReactionType(models.TextChoices):
        HELPFUL = 'HELPFUL', 'Helpful'
        INSPIRING = 'INSPIRING', 'Inspiring'
        DETAILED = 'DETAILED', 'Detailed'
    
    # Relationships
    critique = models.ForeignKey(Critique, on_delete=models.CASCADE, related_name='reactions')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='critique_reactions')
    
    # Reaction data
    reaction_type = models.CharField(
        max_length=20, 
        choices=ReactionType.choices,
        help_text="The type of reaction given to the critique"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        # Ensure each user can only react once per type on a given critique
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'critique', 'reaction_type'],
                name='unique_user_critique_reaction'
            )
        ]
        ordering = ['-created_at']
        verbose_name = 'Critique Reaction'
        verbose_name_plural = 'Critique Reactions'
    
    def __str__(self):
        return f"{self.user.username}'s {self.reaction_type} reaction to critique by {self.critique.author.username}"
