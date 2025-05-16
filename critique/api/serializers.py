from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from critique.models import ArtWork, Review, Profile, Critique, Notification, Reaction

class ProfileSerializer(serializers.ModelSerializer):
    """Serializer for the user Profile model."""
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    profile_picture_display_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Profile
        fields = ['id', 'username', 'email', 'bio', 'location', 'profile_picture', 
                 'profile_picture_url', 'profile_picture_display_url', 'website', 'birth_date']
        read_only_fields = ['id', 'username', 'email', 'profile_picture_display_url']
        
    def get_profile_picture_display_url(self, obj):
        """Return the URL to display the profile picture, prioritizing S3 storage."""
        if obj.profile_picture and hasattr(obj.profile_picture, 'url'):
            return obj.profile_picture.url
        return obj.profile_picture_url
        
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
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'profile', 'auth_info']
        read_only_fields = ['id']
        
    def get_auth_info(self, obj):
        """Return authentication-related information."""
        return {
            'is_authenticated': True,
            'is_staff': obj.is_staff,
            'is_superuser': obj.is_superuser,
            'date_joined': obj.date_joined,
            'last_login': obj.last_login,
        }

class ArtWorkSerializer(serializers.ModelSerializer):
    """Serializer for the ArtWork model with author information."""
    author = UserSerializer(read_only=True)
    likes_count = serializers.SerializerMethodField()
    reviews_count = serializers.SerializerMethodField()
    critiques_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    image_display_url = serializers.SerializerMethodField()
    critiques = serializers.SerializerMethodField()
    
    class Meta:
        model = ArtWork
        fields = [
            'id', 'title', 'description', 'image', 'image_url', 'image_display_url',
            'created_at', 'updated_at', 'author', 'medium', 'dimensions', 'tags', 
            'likes_count', 'reviews_count', 'critiques_count', 'is_liked', 'critiques'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'author', 
                           'likes_count', 'reviews_count', 'critiques_count', 
                           'is_liked', 'image_display_url', 'critiques']
                           
    def get_image_display_url(self, obj):
        """Return the URL to display the image, prioritizing S3 storage."""
        if obj.image and hasattr(obj.image, 'url'):
            return obj.image.url
        return obj.image_url
    
    def get_likes_count(self, obj):
        """Return the number of likes for this artwork."""
        return obj.likes.count()
    
    def get_reviews_count(self, obj):
        """Return the number of reviews for this artwork."""
        return obj.reviews.count()
        
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
    
    def create(self, validated_data):
        """Create a new artwork with the current user as author."""
        user = self.context['request'].user
        artwork = ArtWork.objects.create(author=user, **validated_data)
        return artwork

class ArtWorkListSerializer(serializers.ModelSerializer):
    """Simplified serializer for listing artwork."""
    author_name = serializers.CharField(source='author.username', read_only=True)
    likes_count = serializers.SerializerMethodField()
    reviews_count = serializers.SerializerMethodField()
    tags_list = serializers.SerializerMethodField()
    image_display_url = serializers.SerializerMethodField()
    
    class Meta:
        model = ArtWork
        fields = ['id', 'title', 'image_display_url', 'author_name', 'created_at', 
                 'medium', 'likes_count', 'reviews_count', 'tags_list']
                 
    def get_image_display_url(self, obj):
        """Return the URL to display the image, prioritizing S3 storage."""
        if obj.image and hasattr(obj.image, 'url'):
            return obj.image.url
        return obj.image_url
        
    def get_likes_count(self, obj):
        """Return the number of likes for this artwork."""
        return obj.likes.count()
    
    def get_reviews_count(self, obj):
        """Return the number of reviews for this artwork."""
        return obj.reviews.count()
        
    def get_tags_list(self, obj):
        """Return the tags as a list."""
        if not obj.tags:
            return []
        return [tag.strip() for tag in obj.tags.split(',') if tag.strip()]

class ReviewSerializer(serializers.ModelSerializer):
    """Serializer for the Review model with reviewer information."""
    reviewer = UserSerializer(read_only=True)
    
    class Meta:
        model = Review
        fields = ['id', 'artwork', 'reviewer', 'content', 'rating', 'created_at']
        read_only_fields = ['id', 'reviewer', 'created_at']
    
    def create(self, validated_data):
        """Create a new review with the current user as reviewer."""
        user = self.context['request'].user
        review = Review.objects.create(reviewer=user, **validated_data)
        return review

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
    
    class Meta:
        model = Critique
        fields = [
            'id', 'artwork', 'artwork_title', 'author', 'author_name', 
            'author_profile_url', 'text', 'composition_score', 'technique_score', 
            'originality_score', 'average_score', 'reactions_count',
            'helpful_count', 'inspiring_count', 'detailed_count', 'user_reactions',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'author', 'author_name', 'author_profile_url', 
            'artwork_title', 'average_score', 'reactions_count',
            'helpful_count', 'inspiring_count', 'detailed_count', 'user_reactions',
            'created_at', 'updated_at'
        ]
    
    def get_author_profile_url(self, obj):
        """Return a URL to the author's profile."""
        return f"/profile/{obj.author.id}/"
    
    def get_average_score(self, obj):
        """Return the average score for this critique."""
        return obj.get_average_score()
        
    def get_helpful_count(self, obj):
        """Return the count of HELPFUL reactions for this critique."""
        return obj.reaction_set.filter(reaction_type='HELPFUL').count()
        
    def get_inspiring_count(self, obj):
        """Return the count of INSPIRING reactions for this critique."""
        return obj.reaction_set.filter(reaction_type='INSPIRING').count()
        
    def get_detailed_count(self, obj):
        """Return the count of DETAILED reactions for this critique."""
        return obj.reaction_set.filter(reaction_type='DETAILED').count()
        
    def get_user_reactions(self, obj):
        """Return a list of reaction types the current user has given to this critique."""
        user = self.context.get('request').user
        if not user or user.is_anonymous:
            return []
            
        return list(obj.reaction_set.filter(user=user).values_list('reaction_type', flat=True))
    
    def create(self, validated_data):
        """Create a new critique with the current user as author."""
        user = self.context['request'].user
        critique = Critique.objects.create(author=user, **validated_data)
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
    
    class Meta:
        model = Critique
        fields = [
            'id', 'artwork', 'artwork_title', 'author_name', 
            'text', 'average_score', 'reactions_count', 
            'helpful_count', 'inspiring_count', 'detailed_count',
            'user_reactions', 'created_at'
        ]
    
    def get_average_score(self, obj):
        """Return the average score for this critique."""
        return obj.get_average_score()
        
    def get_reactions_count(self, obj):
        """Return the count of reactions for this critique, grouped by type."""
        reactions_count = {
            'HELPFUL': obj.reaction_set.filter(reaction_type='HELPFUL').count(),
            'INSPIRING': obj.reaction_set.filter(reaction_type='INSPIRING').count(),
            'DETAILED': obj.reaction_set.filter(reaction_type='DETAILED').count(),
            'total': obj.reaction_set.count()
        }
        return reactions_count
        
    def get_helpful_count(self, obj):
        """Return the count of HELPFUL reactions for this critique."""
        return obj.reaction_set.filter(reaction_type='HELPFUL').count()
        
    def get_inspiring_count(self, obj):
        """Return the count of INSPIRING reactions for this critique."""
        return obj.reaction_set.filter(reaction_type='INSPIRING').count()
        
    def get_detailed_count(self, obj):
        """Return the count of DETAILED reactions for this critique."""
        return obj.reaction_set.filter(reaction_type='DETAILED').count()
        
    def get_user_reactions(self, obj):
        """Return a list of reaction types the current user has given to this critique."""
        user = self.context.get('request').user
        if not user or user.is_anonymous:
            return []
            
        return list(obj.reaction_set.filter(user=user).values_list('reaction_type', flat=True))
        
        
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
        elif isinstance(obj.target, Review):
            return f"Review on: {obj.target.artwork.title}"
        elif isinstance(obj.target, Reaction):
            return f"Reaction on critique for: {obj.target.critique.artwork.title}"
        elif isinstance(obj.target, User):
            return f"User: {obj.target.username}"
        
        # Default fallback
        return str(obj.target)