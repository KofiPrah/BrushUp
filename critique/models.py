from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.conf import settings
from django.utils import timezone

# Import S3 storage backend for files if S3 is enabled
if settings.USE_S3:
    from artcritique.storage_backends import PublicMediaStorage
    s3_storage = PublicMediaStorage()
else:
    s3_storage = None

# Create your models here.
class Profile(models.Model):
    """
    Extended user profile model with additional information about the user.
    Includes karma points earned through positive contributions and user role.
    """
    # User role choices
    ROLE_USER = 'USER'
    ROLE_MODERATOR = 'MODERATOR'
    ROLE_ADMIN = 'ADMIN'
    
    ROLE_CHOICES = [
        (ROLE_USER, 'Regular User'),
        (ROLE_MODERATOR, 'Moderator'),
        (ROLE_ADMIN, 'Administrator'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=100, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True, 
                                    storage=s3_storage if settings.USE_S3 else None)
    profile_picture_url = models.URLField(max_length=1000, blank=True)  # Legacy URL field
    website = models.URLField(max_length=200, blank=True)
    karma = models.IntegerField(default=0, help_text="Points earned through positive contributions")
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=ROLE_USER,
        help_text="User role determines permissions in the system"
    )
    
    def __str__(self):
        return f"{self.user.username}'s profile"
    
    def is_moderator_or_admin(self):
        """Check if the user is a moderator or administrator."""
        return self.role in [self.ROLE_MODERATOR, self.ROLE_ADMIN] or self.user.is_superuser
    
    def is_admin(self):
        """Check if the user is an administrator."""
        return self.role == self.ROLE_ADMIN or self.user.is_superuser

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create a Profile instance when a new User is created."""
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save the Profile instance when the User is saved."""
    instance.profile.save()

class Folder(models.Model):
    """
    Model representing a portfolio folder that groups artworks together.
    Allows users to organize their artworks into themed collections.
    """
    # Visibility choices
    VISIBILITY_PUBLIC = 'public'
    VISIBILITY_PRIVATE = 'private'
    VISIBILITY_UNLISTED = 'unlisted'  # Can be accessed with direct link but not publicly listed
    
    VISIBILITY_CHOICES = [
        (VISIBILITY_PUBLIC, 'Public'),
        (VISIBILITY_PRIVATE, 'Private'),
        (VISIBILITY_UNLISTED, 'Unlisted'),
    ]
    
    name = models.CharField(
        max_length=200, 
        help_text="Name of the portfolio folder (e.g., 'Landscape Series', 'Abstract Works')"
    )
    description = models.TextField(
        blank=True, 
        help_text="Optional description of this portfolio folder"
    )
    owner = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='folders',
        help_text="The user who owns this portfolio folder"
    )
    is_public = models.CharField(
        max_length=20,
        choices=VISIBILITY_CHOICES,
        default=VISIBILITY_PUBLIC,
        help_text="Visibility level of this portfolio folder"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Optional fields for enhanced portfolio features
    cover_image = models.ImageField(
        upload_to='folder_covers/', 
        blank=True, 
        null=True,
        storage=s3_storage if settings.USE_S3 else None,
        help_text="Optional cover image for the portfolio folder"
    )
    slug = models.SlugField(
        max_length=250, 
        blank=True,
        help_text="URL-friendly version of the folder name"
    )
    
    class Meta:
        ordering = ['-updated_at', '-created_at']
        unique_together = ['owner', 'slug']  # Ensure unique slugs per user
        verbose_name = 'Portfolio Folder'
        verbose_name_plural = 'Portfolio Folders'
    
    def __str__(self):
        return f"{self.owner.username}'s {self.name}"
    
    def get_absolute_url(self):
        """Return the URL for this folder."""
        return f"/profile/{self.owner.username}/folder/{self.slug}/"
    
    def artwork_count(self):
        """Return the number of artworks in this folder."""
        return self.artworks.count()
    
    def is_viewable_by(self, user):
        """Check if a user can view this folder."""
        if self.is_public == self.VISIBILITY_PUBLIC:
            return True
        elif self.is_public == self.VISIBILITY_PRIVATE:
            return user == self.owner
        elif self.is_public == self.VISIBILITY_UNLISTED:
            return True  # Accessible with direct link
        return False
    
    def save(self, *args, **kwargs):
        """Override save to auto-generate slug if not provided."""
        if not self.slug:
            from django.utils.text import slugify
            import uuid
            base_slug = slugify(self.name)
            unique_slug = base_slug
            counter = 1
            
            # Ensure slug uniqueness for this user
            while Folder.objects.filter(owner=self.owner, slug=unique_slug).exists():
                unique_slug = f"{base_slug}-{counter}"
                counter += 1
            
            self.slug = unique_slug
        
        super().save(*args, **kwargs)

class ArtWorkVersion(models.Model):
    """Model to track different versions of artwork for comparison"""
    artwork = models.ForeignKey('ArtWork', on_delete=models.CASCADE, related_name='versions')
    version_number = models.PositiveIntegerField()
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='artwork_versions/', blank=True, null=True,
                           storage=s3_storage if settings.USE_S3 else None)
    created_at = models.DateTimeField(auto_now_add=True)
    version_notes = models.TextField(blank=True, help_text="Notes about changes in this version")
    
    # Copy of artwork metadata at time of version creation
    medium = models.CharField(max_length=100, blank=True)
    dimensions = models.CharField(max_length=100, blank=True)
    tags = models.CharField(max_length=200, blank=True)
    
    class Meta:
        unique_together = ['artwork', 'version_number']
        ordering = ['-version_number']
    
    def __str__(self):
        return f"{self.artwork.title} - Version {self.version_number}"

class ArtWork(models.Model):
    """
    Model representing an artwork submitted by a user.
    """
    # Visibility choices
    VISIBILITY_PUBLIC = 'public'
    VISIBILITY_PRIVATE = 'private'
    VISIBILITY_UNLISTED = 'unlisted'
    
    VISIBILITY_CHOICES = [
        (VISIBILITY_PUBLIC, 'Public'),
        (VISIBILITY_PRIVATE, 'Private'),
        (VISIBILITY_UNLISTED, 'Unlisted'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='artworks/', blank=True, null=True,
                           storage=s3_storage if settings.USE_S3 else None)  # Image file
    image_url = models.URLField(max_length=1000, blank=True)  # Legacy URL field for backwards compatibility
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    author = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='artworks',
        null=True,  # Allow null for migration purposes
    )
    
    # Draft/Published status
    is_published = models.BooleanField(default=True, help_text="Whether this artwork is published and visible to others")
    
    # Visibility settings
    visibility = models.CharField(
        max_length=20,
        choices=VISIBILITY_CHOICES,
        default=VISIBILITY_PUBLIC,
        help_text="Who can see this artwork"
    )
    
    # Critique request flag
    seeking_critique = models.BooleanField(default=False, help_text="Whether the artist is actively seeking critique for this piece")
    
    # Additional optional fields
    medium = models.CharField(max_length=100, blank=True)  # e.g., "Oil painting", "Digital art"
    dimensions = models.CharField(max_length=100, blank=True)  # e.g., "24x36 inches"
    tags = models.CharField(max_length=200, blank=True)  # Comma-separated tags
    
    # Portfolio folder organization
    folder = models.ForeignKey(
        Folder,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='artworks',
        help_text="Optional portfolio folder this artwork belongs to"
    )
    
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
    
    @property
    def tags_list(self):
        """Return tags as a list."""
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',') if tag.strip()]
        return []
    
    @property
    def critique_count(self):
        """Return the number of critiques for this artwork."""
        return self.critiques.filter(is_hidden=False).count()
    
    def create_version(self, version_notes=""):
        """Create a new version of this artwork with current state"""
        next_version = self.get_next_version_number()
        
        version = ArtWorkVersion.objects.create(
            artwork=self,
            version_number=next_version,
            title=self.title,
            description=self.description,
            image=self.image,
            version_notes=version_notes,
            medium=self.medium,
            dimensions=self.dimensions,
            tags=self.tags
        )
        return version
    
    def get_next_version_number(self):
        """Get the next version number for this artwork"""
        last_version = self.versions.first()
        return (last_version.version_number + 1) if last_version else 1
    
    def get_latest_version(self):
        """Get the most recent version of this artwork"""
        return self.versions.first()
    
    def has_versions(self):
        """Check if this artwork has any versions"""
        return self.versions.exists()
    
    @property
    def version_count(self):
        """Return the number of versions for this artwork"""
        return self.versions.count()


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
    
    # Hide from public view - only visible to the artist and author
    is_hidden = models.BooleanField(default=False, help_text="If true, critique is hidden from public view and only visible to the artist and author")
    hidden_reason = models.TextField(blank=True, null=True, help_text="Optional reason for hiding the critique")
    hidden_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='hidden_critiques')
    hidden_at = models.DateTimeField(null=True, blank=True)
    
    # Moderation flags
    is_flagged = models.BooleanField(default=False, help_text="If true, critique has been flagged for moderation")
    flag_reason = models.TextField(blank=True, null=True, help_text="Reason for flagging the critique")
    flagged_by = models.ManyToManyField(User, related_name='flagged_critiques', blank=True)
    moderation_status = models.CharField(
        max_length=20,
        choices=[
            ('PENDING', 'Pending Review'),
            ('APPROVED', 'Approved'),
            ('REJECTED', 'Rejected')
        ],
        default='APPROVED',
        help_text="Moderation status of this critique"
    )
    
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
        
    def has_user_reaction(self, user):
        """Check if a user has given any reaction to this critique."""
        if not user.is_authenticated:
            return False
        return self.reactions.filter(user=user).exists()
        
    def has_user_reaction_helpful(self, user=None):
        """Check if a user has given a HELPFUL reaction to this critique."""
        # Get the user from the context if not provided explicitly
        from django.contrib.auth.models import AnonymousUser
        from threading import currentThread
        
        # Get thread local request
        request = getattr(currentThread(), 'request', None)
        if user is None and request is not None:
            user = getattr(request, 'user', None)
        
        if not user or not hasattr(user, 'is_authenticated') or not user.is_authenticated:
            return False
            
        return self.reactions.filter(user=user, reaction_type='HELPFUL').exists()
        
    def has_user_reaction_inspiring(self, user=None):
        """Check if a user has given an INSPIRING reaction to this critique."""
        # Get the user from the context if not provided explicitly
        from django.contrib.auth.models import AnonymousUser
        
        # Get current user if not provided
        if user is None:
            from django.contrib.auth import get_user
            try:
                from django.contrib.auth.middleware import get_user
                from django.contrib.auth.models import AnonymousUser
                user = AnonymousUser()
            except:
                pass
        
        if not user or not hasattr(user, 'is_authenticated') or not user.is_authenticated:
            return False
            
        return self.reactions.filter(user=user, reaction_type='INSPIRING').exists()
        
    def has_user_reaction_detailed(self, user=None):
        """Check if a user has given a DETAILED reaction to this critique."""
        # Get the user from the context if not provided explicitly
        from django.contrib.auth.models import AnonymousUser
        
        # Get current user if not provided
        if user is None:
            from django.contrib.auth import get_user
            try:
                from django.contrib.auth.middleware import get_user
                from django.contrib.auth.models import AnonymousUser
                user = AnonymousUser()
            except:
                pass
        
        if not user or not hasattr(user, 'is_authenticated') or not user.is_authenticated:
            return False
            
        return self.reactions.filter(user=user, reaction_type='DETAILED').exists()
        
    def get_helpful_count(self):
        """Get count of HELPFUL reactions."""
        return self.reactions.filter(reaction_type='HELPFUL').count()
        
    def get_inspiring_count(self):
        """Get count of INSPIRING reactions."""
        return self.reactions.filter(reaction_type='INSPIRING').count()
        
    def get_detailed_count(self):
        """Get count of DETAILED reactions."""
        return self.reactions.filter(reaction_type='DETAILED').count()
        
    def hide(self, user, reason=None):
        """Hide a critique from public view."""
        from django.utils import timezone
        self.is_hidden = True
        self.hidden_reason = reason
        self.hidden_by = user
        self.hidden_at = timezone.now()
        self.save()
        
    def unhide(self):
        """Unhide a critique."""
        self.is_hidden = False
        self.hidden_reason = None
        self.hidden_by = None
        self.hidden_at = None
        self.save()
        
    def flag(self, user, reason):
        """Flag a critique for moderation."""
        self.is_flagged = True
        self.flag_reason = reason
        self.flagged_by.add(user)
        self.moderation_status = 'PENDING'
        self.save()
        
    def approve(self):
        """Approve a flagged critique after moderation."""
        self.is_flagged = False
        self.moderation_status = 'APPROVED'
        self.save()
        
    def reject(self):
        """Reject a flagged critique after moderation."""
        self.is_flagged = True
        self.moderation_status = 'REJECTED'
        self.save()


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


class KarmaEvent(models.Model):
    """
    Model to track karma point awards and the reasons behind them.
    Provides a historical record of how users earned karma points.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='karma_events')
    points = models.IntegerField(default=0)
    action = models.CharField(max_length=50)
    reason = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    # Optional content object reference (what the karma was earned for)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Karma Event'
        verbose_name_plural = 'Karma Events'
        
    def __str__(self):
        return f"Karma: {self.points} points to {self.user.username} for {self.action}"


class CritiqueReply(models.Model):
    """
    Model for artist replies to critiques.
    Allows the artwork owner to respond to critiques without deleting them.
    """
    critique = models.ForeignKey(Critique, on_delete=models.CASCADE, related_name='replies')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='critique_replies')
    text = models.TextField(help_text="Reply to the critique")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Critique Reply'
        verbose_name_plural = 'Critique Replies'
    
    def __str__(self):
        return f"Reply by {self.author.username} to critique on {self.critique.artwork.title}"


class Notification(models.Model):
    """Model to store user notifications."""
    recipient = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='notifications'
    )
    message = models.TextField()
    # Optional link to relevant content
    target_content_type = models.ForeignKey(
        ContentType, 
        on_delete=models.CASCADE,
        null=True, 
        blank=True
    )
    target_object_id = models.PositiveIntegerField(null=True, blank=True)
    target = GenericForeignKey('target_content_type', 'target_object_id')
    # Optional direct URL for simple notifications
    url = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'is_read', 'created_at'])
        ]
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
    
    def __str__(self):
        return f"Notification for {self.recipient.username}: {self.message[:50]}"
