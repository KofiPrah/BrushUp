from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from django.contrib.auth.models import User
from critique.models import ArtWork, Review, Profile
from .serializers import (
    UserSerializer, ProfileSerializer, ProfileUpdateSerializer, ArtWorkSerializer, 
    ArtWorkListSerializer, ReviewSerializer
)
from .permissions import IsAuthorOrReadOnly, IsOwnerOrReadOnly
from django.db import connection

class ProfileViewSet(viewsets.ModelViewSet):
    """API endpoint for managing user profiles.
    
    This ViewSet provides endpoints for:
    - GET /api/profiles/ - List all profiles (staff only)
    - GET /api/profiles/{id}/ - Get profile by ID (staff or owner)
    - GET /api/profiles/me/ - Get current user's profile
    - PUT/PATCH /api/profiles/me/ - Update current user's profile
    """
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Users can only update their own profile."""
        if self.request.user.is_staff:
            return Profile.objects.all()
        return Profile.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        """Return different serializers based on action."""
        if self.action in ['update', 'partial_update', 'update_me']:
            return ProfileUpdateSerializer
        return ProfileSerializer
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get the current user's profile."""
        profile = Profile.objects.get(user=request.user)
        serializer = self.get_serializer(profile)
        return Response(serializer.data)
    
    @action(detail=False, methods=['put', 'patch'])
    def update_me(self, request):
        """Update the current user's profile."""
        profile = Profile.objects.get(user=request.user)
        
        # Use partial=True for PATCH requests
        partial = request.method == 'PATCH'
        serializer = self.get_serializer(profile, data=request.data, partial=partial)
        
        if serializer.is_valid():
            serializer.save()
            # Get updated profile with standard serializer for response
            response_serializer = ProfileSerializer(profile)
            return Response(response_serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    def check_object_permissions(self, request, obj):
        """Ensure users can only access their own profiles unless staff."""
        if not request.user.is_staff and obj.user != request.user:
            self.permission_denied(request, message="You can only access your own profile.")
        return super().check_object_permissions(request, obj)

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for viewing users."""
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    
    def get_permissions(self):
        """Allow anonymous users to see the list, but require authentication for detail."""
        if self.action == 'list':
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
        
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get the current user's details."""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

class ArtWorkViewSet(viewsets.ModelViewSet):
    """API endpoint for viewing and editing artworks.
    
    Allows list, retrieve, create, update, and delete operations on artworks.
    Only authenticated users can create artworks, and only the artwork's author 
    (or admins) can update or delete it.
    """
    queryset = ArtWork.objects.all().order_by('-created_at')
    serializer_class = ArtWorkSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'tags', 'author__username']
    ordering_fields = ['created_at', 'updated_at', 'title']
    
    def get_serializer_class(self):
        """Return different serializers for list and detail views."""
        if self.action == 'list':
            return ArtWorkListSerializer
        return ArtWorkSerializer
    
    def get_serializer_context(self):
        """Add the request to the serializer context."""
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context
        
    def perform_create(self, serializer):
        """Set the author to the current user when creating an artwork."""
        serializer.save(author=self.request.user)
        
    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        """Toggle like status for the current user on this artwork."""
        artwork = self.get_object()
        user = request.user
        
        if artwork.likes.filter(id=user.id).exists():
            # User already liked this artwork, so unlike it
            artwork.likes.remove(user)
            return Response({'status': 'unliked'})
        else:
            # User hasn't liked this artwork, so like it
            artwork.likes.add(user)
            return Response({'status': 'liked'})
            
    @action(detail=True, methods=['get'])
    def reviews(self, request, pk=None):
        """Get all reviews for this artwork."""
        artwork = self.get_object()
        reviews = artwork.reviews.all().order_by('-created_at')
        
        page = self.paginate_queryset(reviews)
        if page is not None:
            serializer = ReviewSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
            
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)
        
    @action(detail=False, methods=['get'])
    def by_tag(self, request):
        """
        Filter artworks by tag.
        
        Example: /api/artworks/by_tag/?tag=landscape
        """
        tag = request.query_params.get('tag', None)
        if not tag:
            return Response(
                {"error": "Tag parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Look for tag in the comma-separated tags field
        artworks = self.get_queryset().filter(tags__contains=tag)
        
        page = self.paginate_queryset(artworks)
        if page is not None:
            serializer = ArtWorkListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
            
        serializer = ArtWorkListSerializer(artworks, many=True)
        return Response(serializer.data)
        
    @action(detail=False, methods=['get'])
    def popular(self, request):
        """
        Get popular artworks based on the number of likes.
        
        Example: /api/artworks/popular/
        """
        # Annotate the queryset with the count of likes
        from django.db.models import Count
        artworks = self.get_queryset().annotate(
            like_count=Count('likes')
        ).order_by('-like_count')
        
        # Get limit from query params, default to 10
        limit = request.query_params.get('limit', 10)
        try:
            limit = int(limit)
            if limit <= 0:
                limit = 10
        except ValueError:
            limit = 10
            
        artworks = artworks[:limit]
        
        page = self.paginate_queryset(artworks)
        if page is not None:
            serializer = ArtWorkListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
            
        serializer = ArtWorkListSerializer(artworks, many=True)
        return Response(serializer.data)
        
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """
        Get recently added artworks.
        
        Example: /api/artworks/recent/?limit=5
        """
        artworks = self.get_queryset().order_by('-created_at')
        
        # Get limit from query params, default to 10
        limit = request.query_params.get('limit', 10)
        try:
            limit = int(limit)
            if limit <= 0:
                limit = 10
        except ValueError:
            limit = 10
            
        artworks = artworks[:limit]
        
        page = self.paginate_queryset(artworks)
        if page is not None:
            serializer = ArtWorkListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
            
        serializer = ArtWorkListSerializer(artworks, many=True)
        return Response(serializer.data)
        
    @action(detail=False, methods=['get'])
    def user_artworks(self, request):
        """
        Get all artworks created by a specific user.
        
        Example: /api/artworks/user_artworks/?user_id=1
        """
        user_id = request.query_params.get('user_id', None)
        if not user_id:
            return Response(
                {"error": "user_id parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            # Check if user exists
            User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response(
                {"error": f"User with ID {user_id} does not exist"},
                status=status.HTTP_404_NOT_FOUND
            )
            
        artworks = self.get_queryset().filter(author_id=user_id).order_by('-created_at')
        
        page = self.paginate_queryset(artworks)
        if page is not None:
            serializer = ArtWorkListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
            
        serializer = ArtWorkListSerializer(artworks, many=True)
        return Response(serializer.data)

class ReviewViewSet(viewsets.ModelViewSet):
    """API endpoint for viewing and editing reviews.
    
    Allows list, retrieve, create, update, and delete operations on reviews.
    Only authenticated users can create reviews, and only the review's author 
    (or admins) can update or delete it.
    """
    queryset = Review.objects.all().order_by('-created_at')
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at', 'rating']
    
    def get_queryset(self):
        """Optionally filter reviews by artwork ID."""
        queryset = Review.objects.all().order_by('-created_at')
        artwork_id = self.request.query_params.get('artwork', None)
        if artwork_id is not None:
            queryset = queryset.filter(artwork_id=artwork_id)
        return queryset
    
    def get_serializer_context(self):
        """Add the request to the serializer context."""
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context
        
    def perform_create(self, serializer):
        """Set the reviewer to the current user when creating a review."""
        serializer.save(reviewer=self.request.user)


@api_view(['GET'])
def health_check(request):
    """
    API endpoint for health checking the service.
    Returns information about the API status and database connection.
    """
    # Check database connection
    db_status = "OK"
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
    except Exception as e:
        db_status = f"ERROR: {str(e)}"
    
    # Count objects in the database
    try:
        artwork_count = ArtWork.objects.count()
        review_count = Review.objects.count()
        user_count = User.objects.count()
    except Exception as e:
        artwork_count = review_count = user_count = f"ERROR: {str(e)}"
    
    # Compile response data
    data = {
        "status": "healthy",
        "api_version": "1.0.0",
        "database": {
            "status": db_status,
            "counts": {
                "artworks": artwork_count,
                "reviews": review_count,
                "users": user_count,
            }
        },
        "message": "Art Critique API is running"
    }
    
    return Response(data, status=status.HTTP_200_OK)