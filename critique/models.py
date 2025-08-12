from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.conf import settings
from django.utils import timezone
from .validators import validate_image_file

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
        validators=[validate_image_file],
        help_text="Optional cover image for the portfolio folder. Supported formats: JPEG, PNG, GIF, WebP, SVG, BMP, TIFF (max 20MB)"
    )
    slug = models.SlugField(
        max_length=250, 
        blank=True,
        help_text="URL-friendly version of the folder name"
    )
    display_order = models.IntegerField(
        default=0,
        help_text="Order for displaying folders in portfolio (lower values appear first)"
    )
    
    class Meta:
        ordering = ['display_order', '-updated_at', '-created_at']
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
                           storage=s3_storage if settings.USE_S3 else None,
                           validators=[validate_image_file],
                           help_text="Supported formats: JPEG, PNG, GIF, WebP, SVG, BMP, TIFF (max 20MB)")
    created_at = models.DateTimeField(auto_now_add=True)
    version_notes = models.TextField(blank=True, help_text="Notes about changes in this version")
    
    # Copy of artwork metadata at time of version creation
    medium = models.CharField(max_length=100, blank=True)
    dimensions = models.CharField(max_length=100, blank=True)
    tags = models.CharField(max_length=200, blank=True)
    
    class Meta:
        unique_together = ['artwork', 'version_number']
        ordering = ['-version_number']
    
    @property
    def is_archived(self):
        """Check if this version is archived based on version_notes"""
        return self.version_notes and '[ARCHIVED:' in self.version_notes
    
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
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='artworks/', blank=True, null=True,
                           storage=s3_storage if settings.USE_S3 else None,
                           validators=[validate_image_file],
                           help_text="Supported formats: JPEG, PNG, GIF, WebP, SVG, BMP, TIFF (max 20MB)")  # Image file
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
    
    # Current version pointer - all image data should live in versions
    current_version = models.ForeignKey(
        'ArtWorkVersion',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='current_for',
        help_text="Points to the current active version of this artwork"
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
        
        # Automatically set this as the current version
        self.current_version = version
        self.save(update_fields=['current_version'])
        
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
    
    def get_current_version_number(self):
        """Get the current version number (latest version + 1, or 1 if no versions)"""
        latest_version = self.get_latest_version()
        return (latest_version.version_number + 1) if latest_version else 1
    
    def get_display_image_url(self):
        """Get the image URL for display, prioritizing current_version over legacy fields"""
        if self.current_version and self.current_version.image:
            return self.current_version.image.url
        elif self.image:
            return self.image.url
        elif self.image_url:
            return self.image_url
        return None
    
    def get_display_image(self):
        """Get the image object for display, prioritizing current_version"""
        if self.current_version and self.current_version.image:
            return self.current_version.image
        return self.image


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
    artwork_version = models.ForeignKey('ArtWorkVersion', on_delete=models.SET_NULL, 
                                      null=True, blank=True, related_name='critiques',
                                      help_text="The specific version of the artwork this critique was written for")
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
    
    def has_engagement(self):
        """
        Check if this critique has any engagement (replies or reactions from others).
        Returns True if the critique has replies or reactions from other users, False otherwise.
        Author's own reactions don't count as engagement for deletion purposes.
        """
        # Check for replies
        has_replies = self.replies.exists()
        
        # Check for reactions from other users (exclude author's own reactions)
        has_reactions_from_others = self.reactions.exclude(user=self.author).exists()
        
        return has_replies or has_reactions_from_others
    
    def get_engagement_summary(self):
        """
        Get a summary of engagement for this critique from other users.
        Returns a dictionary with reply and reaction counts (excluding author's own reactions).
        """
        reply_count = self.replies.count()
        reaction_count_from_others = self.reactions.exclude(user=self.author).count()
        
        return {
            'reply_count': reply_count,
            'reaction_count': reaction_count_from_others,
            'total_engagement': reply_count + reaction_count_from_others
        }
    
    def get_overall_score(self):
        """Return the overall average score as a single number for display purposes."""
        return self.get_average_score() or 0


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


class AchievementBadge(models.Model):
    """
    Model representing different achievement badges that users can earn.
    These are predefined achievements based on various activities and milestones.
    """
    CATEGORY_ARTWORK = 'artwork'
    CATEGORY_CRITIQUE = 'critique'
    CATEGORY_COMMUNITY = 'community'
    CATEGORY_MILESTONE = 'milestone'
    CATEGORY_SPECIAL = 'special'
    
    CATEGORY_CHOICES = [
        (CATEGORY_ARTWORK, 'Artwork'),
        (CATEGORY_CRITIQUE, 'Critique'),
        (CATEGORY_COMMUNITY, 'Community'),
        (CATEGORY_MILESTONE, 'Milestone'),
        (CATEGORY_SPECIAL, 'Special'),
    ]
    
    TIER_BRONZE = 'bronze'
    TIER_SILVER = 'silver'
    TIER_GOLD = 'gold'
    TIER_PLATINUM = 'platinum'
    
    TIER_CHOICES = [
        (TIER_BRONZE, 'Bronze'),
        (TIER_SILVER, 'Silver'),
        (TIER_GOLD, 'Gold'),
        (TIER_PLATINUM, 'Platinum'),
    ]
    
    name = models.CharField(max_length=100, unique=True, help_text="Name of the achievement badge")
    description = models.TextField(help_text="Description of what this badge represents")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, help_text="Category this badge belongs to")
    tier = models.CharField(max_length=20, choices=TIER_CHOICES, help_text="Tier/rarity of this badge")
    icon = models.CharField(max_length=50, help_text="Bootstrap icon class for this badge")
    color = models.CharField(max_length=20, help_text="CSS color class for this badge")
    
    # Criteria for earning this badge
    criteria_type = models.CharField(max_length=50, help_text="Type of criteria (e.g., 'artwork_count', 'karma_points')")
    criteria_value = models.IntegerField(help_text="Threshold value for earning this badge")
    
    # Badge visibility and availability
    is_active = models.BooleanField(default=True, help_text="Whether this badge can be earned")
    is_hidden = models.BooleanField(default=False, help_text="Whether this badge is visible to users")
    
    # Ordering and metadata
    sort_order = models.PositiveIntegerField(default=0, help_text="Display order for this badge")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['category', 'tier', 'sort_order']
        verbose_name = 'Achievement Badge'
        verbose_name_plural = 'Achievement Badges'
    
    def __str__(self):
        return f"{self.name} ({self.tier.title()})"


class UserAchievement(models.Model):
    """
    Model representing badges earned by users.
    Links users to their earned achievement badges with timestamps.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='achievements')
    badge = models.ForeignKey(AchievementBadge, on_delete=models.CASCADE, related_name='earned_by')
    earned_at = models.DateTimeField(auto_now_add=True)
    
    # Optional context about when/why the badge was earned
    context_data = models.JSONField(blank=True, null=True, help_text="Additional context about earning this badge")
    
    # Notification sent status
    notification_sent = models.BooleanField(default=False, help_text="Whether user was notified about earning this badge")
    
    class Meta:
        unique_together = ['user', 'badge']  # A user can only earn each badge once
        ordering = ['-earned_at']
        verbose_name = 'User Achievement'
        verbose_name_plural = 'User Achievements'
    
    def __str__(self):
        return f"{self.user.username} earned {self.badge.name}"


# Two-at-a-Time Critique Feed Models

class Tag(models.Model):
    """
    Model for critique tags that can be applied as quick feedback.
    Supports Pro/Con polarity for structured feedback.
    """
    PRO, CON = "PRO", "CON"
    POLARITY_CHOICES = [(PRO, "Pro"), (CON, "Con")]

    label = models.CharField(max_length=64, unique=True, help_text="The tag label (e.g., 'strong focal point', 'muddy values')")
    polarity = models.CharField(max_length=3, choices=POLARITY_CHOICES, help_text="Whether this is a positive (Pro) or constructive (Con) tag")
    category = models.CharField(max_length=32, blank=True, help_text="Category like 'composition', 'technique', 'concept'")
    is_system = models.BooleanField(default=False, help_text="System-provided tags vs user-created tags")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['polarity', 'category', 'label']
        verbose_name = 'Critique Tag'
        verbose_name_plural = 'Critique Tags'

    def __str__(self):
        return f"{self.polarity}:{self.label}"


class QuickCrit(models.Model):
    """
    Model for quick critiques that use tags and optional notes.
    Part of the two-at-a-time critique feed system.
    """
    artwork = models.ForeignKey(ArtWork, on_delete=models.CASCADE, related_name="quick_crits")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="quick_crits")
    note = models.TextField(blank=True, help_text="Optional detailed note from the critic")
    summary = models.TextField(blank=True, help_text="AI-generated summary if note is blank")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = 'Quick Critique'
        verbose_name_plural = 'Quick Critiques'

    def __str__(self):
        return f"Quick critique by {self.author.username} on {self.artwork.title}"


class QuickCritTag(models.Model):
    """
    Junction table linking quick critiques to their tags.
    """
    quickcrit = models.ForeignKey(QuickCrit, on_delete=models.CASCADE, related_name="qc_tags")
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE, related_name="quick_crits")
    
    class Meta:
        unique_together = ("quickcrit", "tag")
        verbose_name = 'Quick Critique Tag'
        verbose_name_plural = 'Quick Critique Tags'

    def __str__(self):
        return f"{self.tag.label} on {self.quickcrit.artwork.title}"


class PairSession(models.Model):
    """
    Model to track which artwork pairs a user has seen to avoid immediate repeats.
    Helps create better user experience in the two-at-a-time feed.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="pair_sessions")
    spotlight = models.ForeignKey(ArtWork, on_delete=models.CASCADE, related_name="spotlight_sessions")
    counter = models.ForeignKey(ArtWork, on_delete=models.CASCADE, related_name="counter_sessions")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = 'Pair Session'
        verbose_name_plural = 'Pair Sessions'

    def __str__(self):
        return f"{self.user.username} saw {self.spotlight.title} + {self.counter.title}"
