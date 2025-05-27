from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from critique.models import ArtWork, Profile, Critique, Notification, Reaction, CritiqueReply, Folder
from critique.api.missing_image_handler import get_image_url

class ProfileSerializer(serializers.ModelSerializer):
    """Serializer for the user Profile model."""
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    profile_picture_display_url = serializers.SerializerMethodField()
    unread_notifications_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Profile
        fields = ['id', 'username', 'email', 'bio', 'location', 'profile_picture', 
                 'profile_picture_url', 'profile_picture_display_url', 'website', 'birth_date',
                 'karma', 'unread_notifications_count']
        read_only_fields = ['id', 'username', 'email', 'profile_picture_display_url', 
                           'karma', 'unread_notifications_count']
        
    def get_profile_picture_display_url(self, obj):
        """Return the URL to display the profile picture, prioritizing S3 storage."""
        if obj.profile_picture and hasattr(obj.profile_picture, 'url'):
            return obj.profile_picture.url
        return obj.profile_picture_url
        
    def get_unread_notifications_count(self, obj):
        """Return the count of unread notifications for the user."""
        from critique.models import Notification
        return Notification.objects.filter(recipient=obj.user, is_read=False).count()
        
class ProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile information."""
    first_name = serializers.CharField(source='user.first_name', required=False)
    last_name = serializers.CharField(source='user.last_name', required=False)
    profile_picture_display_url = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Profile
        fields = ['bio', 'location', 'profile_picture', 'profile_picture_url', 
                 'profile_picture_display_url', 'website', 'birth_date', 
                 'first_name', 'last_name']
                 
    def get_profile_picture_display_url(self, obj):
        """Return the URL to display the profile picture, prioritizing S3 storage."""
        if obj.profile_picture and hasattr(obj.profile_picture, 'url'):
            return obj.profile_picture.url
        return obj.profile_picture_url
        
    def update(self, instance, validated_data):
        """Update the User and Profile models."""
        user_data = validated_data.pop('user', {})
        
        # Update User fields
        user = instance.user
        if 'first_name' in user_data:
            user.first_name = user_data['first_name']
        if 'last_name' in user_data:
            user.last_name = user_data['last_name']
        user.save()
        
        # Update Profile fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        return instance

class UserSerializer(serializers.ModelSerializer):
    """Serializer for the User model with profile information."""
    profile = ProfileSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'profile', 'is_staff', 'date_joined', 'last_login']
        read_only_fields = ['id', 'is_staff', 'date_joined', 'last_login']
        
class UserProfileSerializer(serializers.ModelSerializer):
    """Enhanced serializer for the User model with extra authentication information."""
    profile = ProfileSerializer(read_only=True)
    auth_info = serializers.SerializerMethodField()
    karma = serializers.SerializerMethodField()
    unread_notifications_count = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'profile', 
                 'auth_info', 'karma', 'unread_notifications_count']
        read_only_fields = ['id', 'karma', 'unread_notifications_count']
        
    def get_auth_info(self, obj):
        """Return authentication-related information."""
        return {
            'is_authenticated': True,
            'is_staff': obj.is_staff,
            'is_superuser': obj.is_superuser,
            'date_joined': obj.date_joined,
            'last_login': obj.last_login,
        }
        
    def get_karma(self, obj):
        """Return the user's karma score."""
        if hasattr(obj, 'profile'):
            return obj.profile.karma
        return 0
        
    def get_unread_notifications_count(self, obj):
        """Return the count of unread notifications for the user."""
        from critique.models import Notification
        return Notification.objects.filter(recipient=obj, is_read=False).count()

class ArtWorkSerializer(serializers.ModelSerializer):
    """Serializer for the ArtWork model with author information and folder assignment."""
    author = UserSerializer(read_only=True)
    likes_count = serializers.SerializerMethodField()
    critiques_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    image_display_url = serializers.SerializerMethodField()
    critiques = serializers.SerializerMethodField()
    folder_name = serializers.CharField(source='folder.name', read_only=True)
    folder_slug = serializers.CharField(source='folder.slug', read_only=True)
    
    class Meta:
        model = ArtWork
        fields = [
            'id', 'title', 'description', 'image', 'image_url', 'image_display_url',
            'created_at', 'updated_at', 'author', 'medium', 'dimensions', 'tags', 
            'folder', 'folder_name', 'folder_slug',
            'likes_count', 'critiques_count', 'is_liked', 'critiques'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'author', 
                           'likes_count', 'critiques_count', 
                           'is_liked', 'image_display_url', 'critiques',
                           'folder_name', 'folder_slug']
                           
    def get_image_display_url(self, obj):
        """Return the URL to display the image, prioritizing S3 storage."""
        if obj.image and hasattr(obj.image, 'url'):
            return obj.image.url
        return obj.image_url
    
    def get_likes_count(self, obj):
        """Return the number of likes for this artwork."""
        return obj.likes.count()
    
        
    def get_critiques_count(self, obj):
        """Return the number of critiques for this artwork."""
        return obj.critiques.count()
    
    def get_critiques(self, obj):
        """Return the critiques for this artwork."""
        # For detail view, include critiques with the artwork
        if self.context.get('view') and self.context['view'].action == 'retrieve':
            critiques = obj.critiques.all().order_by('-created_at')[:5]  # Limit to the 5 most recent critiques
            from .serializers import CritiqueListSerializer
            return CritiqueListSerializer(critiques, many=True, context=self.context).data
        return None
    
    def get_is_liked(self, obj):
        """Return whether the current user has liked this artwork."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(id=request.user.id).exists()
        return False
    
    def validate_folder(self, value):
        """Validate that the user can only assign artwork to their own folders."""
        if value is not None:
            request = self.context.get('request')
            if request and hasattr(request, 'user') and request.user.is_authenticated:
                if value.owner != request.user:
                    raise serializers.ValidationError(
                        "You can only assign artworks to your own folders."
                    )
        return value
    
    def create(self, validated_data):
        """Create a new artwork with the current user as author."""
        # Author is now being set in the view via perform_create method
        # so we don't need to set it here to avoid the duplicate argument error
        artwork = ArtWork.objects.create(**validated_data)
        return artwork
    
    def update(self, instance, validated_data):
        """Update artwork, ensuring folder assignment validation."""
        # Additional check: ensure the artwork being updated belongs to the current user
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            if instance.author != request.user:
                raise serializers.ValidationError(
                    "You can only modify your own artworks."
                )
        return super().update(instance, validated_data)

class ArtWorkListSerializer(serializers.ModelSerializer):
    """Simplified serializer for listing artwork."""
    author_name = serializers.CharField(source='author.username', read_only=True)
    likes_count = serializers.SerializerMethodField()

    tags_list = serializers.SerializerMethodField()
    image_display_url = serializers.SerializerMethodField()
    
    class Meta:
        model = ArtWork
        fields = ['id', 'title', 'image_display_url', 'author_name', 'created_at', 
                 'medium', 'likes_count', 'tags_list']
                 
    def get_image_display_url(self, obj):
        """Return the URL to display the image, prioritizing S3 storage."""
        if obj.image and hasattr(obj.image, 'url'):
            return obj.image.url
        return obj.image_url
        
    def get_likes_count(self, obj):
        """Return the number of likes for this artwork."""
        return obj.likes.count()
    
    def get_tags_list(self, obj):
        """Return the tags as a list."""
        if not obj.tags:
            return []
        return [tag.strip() for tag in obj.tags.split(',') if tag.strip()]



class CritiqueReplySerializer(serializers.ModelSerializer):
    """Serializer for artist replies to critiques."""
    author = UserSerializer(read_only=True)
    author_name = serializers.CharField(source='author.username', read_only=True)
    
    class Meta:
        model = CritiqueReply
        fields = ['id', 'critique', 'author', 'author_name', 'text', 'created_at', 'updated_at']
        read_only_fields = ['id', 'author', 'author_name', 'created_at', 'updated_at']


class CritiqueSerializer(serializers.ModelSerializer):
    """Serializer for the Critique model with author information."""
    author = UserSerializer(read_only=True)
    author_name = serializers.CharField(source='author.username', read_only=True)
    author_profile_url = serializers.SerializerMethodField()
    artwork_title = serializers.CharField(source='artwork.title', read_only=True)
    average_score = serializers.SerializerMethodField()
    reactions_count = serializers.SerializerMethodField()
    helpful_count = serializers.SerializerMethodField()
    inspiring_count = serializers.SerializerMethodField()
    detailed_count = serializers.SerializerMethodField()
    user_reactions = serializers.SerializerMethodField()
    replies = CritiqueReplySerializer(many=True, read_only=True)
    is_hidden_from_public = serializers.BooleanField(source='is_hidden', read_only=True)
    can_hide = serializers.SerializerMethodField()
    can_reply = serializers.SerializerMethodField()
    hidden_reason = serializers.CharField(read_only=True)
    is_flagged = serializers.BooleanField(read_only=True)
    
    def get_reactions_count(self, obj):
        """Return the total count of all reactions for this critique."""
        return {
            'HELPFUL': obj.reactions.filter(reaction_type='HELPFUL').count(),
            'INSPIRING': obj.reactions.filter(reaction_type='INSPIRING').count(),
            'DETAILED': obj.reactions.filter(reaction_type='DETAILED').count(),
            'TOTAL': obj.reactions.count()
        }
    
    def get_can_hide(self, obj):
        """Return true if the current user can hide this critique (artwork owner)."""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return obj.artwork.author == request.user
    
    def get_can_reply(self, obj):
        """Return true if the current user can reply to this critique (artwork owner)."""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return obj.artwork.author == request.user
    
    class Meta:
        model = Critique
        fields = [
            'id', 'artwork', 'artwork_title', 'author', 'author_name', 
            'author_profile_url', 'text', 'composition_score', 'technique_score', 
            'originality_score', 'average_score', 'reactions_count',
            'helpful_count', 'inspiring_count', 'detailed_count', 'user_reactions',
            'created_at', 'updated_at', 'replies', 'is_hidden_from_public', 'hidden_reason',
            'is_flagged', 'can_hide', 'can_reply'
        ]
        read_only_fields = [
            'id', 'author', 'author_name', 'author_profile_url', 
            'artwork_title', 'average_score', 'reactions_count',
            'helpful_count', 'inspiring_count', 'detailed_count', 'user_reactions',
            'created_at', 'updated_at', 'replies', 'is_hidden_from_public', 
            'hidden_reason', 'is_flagged', 'can_hide', 'can_reply'
        ]
    
    def get_author_profile_url(self, obj):
        """Return a URL to the author's profile."""
        return f"/profile/{obj.author.id}/"
    
    def get_average_score(self, obj):
        """Return the average score for this critique."""
        return obj.get_average_score()
        
    def get_helpful_count(self, obj):
        """Return the count of HELPFUL reactions for this critique."""
        return obj.reactions.filter(reaction_type='HELPFUL').count()
        
    def get_inspiring_count(self, obj):
        """Return the count of INSPIRING reactions for this critique."""
        return obj.reactions.filter(reaction_type='INSPIRING').count()
        
    def get_detailed_count(self, obj):
        """Return the count of DETAILED reactions for this critique."""
        return obj.reactions.filter(reaction_type='DETAILED').count()
        
    def get_user_reactions(self, obj):
        """Return a list of reaction types the current user has given to this critique."""
        user = self.context.get('request').user
        if not user or user.is_anonymous:
            return []
            
        return list(obj.reactions.filter(user=user).values_list('reaction_type', flat=True))
    
    def create(self, validated_data):
        """Create a new critique with the current user as author."""
        # Author is set in the view's perform_create method
        # This prevents the "multiple values for keyword argument 'author'" error
        critique = Critique.objects.create(**validated_data)
        return critique
        
class CritiqueListSerializer(serializers.ModelSerializer):
    """Simplified serializer for listing critiques."""
    author_name = serializers.CharField(source='author.username', read_only=True)
    artwork_title = serializers.CharField(source='artwork.title', read_only=True)
    average_score = serializers.SerializerMethodField()
    reactions_count = serializers.SerializerMethodField()
    helpful_count = serializers.SerializerMethodField()
    inspiring_count = serializers.SerializerMethodField()
    detailed_count = serializers.SerializerMethodField()
    user_reactions = serializers.SerializerMethodField()
    is_hidden_from_public = serializers.BooleanField(source='is_hidden', read_only=True)
    can_hide = serializers.SerializerMethodField()
    can_reply = serializers.SerializerMethodField()
    has_replies = serializers.SerializerMethodField()
    
    def get_reactions_count(self, obj):
        """Return the total count of all reactions for this critique."""
        return {
            'HELPFUL': obj.reactions.filter(reaction_type='HELPFUL').count(),
            'INSPIRING': obj.reactions.filter(reaction_type='INSPIRING').count(),
            'DETAILED': obj.reactions.filter(reaction_type='DETAILED').count(),
            'TOTAL': obj.reactions.count()
        }
    
    def get_can_hide(self, obj):
        """Return true if the current user can hide this critique (artwork owner)."""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return obj.artwork.author == request.user
    
    def get_can_reply(self, obj):
        """Return true if the current user can reply to this critique (artwork owner)."""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return obj.artwork.author == request.user
    
    def get_has_replies(self, obj):
        """Return true if this critique has any replies."""
        return obj.replies.exists()
    
    class Meta:
        model = Critique
        fields = [
            'id', 'artwork', 'artwork_title', 'author_name', 
            'text', 'average_score', 'reactions_count', 
            'helpful_count', 'inspiring_count', 'detailed_count',
            'user_reactions', 'created_at', 'is_hidden_from_public',
            'can_hide', 'can_reply', 'has_replies'
        ]
    
    def get_average_score(self, obj):
        """Return the average score for this critique."""
        return obj.get_average_score()
        
    def get_helpful_count(self, obj):
        """Return the count of HELPFUL reactions for this critique."""
        return obj.reactions.filter(reaction_type='HELPFUL').count()
        
    def get_inspiring_count(self, obj):
        """Return the count of INSPIRING reactions for this critique."""
        return obj.reactions.filter(reaction_type='INSPIRING').count()
        
    def get_detailed_count(self, obj):
        """Return the count of DETAILED reactions for this critique."""
        return obj.reactions.filter(reaction_type='DETAILED').count()
        
    def get_user_reactions(self, obj):
        """Return a list of reaction types the current user has given to this critique."""
        user = self.context.get('request').user
        if not user or user.is_anonymous:
            return []
            
        return list(obj.reactions.filter(user=user).values_list('reaction_type', flat=True))
        
        
class ReactionSerializer(serializers.ModelSerializer):
    """Serializer for the Reaction model."""
    user = UserSerializer(read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    critique_id = serializers.PrimaryKeyRelatedField(
        source='critique',
        queryset=Critique.objects.all()
    )
    
    class Meta:
        model = Reaction
        fields = [
            'id', 'critique_id', 'user', 'username', 
            'reaction_type', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'username', 'created_at']
    
    def validate(self, data):
        """
        Check that the user hasn't already given this type of reaction to this critique.
        This is in addition to the model constraint, to provide a better error message.
        """
        user = self.context['request'].user
        critique = data['critique']
        reaction_type = data['reaction_type']
        
        # Check if user already gave this reaction type to this critique
        existing = Reaction.objects.filter(
            user=user,
            critique=critique,
            reaction_type=reaction_type
        ).exists()
        
        if existing:
            raise serializers.ValidationError(
                f"You have already given a {reaction_type} reaction to this critique."
            )
        
        return data
    
    def create(self, validated_data):
        """Create a new reaction with the current user."""
        user = self.context['request'].user
        return Reaction.objects.create(user=user, **validated_data)


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for Notification objects."""
    recipient_username = serializers.ReadOnlyField(source='recipient.username')
    target_type = serializers.SerializerMethodField()
    target_id = serializers.SerializerMethodField()
    target_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Notification
        fields = [
            'id', 'recipient', 'recipient_username', 'message', 
            'target_type', 'target_id', 'target_display', 'url',
            'created_at', 'is_read'
        ]
        read_only_fields = ['id', 'recipient', 'recipient_username', 'created_at']
    
    def get_target_type(self, obj):
        """Get the target content type name if available."""
        if obj.target_content_type:
            return obj.target_content_type.model
        return None
    
    def get_target_id(self, obj):
        """Get the target object ID if available."""
        return obj.target_object_id
    
    def get_target_display(self, obj):
        """Get a human-readable representation of the target."""
        if not obj.target:
            return None
            
        # Handle different types of target objects
        if isinstance(obj.target, ArtWork):
            return f"Artwork: {obj.target.title}"
        elif isinstance(obj.target, Critique):
            return f"Critique on: {obj.target.artwork.title}"
        elif isinstance(obj.target, Reaction):
            return f"Reaction on critique for: {obj.target.critique.artwork.title}"
        elif isinstance(obj.target, User):
            return f"User: {obj.target.username}"
        
        # Default fallback
        return str(obj.target)

# ============================================================================
# FOLDER SERIALIZERS FOR PORTFOLIO MANAGEMENT
# ============================================================================

class FolderSerializer(serializers.ModelSerializer):
    """Complete serializer for Folder model with portfolio management features."""
    owner_username = serializers.CharField(source='owner.username', read_only=True)
    artwork_count = serializers.SerializerMethodField()
    cover_image_url = serializers.SerializerMethodField()
    can_edit = serializers.SerializerMethodField()
    can_delete = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()
    artworks = serializers.SerializerMethodField()
    
    class Meta:
        model = Folder
        fields = [
            'id', 'name', 'description', 'owner', 'owner_username', 
            'is_public', 'created_at', 'updated_at', 'cover_image', 
            'cover_image_url', 'slug', 'artwork_count', 'can_edit', 
            'can_delete', 'url', 'artworks'
        ]
        read_only_fields = ['id', 'owner', 'owner_username', 'created_at', 
                           'updated_at', 'slug', 'artwork_count', 'can_edit', 
                           'can_delete', 'url', 'cover_image_url', 'artworks']
    
    def get_artwork_count(self, obj):
        """Return the number of artworks in this folder."""
        return obj.artwork_count()
    
    def get_cover_image_url(self, obj):
        """Return the URL for the folder's cover image."""
        if obj.cover_image and hasattr(obj.cover_image, 'url'):
            return obj.cover_image.url
        return None
    
    def get_can_edit(self, obj):
        """Check if the current user can edit this folder."""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return obj.owner == request.user
    
    def get_can_delete(self, obj):
        """Check if the current user can delete this folder."""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return obj.owner == request.user
    
    def get_url(self, obj):
        """Return the URL for this folder."""
        return obj.get_absolute_url()
    
    def get_artworks(self, obj):
        """Return the artworks in this folder."""
        # Use ArtWorkListSerializer to avoid circular imports and provide efficient listing
        artworks = obj.artworks.all().order_by('-created_at')
        return ArtWorkListSerializer(artworks, many=True, context=self.context).data

class FolderListSerializer(serializers.ModelSerializer):
    """Simplified serializer for listing folders in portfolios."""
    owner_username = serializers.CharField(source='owner.username', read_only=True)
    artwork_count = serializers.SerializerMethodField()
    cover_image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Folder
        fields = [
            'id', 'name', 'description', 'owner_username', 'is_public', 
            'created_at', 'slug', 'artwork_count', 'cover_image_url'
        ]
        read_only_fields = ['id', 'owner_username', 'created_at', 'slug', 
                           'artwork_count', 'cover_image_url']
    
    def get_artwork_count(self, obj):
        """Return the number of artworks in this folder."""
        return obj.artwork_count()
    
    def get_cover_image_url(self, obj):
        """Return the URL for the folder's cover image."""
        if obj.cover_image and hasattr(obj.cover_image, 'url'):
            return obj.cover_image.url
        return None

class FolderCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating folders."""
    
    class Meta:
        model = Folder
        fields = ['name', 'description', 'is_public', 'cover_image']
    
    def validate_name(self, value):
        """Validate that the folder name is not empty and reasonable length."""
        if not value or not value.strip():
            raise serializers.ValidationError("Folder name cannot be empty.")
        if len(value.strip()) > 200:
            raise serializers.ValidationError("Folder name cannot exceed 200 characters.")
        return value.strip()