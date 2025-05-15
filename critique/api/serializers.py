from rest_framework import serializers
from django.contrib.auth.models import User
from critique.models import ArtWork, Review, Profile

class ProfileSerializer(serializers.ModelSerializer):
    """Serializer for the user Profile model."""
    
    class Meta:
        model = Profile
        fields = ['id', 'bio', 'location', 'profile_picture', 'website', 'birth_date']
        read_only_fields = ['id']

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
    is_liked = serializers.SerializerMethodField()
    
    class Meta:
        model = ArtWork
        fields = [
            'id', 'title', 'description', 'image', 'created_at', 'updated_at',
            'author', 'medium', 'dimensions', 'tags', 'likes_count', 'reviews_count', 'is_liked'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'author', 'likes_count', 'reviews_count', 'is_liked']
    
    def get_likes_count(self, obj):
        """Return the number of likes for this artwork."""
        return obj.likes.count()
    
    def get_reviews_count(self, obj):
        """Return the number of reviews for this artwork."""
        return obj.reviews.count()
    
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
    
    class Meta:
        model = ArtWork
        fields = ['id', 'title', 'image', 'author_name', 'created_at', 'medium', 'likes_count', 'reviews_count', 'tags_list']
        
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