from rest_framework import viewsets, permissions, status, filters, parsers
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Max
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from critique.models import ArtWork, ArtWorkVersion, Profile, Critique, Reaction, Notification, CritiqueReply, Folder
from .serializers import (
    UserSerializer, ProfileSerializer, ProfileUpdateSerializer, ArtWorkSerializer, ArtWorkVersionSerializer,
    ArtWorkListSerializer, CritiqueSerializer, CritiqueListSerializer,
    ReactionSerializer, NotificationSerializer, CritiqueReplySerializer,
    FolderSerializer, FolderListSerializer, FolderCreateUpdateSerializer
)
from .permissions import (
    IsAuthorOrReadOnly, IsOwnerOrReadOnly, IsModeratorOrOwner, 
    IsModeratorOrAdmin, IsAdminOnly
)
from .filters import ArtWorkFilter, CritiqueFilter
from .pagination import CustomPageNumberPagination, InfiniteScrollPagination
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
    """API endpoint for viewing and editing artworks with comprehensive search and filtering.

    Allows list, retrieve, create, update, and delete operations on artworks.
    Only authenticated users can create artworks.

    Permissions:
    - Anyone can view artworks (GET)
    - Only authenticated users can create artworks (POST)
    - Only the artwork's author can update it (PUT/PATCH)
    - Only the artwork's author or users with MODERATOR/ADMIN role can delete it (DELETE)

    Search and Filtering:
    - Search: ?search=query (searches title, description, tags, author username)
    - Filter by author: ?author=user_id or ?author__username=username
    - Filter by medium: ?medium=acrylic
    - Filter by tags: ?tags=landscape
    - Filter by date: ?created_after=2024-01-01&created_before=2024-12-31
    - Filter by popularity: ?min_likes=5&min_critiques=3
    - Ordering: ?ordering=-created_at (prefix with - for descending)

    For image uploads:
    - POST to /api/artworks/ with multipart/form-data
    - Include 'image' field with the image file
    - Other fields (title, description, etc.) can be included in the same request
    """
    queryset = ArtWork.objects.all()
    serializer_class = ArtWorkSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = CustomPageNumberPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ArtWorkFilter
    search_fields = ['title', 'description', 'tags', 'author__username']
    ordering_fields = ['created_at', 'updated_at', 'title', 'likes_count', 'critiques_count', 'popularity_score']
    ordering = ['-created_at']  # Default ordering

    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = CustomPageNumberPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ArtWorkFilter
    search_fields = ['title', 'description', 'tags', 'author__username']
    ordering_fields = ['created_at', 'updated_at', 'title', 'likes_count', 'critiques_count', 'popularity_score']
    ordering = ['-created_at']  # Default ordering
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]

    def get_queryset(self):
        """Return queryset with popularity annotations and folder visibility filtering."""
        from django.db.models import Count, Q

        queryset = ArtWork.objects.annotate(
            critiques_count=Count('critiques', distinct=True),
            likes_count=Count('likes', distinct=True),
            # Calculate popularity score: critiques * 2 + likes + reactions
            popularity_score=Count('critiques', distinct=True) * 2 + 
                           Count('likes', distinct=True) + 
                           Count('critiques__reactions', distinct=True)
        ).order_by('-created_at')

        # Filter out artworks in private folders unless user is the folder owner
        user = self.request.user
        if user.is_authenticated:
            # Authenticated users see:
            # 1. Artworks not in any folder
            # 2. Artworks in public folders
            # 3. Artworks in their own folders (any visibility)
            # 4. Artworks in unlisted folders (direct access allowed)
            queryset = queryset.filter(
                Q(folder__isnull=True) |  # Not in any folder
                Q(folder__is_public=Folder.VISIBILITY_PUBLIC) |  # Public folders
                Q(folder__is_public=Folder.VISIBILITY_UNLISTED) |  # Unlisted folders
                Q(folder__owner=user)  # User's own folders
            )
        else:
            # Anonymous users only see:
            # 1. Artworks not in any folder
            # 2. Artworks in public folders
            queryset = queryset.filter(
                Q(folder__isnull=True) |  # Not in any folder
                Q(folder__is_public=Folder.VISIBILITY_PUBLIC)  # Public folders only
            )

        return queryset

    def retrieve(self, request, *args, **kwargs):
        """Override retrieve to enforce artwork and folder visibility rules."""
        artwork = self.get_object()

        # Check if artwork is in a folder and if user can view that folder
        if artwork.folder and not artwork.folder.is_viewable_by(request.user):
            return Response(
                {"detail": "Not found."},  # Don't reveal artwork exists
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = self.get_serializer(artwork)
        return Response(serializer.data)

    def get_permissions(self):
        """
        Return different permission classes based on the action:
        - create: IsAuthenticated
        - update/partial_update: IsAuthorOrReadOnly (only author can edit)
        - destroy: IsModeratorOrOwner (author or moderator/admin can delete)
        - default: IsAuthenticatedOrReadOnly
        """
        if self.action == 'destroy':
            permission_classes = [permissions.IsAuthenticated, IsModeratorOrOwner]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [permissions.IsAuthenticated, IsAuthorOrReadOnly]
        elif self.action == 'create':
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.IsAuthenticatedOrReadOnly]

        return [permission() for permission in permission_classes]

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

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def toggle_publish_status(self, request, pk=None):
        """Toggle the publish status of an artwork."""
        artwork = self.get_object()
        
        # Only the author can toggle publish status
        if artwork.author != request.user:
            return Response(
                {"detail": "You don't have permission to modify this artwork."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        artwork.is_published = not artwork.is_published
        artwork.save()
        
        return Response({
            "id": artwork.id,
            "is_published": artwork.is_published,
            "status": "published" if artwork.is_published else "draft"
        })

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def toggle_critique_request(self, request, pk=None):
        """Toggle the critique request status of an artwork."""
        artwork = self.get_object()
        
        # Only the author can toggle critique request status
        if artwork.author != request.user:
            return Response(
                {"detail": "You don't have permission to modify this artwork."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        artwork.seeking_critique = not artwork.seeking_critique
        artwork.save()
        
        return Response({
            "id": artwork.id,
            "seeking_critique": artwork.seeking_critique
        })

    @action(detail=True, methods=['patch'], permission_classes=[permissions.IsAuthenticated])
    def quick_edit(self, request, pk=None):
        """Quick edit artwork fields (title, description, tags)."""
        artwork = self.get_object()
        
        # Only the author can edit
        if artwork.author != request.user:
            return Response(
                {"detail": "You don't have permission to modify this artwork."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Allow updating only specific fields
        allowed_fields = ['title', 'description', 'tags']
        update_data = {k: v for k, v in request.data.items() if k in allowed_fields}
        
        serializer = self.get_serializer(artwork, data=update_data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def bulk_actions(self, request):
        """Perform bulk actions on multiple artworks."""
        artwork_ids = request.data.get('artwork_ids', [])
        action_type = request.data.get('action', '')
        
        if not artwork_ids:
            return Response(
                {"detail": "No artwork IDs provided."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Only get artworks owned by the current user
        artworks = ArtWork.objects.filter(
            id__in=artwork_ids,
            author=request.user
        )
        
        if action_type == 'publish':
            artworks.update(is_published=True)
        elif action_type == 'draft':
            artworks.update(is_published=False)
        elif action_type == 'toggle_critique':
            for artwork in artworks:
                artwork.seeking_critique = not artwork.seeking_critique
                artwork.save()
        elif action_type == 'delete':
            artworks.delete()
            return Response({"detail": f"Deleted {len(artwork_ids)} artworks."})
        else:
            return Response(
                {"detail": "Invalid action type."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response({
            "detail": f"Action '{action_type}' applied to {artworks.count()} artworks."
        })

    @action(detail=False, methods=['get'])
    def my_artworks(self, request):
        """Get the current user's artworks."""
        if not request.user.is_authenticated:
            return Response({'detail': 'Authentication required.'}, status=status.HTTP_401_UNAUTHORIZED)

        queryset = self.get_queryset().filter(author=request.user)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def search_by_author(self, request):
        """Search artworks by author username."""
        username = request.query_params.get('username', '')
        if not username:
            return Response({'detail': 'Username parameter is required.'}, status=status.HTTP_400_BAD_REQUEST)

        queryset = self.get_queryset().filter(author__username__icontains=username)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def infinite_scroll(self, request):
        """
        Specialized endpoint for infinite scroll functionality.

        Optimized for loading additional pages with minimal metadata
        for better performance in infinite scroll scenarios.

        Usage: /api/artworks/infinite_scroll/?page=2&search=landscape&medium=oil
        """
        # Temporarily use infinite scroll pagination
        self.pagination_class = InfiniteScrollPagination

        # Apply the same filtering as the main list
        queryset = self.filter_queryset(self.get_queryset())

        # Paginate the results
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        # Fallback if pagination is disabled
        serializer = self.get_serializer(queryset, many=True)
        return Response({'results': serializer.data, 'has_next': False})

    @action(detail=True, methods=['get'])
    def critiques(self, request, pk=None):
        """Get all critiques for this artwork.

        Example: /api/artworks/5/critiques/
        """
        artwork = self.get_object()
        critiques = artwork.critiques.all().order_by('-created_at')

        # Apply pagination
        page = self.paginate_queryset(critiques)
        if page is not None:
            serializer = CritiqueSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)

        serializer = CritiqueSerializer(critiques, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def add_critique(self, request, pk=None):
        """Add a critique to this artwork.

        Example: POST /api/artworks/5/add_critique/
        Payload: { "text": "Great composition!", "composition_score": 5, "technique_score": 4, "originality_score": 5 }
        """
        artwork = self.get_object()

        # Create a mutable copy of the request data and add the artwork ID
        data = request.data.copy()
        data['artwork'] = artwork.id

        # Create and validate the serializer
        serializer = CritiqueSerializer(data=data, context={'request': request})
        if serializer.is_valid():
            serializer.save(author=request.user, artwork=artwork)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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




class CritiqueViewSet(viewsets.ModelViewSet):
    """API endpoint for viewing and editing critiques with comprehensive search and filtering.

    Allows list, retrieve, create, update, and delete operations on critiques.

    Permissions:
    - Anyone can view critiques (GET)
    - Only authenticated users can create critiques (POST)
    - Only the critique's author can update it (PUT/PATCH)
    - Only the critique's author or users with MODERATOR/ADMIN role can delete it (DELETE)
    - Only the artwork's author can hide critiques (POST to /api/critiques/{id}/hide/)
    - Only users with MODERATOR/ADMIN role can flag critiques as inappropriate (POST to /api/critiques/{id}/flag/)

    Search and Filtering:
    - Search: ?search=query (searches critique text)
    - Filter by author: ?author=user_id or ?author__username=username
    - Filter by artwork: ?artwork=artwork_id or ?artwork__title=title
    - Filter by scores: ?min_composition_score=7&min_technique_score=8
    - Filter by date: ?created_after=2024-01-01&created_before=2024-12-31
    - Filter by reactions: ?min_helpful_reactions=5
    - Hide status: ?is_hidden=false (show only visible critiques)
    - Ordering: ?ordering=-created_at (prefix with - for descending)
    """
    queryset = Critique.objects.all().order_by('-created_at')
    serializer_class = CritiqueSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = CritiqueFilter
    search_fields = ['text', 'author__username', 'artwork__title']
    ordering_fields = ['created_at', 'updated_at', 'composition_score', 'technique_score', 'originality_score']
    ordering = ['-created_at']  # Default ordering

    def get_permissions(self):
        """
        Return different permission classes based on the action:
        - create: IsAuthenticated
        - update/partial_update: IsOwnerOrReadOnly (only author can edit)
        - destroy: IsModeratorOrOwner (author or moderator/admin can delete)
        - hide: Custom permission check in the method (only artwork owner can hide)
        - flag: IsModeratorOrAdmin (only moderators/admins can flag as inappropriate)
        - default: IsAuthenticatedOrReadOnly
        """
        if self.action == 'destroy':
            permission_classes = [permissions.IsAuthenticated, IsModeratorOrOwner]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
        elif self.action == 'create':
            permission_classes = [permissions.IsAuthenticated]
        elif self.action == 'flag':
            permission_classes = [permissions.IsAuthenticated, IsModeratorOrAdmin]
        else:
            permission_classes = [permissions.IsAuthenticatedOrReadOnly]

        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """
        Filter critiques by artwork ID or author ID.
        Only show hidden critiques to the artwork owner and critique author.
        """
        queryset = Critique.objects.all().order_by('-created_at')

        # Filter by artwork
        artwork_id = self.request.query_params.get('artwork', None)
        if artwork_id is not None:
            queryset = queryset.filter(artwork_id=artwork_id)

        # Filter by author/user
        author_id = self.request.query_params.get('author', None)
        if author_id is not None:
            queryset = queryset.filter(author_id=author_id)

        # Hide critiques that have been hidden by the artwork owner, unless
        # the current user is the artwork owner or the critique author
        user = self.request.user
        if user.is_authenticated:
            # If user is authenticated, show hidden critiques if user is
            # the artwork owner or critique author
            queryset = queryset.filter(
                # Either critique is not hidden
                # OR user is the artwork owner
                # OR user is the critique author
                models.Q(is_hidden=False) |
                models.Q(artwork__author=user) |
                models.Q(author=user)
            )
        else:
            # For anonymous users, never show hidden critiques
            queryset = queryset.filter(is_hidden=False)

        # Filter out critiques with rejected moderation status unless
        # the user is the author or artwork owner
        if user.is_authenticated:
            queryset = queryset.filter(
                # Either critique is not rejected
                # OR user is the artwork owner
                # OR user is the critique author
                models.Q(moderation_status__in=['APPROVED', 'PENDING']) |
                models.Q(artwork__author=user) |
                models.Q(author=user)
            )
        else:
            # For anonymous users, only show approved critiques
            queryset = queryset.filter(moderation_status='APPROVED')

        return queryset

    def get_serializer_class(self):
        """Return different serializers based on action."""
        if self.action == 'list':
            return CritiqueListSerializer
        return CritiqueSerializer

    def get_serializer_context(self):
        """Add the request to the serializer context."""
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

    def perform_create(self, serializer):
        """
        Set the author to the current user when creating a critique.
        Prevent users from critiquing their own artwork.
        """
        artwork_id = serializer.validated_data.get('artwork').id
        artwork = ArtWork.objects.get(id=artwork_id)

        # Check if user is trying to critique their own artwork
        if self.request.user == artwork.author:
            from rest_framework.exceptions import ValidationError
            raise ValidationError("You cannot critique your own artwork.")

        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def hide(self, request, pk=None):
        """
        Hide a critique from public view.
        Only the artwork owner can hide critiques.

        Example: POST /api/critiques/5/hide/
        Payload: { "reason": "Inappropriate content" } (optional)
        """
        critique = self.get_object()

        # Check if user is the artwork owner
        if request.user != critique.artwork.author:
            return Response(
                {"error": "Only the artwork owner can hide critiques"},
                status=status.HTTP_403_FORBIDDEN
            )

        # Get the reason from request data (optional)
        reason = request.data.get('reason', None)

        # Hide the critique
        critique.hide(request.user, reason)

        serializer = self.get_serializer(critique)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def unhide(self, request, pk=None):
        """
        Unhide a previously hidden critique.
        Only the artwork owner who hid the critique can unhide it.

        Example: POST /api/critiques/5/unhide/
        """
        critique = self.get_object()

        # Check if user is the artwork owner
        if request.user != critique.artwork.author:
            return Response(
                {"error": "Only the artwork owner can unhide critiques"},
                status=status.HTTP_403_FORBIDDEN
            )

        # Make sure the critique is actually hidden
        if not critique.is_hidden:
            return Response(
                {"error": "This critique is not hidden"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Unhide the critique
        critique.unhide()

        serializer = self.get_serializer(critique)
        return Response({
            "status": "success",
            "message": "Critique has been unhidden successfully",
            "critique": serializer.data
        })

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated, IsModeratorOrAdmin])
    def flag(self, request, pk=None):
        """
        Flag a critique for moderation.
        Only users with MODERATOR or ADMIN role can flag critiques.

        Example: POST /api/critiques/5/flag/
        Payload: { "reason": "Offensive content" }
        """
        critique = self.get_object()

        # Check if reason is provided
        reason = request.data.get('reason', None)
        if not reason:
            return Response(
                {"error": "Reason for flagging is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Flag the critique as a moderator action
        critique.flag(request.user, reason)

        return Response({
            "status": "Critique has been flagged for moderation",
            "message": "The critique has been flagged as inappropriate by a moderator"
        })

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated], url_path='replies')
    def replies(self, request, pk=None):
        """
        Add a reply to a critique.
        Any authenticated user can reply to critiques.

        Example: POST /api/critiques/5/replies/
        Payload: { "text": "Thank you for your feedback!" }
        """
        critique = self.get_object()

        # Allow any authenticated user to reply (not just artwork owner)
        # if request.user != critique.artwork.author:
        #     return Response(
        #         {"error": "Only the artwork owner can reply to critiques"},
        #         status=status.HTTP_403_FORBIDDEN
        #     )

        # Check if text is provided
        text = request.data.get('text', None)
        if not text:
            return Response(
                {"error": "Reply text is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create the reply
        from critique.models import CritiqueReply
        reply = CritiqueReply.objects.create(
            critique=critique,
            author=request.user,
            text=text
        )

        serializer = CritiqueReplySerializer(reply)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated], url_path='test-react')
    def test_react(self, request, pk=None):
        """Test endpoint to verify routing works."""
        return Response({
            "message": "Test endpoint working",
            "critique_id": pk,
            "user": str(request.user),
            "method": request.method
        })

    @action(detail=True, methods=['post'], permission_classes=[], url_path='react')
    def react(self, request, pk=None):
        """
        Toggle a reaction on this critique.

        Example: POST /api/critiques/5/react/
        Payload: {"type": "HELPFUL"}

        This will create the reaction if it doesn't exist or remove it if it does,
        effectively toggling the reaction status.
        """
        try:
            critique = self.get_object()
            
            # Ensure user is authenticated for reactions
            if not request.user.is_authenticated:
                return Response(
                    {"error": "Authentication required"},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            # Prevent users from reacting to their own critiques
            if critique.author == request.user:
                return Response(
                    {"error": "You cannot react to your own critique"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Validate reaction type - try both 'type' and 'reaction_type' fields
            reaction_type = request.data.get('type') or request.data.get('reaction_type')
            valid_types = [choice[0] for choice in Reaction.ReactionType.choices]
            
            if not reaction_type:
                return Response(
                    {"error": "Reaction type is required", "valid_types": valid_types},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            if reaction_type not in valid_types:
                return Response(
                    {"error": f"Invalid reaction type '{reaction_type}'. Allowed values: {valid_types}"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Check if user already gave this reaction type to this critique
            existing_reaction = Reaction.objects.filter(
                user=request.user,
                critique=critique,
                reaction_type=reaction_type
            ).first()

            print(f"------ REACTION TOGGLE DEBUG ------")
            print(f"User: {request.user.username}")
            print(f"Critique ID: {critique.id}")
            print(f"Reaction Type: {reaction_type}")
            print(f"Existing reaction: {existing_reaction}")
            print(f"All reactions for this critique: {list(critique.reactions.all().values('user__username', 'reaction_type'))}")

            # Toggle reaction: remove if exists, add if doesn't
            created = False
            if existing_reaction:
                # Remove the reaction (toggle off)
                print(f"Removing existing reaction: {existing_reaction.id}")
                existing_reaction.delete()
                print(f"Reaction deleted successfully")
            else:
                # Create the reaction (toggle on)
                new_reaction = Reaction.objects.create(
                    user=request.user,
                    critique=critique,
                    reaction_type=reaction_type
                )
                print(f"Created new reaction: {new_reaction.id}")
                created = True

            print(f"After toggle - All reactions: {list(critique.reactions.all().values('user__username', 'reaction_type'))}")
            print(f"----------------------------------")

            # Get updated reaction counts
            critique_serializer = CritiqueSerializer(critique, context={'request': request})

            response_data = {
                'created': created,
                'reaction_type': reaction_type,
                'critique_id': critique.id,
                'helpful_count': critique.get_helpful_count(),
                'inspiring_count': critique.get_inspiring_count(),
                'detailed_count': critique.get_detailed_count(),
                'user_reactions': list(critique.reactions.filter(user=request.user).values_list('reaction_type', flat=True))
            }

            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {"error": f"Server error: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def move_to_folder(self, request):
        """
        Move an artwork to a specific folder or remove it from folders (set to None).
        
        POST /api/artworks/move-to-folder/
        Body: {
            "artwork_id": 123,
            "folder_id": 456  // Optional - omit to remove from folders
        }
        """
        try:
            artwork_id = request.data.get('artwork_id')
            folder_id = request.data.get('folder_id')
            
            if not artwork_id:
                return Response(
                    {"error": "artwork_id is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get artwork and verify ownership
            try:
                artwork = ArtWork.objects.get(id=artwork_id, author=request.user)
            except ArtWork.DoesNotExist:
                return Response(
                    {"error": "Artwork not found or you don't have permission to modify it"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Handle folder assignment
            if folder_id:
                try:
                    folder = Folder.objects.get(id=folder_id, owner=request.user)
                    artwork.folder = folder
                except Folder.DoesNotExist:
                    return Response(
                        {"error": "Folder not found or you don't have permission to use it"},
                        status=status.HTTP_404_NOT_FOUND
                    )
            else:
                # Remove from folder (set to None)
                artwork.folder = None
            
            artwork.save()
            
            return Response({
                "success": True,
                "artwork_id": artwork.id,
                "folder_id": artwork.folder.id if artwork.folder else None,
                "folder_name": artwork.folder.name if artwork.folder else None
            })
            
        except Exception as e:
            return Response(
                {"error": f"Server error: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )



    @action(detail=True, methods=['delete'], permission_classes=[permissions.IsAuthenticated])
    def unreact(self, request, pk=None):
        """
        Remove a reaction from this critique.

        Example: DELETE /api/critiques/5/unreact/?reaction_type=HELPFUL

        Note: This endpoint is deprecated. Use toggle_reaction instead.
        """
        critique = self.get_object()

        # Validate reaction type
        reaction_type = request.query_params.get('reaction_type')
        if not reaction_type or reaction_type not in [choice[0] for choice in Reaction.ReactionType.choices]:
            return Response(
                {"error": f"Invalid reaction_type. Allowed values: {[choice[0] for choice in Reaction.ReactionType.choices]}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Find and delete the reaction
        try:
            reaction = Reaction.objects.get(
                user=request.user,
                critique=critique,
                reaction_type=reaction_type
            )
            reaction.delete()

            # Get updated reaction counts
            critique_serializer = CritiqueSerializer(critique, context={'request': request})

            response_data = {
                'helpful_count': critique_serializer.get_helpful_count(critique),
                'inspiring_count': critique_serializer.get_inspiring_count(critique),
                'detailed_count': critique_serializer.get_detailed_count(critique)
            }

            return Response(response_data, status=status.HTTP_200_OK)
        except Reaction.DoesNotExist:
            return Response(
                {"error": f"You haven't given a {reaction_type} reaction to this critique."},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['get'], url_path='artwork/(?P<artwork_id>[^/.]+)')
    def artwork_critiques(self, request, artwork_id=None):
        """Get all critiques for a specific artwork."""
        critiques = self.get_queryset().filter(artwork_id=artwork_id)
        page = self.paginate_queryset(critiques)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(critiques, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='user/(?P<user_id>[^/.]+)')
    def user_critiques(self, request, user_id=None):
        """Get all critiques by a specific user."""
        critiques = self.get_queryset().filter(author_id=user_id)
        page = self.paginate_queryset(critiques)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(critiques, many=True)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        """
        Delete a critique only if it has no engagement (replies or reactions).
        Users can only delete their own critiques.
        
        Deletion is blocked if the critique has:
        - Any replies from other users
        - Any reactions (HELPFUL, INSPIRING, DETAILED)
        
        If engagement is found, returns 403 Forbidden with helpful message.
        On successful deletion, recalculates artwork aggregated scores and deducts karma.
        """
        critique = self.get_object()
        
        # Check if user owns this critique
        if critique.author != request.user:
            return Response(
                {'error': 'You can only delete your own critiques'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check for engagement using the model method
        if critique.has_engagement():
            print("------ CRITIQUE DELETION DEBUG ------")
            print("Critique ID:", critique.id)
            print("Author:", critique.author.username)
            print("Requesting user:", request.user.username)
            print("Replies count:", critique.replies.count())
            print("Replies:", list(critique.replies.all().values('id', 'author__username', 'text')))
            print("All reactions count:", critique.reactions.count())
            print("All reactions:", list(critique.reactions.all().values('id', 'user__username', 'reaction_type')))
            print("Reactions (excluding author):", list(critique.reactions.exclude(user=critique.author).values('id', 'user__username', 'reaction_type')))
            print("Engagement summary:", critique.get_engagement_summary())
            print("Has engagement?:", critique.has_engagement())
            print("-------------------------------------")
            
            engagement_summary = critique.get_engagement_summary()
            
            # Build detailed error message
            engagement_details = []
            if engagement_summary['reply_count'] > 0:
                engagement_details.append(f"{engagement_summary['reply_count']} reply(s)")
            if engagement_summary['reaction_count'] > 0:
                engagement_details.append(f"{engagement_summary['reaction_count']} reaction(s)")
            
            engagement_text = " and ".join(engagement_details)
            
            return Response(
                {
                    'error': 'This critique has feedback from others and cannot be deleted. You can edit it or request to hide it.',
                    'details': f'Critique has {engagement_text}',
                    'engagement_summary': engagement_summary,
                    'suggestion': 'Consider editing your critique or asking the artwork owner to hide it if inappropriate.'
                },
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Store artwork for score recalculation
        artwork = critique.artwork
        
        # Deduct karma points for critique deletion
        try:
            from ..karma import deduct_critique_karma
            deduct_critique_karma(request.user, critique)
        except ImportError:
            # If karma system is not available, continue with deletion
            pass
        
        # Delete the critique
        critique_id = critique.id
        critique.delete()
        
        # Recalculate artwork aggregated scores
        self._recalculate_artwork_scores(artwork)
        
        return Response(
            {
                'message': 'Critique deleted successfully',
                'critique_id': critique_id,
                'artwork_scores_updated': True
            },
            status=status.HTTP_204_NO_CONTENT
        )
    
    def _recalculate_artwork_scores(self, artwork):
        """
        Recalculate aggregated scores for an artwork after critique deletion.
        Updates average composition, technique, and originality scores.
        """
        from django.db.models import Avg
        
        # Get remaining critiques for this artwork
        remaining_critiques = artwork.critiques.filter(
            moderation_status='APPROVED',
            is_hidden=False
        )
        
        # Calculate new averages
        averages = remaining_critiques.aggregate(
            avg_composition=Avg('composition_score'),
            avg_technique=Avg('technique_score'),
            avg_originality=Avg('originality_score')
        )
        
        # Update artwork fields if they exist
        if hasattr(artwork, 'avg_composition_score'):
            artwork.avg_composition_score = averages['avg_composition'] or 0
        if hasattr(artwork, 'avg_technique_score'):
            artwork.avg_technique_score = averages['avg_technique'] or 0
        if hasattr(artwork, 'avg_originality_score'):
            artwork.avg_originality_score = averages['avg_originality'] or 0
        
        try:
            artwork.save()
        except Exception:
            # If artwork doesn't have these fields, that's fine
            pass

class ReactionViewSet(viewsets.ModelViewSet):
    """API endpoint for managing reactions to critiques.

    Allows authenticated users to react to critiques with different reaction types:
    - HELPFUL - Indicates the critique was useful to the user
    - INSPIRING - Indicates the critique provided inspiration
    - DETAILED - Indicates the critique was thorough and comprehensive

    Each user can give one reaction of each type to a specific critique.
    """
    queryset = Reaction.objects.all()
    serializer_class = ReactionSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        """Filter reactions by user and/or critique."""
        queryset = Reaction.objects.all()

        # Filter by user
        user_id = self.request.query_params.get('user', None)
        if user_id:
            queryset = queryset.filter(user_id=user_id)

        # Filter by critique
        critique_id = self.request.query_params.get('critique', None)
        if critique_id:
            queryset = queryset.filter(critique_id=critique_id)

        # Filter by reaction type
        reaction_type = self.request.query_params.get('type', None)
        if reaction_type:
            queryset = queryset.filter(reaction_type=reaction_type)

        return queryset

    def perform_create(self, serializer):
        """Set the current user when creating a reaction."""
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def my_reactions(self, request):
        """Get all reactions made by the current user."""
        reactions = Reaction.objects.filter(user=request.user)
        serializer = self.get_serializer(reactions, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def reaction_types(self, request):
        """Get all available reaction types."""
        return Response({
            'reaction_types': [
                {'value': choice[0], 'display': choice[1]} 
                for choice in Reaction.ReactionType.choices
            ]
        })

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get statistics about reactions across the platform."""
        # Total reactions count
        total_count = Reaction.objects.count()

        # Count by type
        counts_by_type = {}
        for reaction_type in [choice[0] for choice in Reaction.ReactionType.choices]:
            count = Reaction.objects.filter(reaction_type=reaction_type).count()
            counts_by_type[reaction_type] = count

        return Response({
            'total_count': total_count,
            'counts_by_type': counts_by_type
        })


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
        critique_count = Critique.objects.count()
        user_count = User.objects.count()
    except Exception as e:
        artwork_count = critique_count = user_count = f"ERROR: {str(e)}"

    # Compile response data
    data = {
        "status": "healthy",
        "api_version": "1.0.0",
        "database": {
            "status": db_status,
            "counts": {
                "artworks": artwork_count,
                "critiques": critique_count,
                "users": user_count,
            }
        },
        "message": "Art Critique API is running"
    }

    return Response(data, status=status.HTTP_200_OK)


class NotificationViewSet(viewsets.ModelViewSet):
    """API endpoint for managing user notifications.

    This ViewSet provides endpoints for:
    - GET /api/notifications/ - List all notifications for the current user
    - GET /api/notifications/{id}/ - Get a specific notification
    - PATCH /api/notifications/{id}/ - Mark a notification as read
    - DELETE /api/notifications/{id}/ - Delete a notification
    - GET /api/notifications/unread/ - Get count of unread notifications
    - POST /api/notifications/mark-all-read/ - Mark all notifications as read
    """
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return only notifications for the current user."""
        return Notification.objects.filter(recipient=self.request.user).order_by('-created_at')

    @action(detail=False, methods=['get'])
    def unread(self, request):
        """Return count of unread notifications for the current user."""
        count = Notification.objects.filter(
            recipient=request.user,
            is_read=False
        ).count()

        return Response({"unread_count": count})

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """Mark all notifications for the current user as read."""
        Notification.objects.filter(
            recipient=request.user,
            is_read=False
        ).update(is_read=True)

        return Response({"status": "success", "message": "All notifications marked as read"})

    @action(detail=False, methods=['post'])
    def mark_multiple_read(self, request):
        """Mark multiple notifications as read in a single request.

        Expects a JSON payload with a list of notification IDs:
        { "notification_ids": [1, 2, 3] }

        Only works for notifications that belong to the current user.
        """
        notification_ids = request.data.get('notification_ids', [])

        if not notification_ids:
            return Response(
                {"error": "No notification IDs provided"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Update only notifications that belong to the current user
        update_count = Notification.objects.filter(
            id__in=notification_ids,
            recipient=request.user
        ).update(is_read=True)

        return Response({
            "status": "success", 
            "message": f"{update_count} notifications marked as read"
        })

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark a specific notification as read."""
        notification = self.get_object()
        notification.is_read = True
        notification.save()

        return Response({
            "status": "success", 
            "message": "Notification marked as read"
        })

    def perform_create(self, serializer):
        """Ensure notifications are always associated with the current user as recipient."""
        serializer.save(recipient=self.request.user)

    def update(self, request, *args, **kwargs):
        """Limit updates to only the is_read field for security."""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        # Only allow updating is_read field
        if 'is_read' in request.data:
            data = {'is_read': request.data['is_read']}
        else:
            return Response(
                {"error": "Only 'is_read' field can be updated"},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)

# ============================================================================
# FOLDER VIEWSET FOR PORTFOLIO MANAGEMENT
# ============================================================================

class FolderViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing portfolio folders.

    Provides comprehensive portfolio management with the following endpoints:
    - GET /api/folders/ - List folders (filtered by ownership and visibility)
    - POST /api/folders/ - Create new folder (authenticated users only)
    - GET /api/folders/{id}/ - Get folder details with contents
    - PUT/PATCH /api/folders/{id}/ - Update folder (owner only)
    - DELETE /api/folders/{id}/ - Delete folder (owner only)
    - GET /api/folders/{id}/artworks/ - List artworks in folder
    - POST /api/folders/{id}/add_artwork/ - Add artwork to folder
    - POST /api/folders/{id}/remove_artwork/ - Remove artwork from folder
    """
    serializer_class = FolderSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'updated_at', 'name']
    ordering = ['-updated_at']

    def get_queryset(self):
        """Return folders based on user permissions and visibility settings."""
        user = self.request.user

        if user.is_authenticated:
            # Authenticated users see their own folders + public folders from others
            # Note: Unlisted folders are handled by direct access only, not in listings
            from django.db.models import Q
            return Folder.objects.filter(
                Q(owner=user) | Q(is_public=Folder.VISIBILITY_PUBLIC)
            ).distinct()
        else:
            # Anonymous users only see public folders
            return Folder.objects.filter(is_public=Folder.VISIBILITY_PUBLIC)

    def retrieve(self, request, *args, **kwargs):
        """Override retrieve to enforce folder visibility rules."""
        folder = self.get_object()

        # Check if user can view this folder
        if not folder.is_viewable_by(request.user):
            return Response(
                {"detail": "Not found."},  # Don't reveal folder exists
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = self.get_serializer(folder)
        return Response(serializer.data)

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'list':
            return FolderListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return FolderCreateUpdateSerializer
        return FolderSerializer

    def perform_create(self, serializer):
        """Create folder with current user as owner."""
        serializer.save(owner=self.request.user)

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action == 'create':
            permission_classes = [permissions.IsAuthenticated]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
        else:
            permission_classes = [permissions.IsAuthenticatedOrReadOnly]

        return [permission() for permission in permission_classes]

    @action(detail=True, methods=['get'])
    def artworks(self, request, pk=None):
        """Get all artworks in this folder."""
        folder = self.get_object()

        # Check if user can view this folder
        if not folder.is_viewable_by(request.user):
            return Response(
                {"error": "You don't have permission to view this folder"},
                status=status.HTTP_403_FORBIDDEN
            )

        artworks = folder.artworks.all().order_by('-created_at')

        # Use the existing ArtWorkListSerializer for consistency
        serializer = ArtWorkListSerializer(artworks, many=True, context={'request': request})
        return Response({
            'folder': FolderSerializer(folder, context={'request': request}).data,
            'artworks': serializer.data,
            'count': artworks.count()
        })

    @action(detail=True, methods=['post'])
    def add_artwork(self, request, pk=None):
        """Add an artwork to this folder."""
        folder = self.get_object()

        # Only folder owner can add artworks
        if folder.owner != request.user:
            return Response(
                {"error": "Only the folder owner can add artworks"},
                status=status.HTTP_403_FORBIDDEN
            )

        artwork_id = request.data.get('artwork_id')
        if not artwork_id:
            return Response(
                {"error": "artwork_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            artwork = ArtWork.objects.get(id=artwork_id, author=request.user)
        except ArtWork.DoesNotExist:
            return Response(
                {"error": "Artwork not found or you don't own it"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Add artwork to folder
        artwork.folder = folder
        artwork.save()

        return Response({
            "status": "success",
            "message": f"Artwork '{artwork.title}' added to folder '{folder.name}'"
        })

    @action(detail=True, methods=['post'])
    def remove_artwork(self, request, pk=None):
        """Remove an artwork from this folder."""
        folder = self.get_object()

        # Only folder owner can remove artworks
        if folder.owner != request.user:
            return Response(
                {"error": "Only the folder owner can remove artworks"},
                status=status.HTTP_403_FORBIDDEN
            )

        artwork_id = request.data.get('artwork_id')
        if not artwork_id:
            return Response(
                {"error": "artwork_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            artwork = ArtWork.objects.get(id=artwork_id, folder=folder, author=request.user)
        except ArtWork.DoesNotExist:
            return Response(
                {"error": "Artwork not found in this folder or you don't own it"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Remove artwork from folder
        artwork.folder = None
        artwork.save()

        return Response({
            "status": "success",
            "message": f"Artwork '{artwork.title}' removed from folder '{folder.name}'"
        })

    @action(detail=False, methods=['get'])
    def my_folders(self, request):
        """Get all folders belonging to the current user."""
        if not request.user.is_authenticated:
            return Response(
                {"error": "Authentication required"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        folders = Folder.objects.filter(owner=request.user).order_by('display_order', '-updated_at')
        serializer = FolderListSerializer(folders, many=True, context={'request': request})

        return Response({
            'folders': serializer.data,
            'count': folders.count()
        })

    @action(detail=False, methods=['post'])
    def reorder(self, request):
        """Reorder folders for the current user."""
        if not request.user.is_authenticated:
            return Response(
                {"error": "Authentication required"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        folder_order = request.data.get('folder_order', [])
        
        if not folder_order or not isinstance(folder_order, list):
            return Response(
                {"error": "folder_order must be a non-empty list"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Validate that all folders belong to the user
            folder_ids = [int(folder_id) for folder_id in folder_order]
            user_folders = Folder.objects.filter(
                id__in=folder_ids, 
                owner=request.user
            )
            
            if user_folders.count() != len(folder_ids):
                return Response(
                    {"error": "Some folders not found or not owned by user"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Update the display order for each folder
            for index, folder_id in enumerate(folder_ids):
                Folder.objects.filter(id=folder_id, owner=request.user).update(
                    display_order=index
                )

            return Response({
                "status": "success",
                "message": "Folder order updated successfully"
            })

        except (ValueError, TypeError) as e:
            return Response(
                {"error": "Invalid folder ID format"},
                status=status.HTTP_400_BAD_REQUEST
            )


class ArtworkVersionViewSet(APIView):
    """API endpoints for managing artwork versions"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, artwork_id):
        """List all versions for a specific artwork"""
        try:
            artwork = ArtWork.objects.get(id=artwork_id, author=request.user)
            versions = artwork.versions.all()
            serializer = ArtWorkVersionSerializer(versions, many=True)
            
            return Response({
                'versions': serializer.data,
                'artwork_title': artwork.title,
                'total_versions': versions.count()
            })
        except ArtWork.DoesNotExist:
            return Response({'error': 'Artwork not found or not owned by user'}, 
                          status=status.HTTP_404_NOT_FOUND)
    
    def post(self, request, artwork_id):
        """Create a new version of an artwork"""
        try:
            artwork = ArtWork.objects.get(id=artwork_id, author=request.user)
            version_notes = request.data.get('version_notes', '')
            force_create = request.data.get('force_create', False)
            
            # Create version with current artwork state
            version = artwork.create_version(version_notes=version_notes)
            
            # Update artwork with new data if provided (skip if just saving current state)
            if not force_create:
                if 'title' in request.data:
                    artwork.title = request.data['title']
                if 'description' in request.data:
                    artwork.description = request.data['description']
                if 'image' in request.data:
                    artwork.image = request.data['image']
                if 'medium' in request.data:
                    artwork.medium = request.data['medium']
                if 'dimensions' in request.data:
                    artwork.dimensions = request.data['dimensions']
                if 'tags' in request.data:
                    artwork.tags = request.data['tags']
                
                artwork.save()
            
            serializer = ArtWorkVersionSerializer(version)
            return Response({
                'version': serializer.data,
                'message': f'Version {version.version_number} created successfully'
            }, status=status.HTTP_201_CREATED)
            
        except ArtWork.DoesNotExist:
            return Response({'error': 'Artwork not found or not owned by user'}, 
                          status=status.HTTP_404_NOT_FOUND)
    
    def retrieve(self, request, artwork_id, version_id):
        """Get a specific version of an artwork"""
        try:
            artwork = ArtWork.objects.get(id=artwork_id, author=request.user)
            version = artwork.versions.get(id=version_id)
            serializer = ArtWorkVersionSerializer(version)
            
            return Response({
                'version': serializer.data,
                'artwork_title': artwork.title
            })
        except ArtWork.DoesNotExist:
            return Response({'error': 'Artwork not found or not owned by user'}, 
                          status=status.HTTP_404_NOT_FOUND)
        except ArtWorkVersion.DoesNotExist:
            return Response({'error': 'Version not found'}, 
                          status=status.HTTP_404_NOT_FOUND)
    
    def delete(self, request, artwork_id, version_id):
        """Delete a specific version"""
        try:
            artwork = ArtWork.objects.get(id=artwork_id, author=request.user)
            version = artwork.versions.get(id=version_id)
            
            # Prevent deletion if this is the only version
            if artwork.versions.count() <= 1:
                return Response({'error': 'Cannot delete the only version of an artwork'}, 
                              status=status.HTTP_400_BAD_REQUEST)
            
            version_number = version.version_number
            version.delete()
            
            return Response({
                'message': f'Version {version_number} deleted successfully',
                'success': True
            })
        except ArtWork.DoesNotExist:
            return Response({'error': 'Artwork not found or not owned by user'}, 
                          status=status.HTTP_404_NOT_FOUND)
        except ArtWorkVersion.DoesNotExist:
            return Response({'error': 'Version not found'}, 
                          status=status.HTTP_404_NOT_FOUND)
    
    def archive(self, request, version_id):
        """Archive a specific version"""
        try:
            version = ArtWorkVersion.objects.get(id=version_id, artwork__author=request.user)
            reason = request.data.get('reason', '')
            
            # Add archived field to model if needed, for now just return success
            return Response({
                'message': f'Version {version.version_number} archived successfully',
                'reason': reason
            })
        except ArtWorkVersion.DoesNotExist:
            return Response({'error': 'Version not found or not owned by user'}, 
                          status=status.HTTP_404_NOT_FOUND)

@api_view(['GET', 'POST'])
@permission_classes([permissions.IsAuthenticated])
def create_artwork_version(request, artwork_id):
    """Create a new version of an artwork or get all versions"""
    try:
        artwork = ArtWork.objects.get(id=artwork_id, author=request.user)
        
        if request.method == 'GET':
            # Return all versions for this artwork
            versions = artwork.versions.all().order_by('-version_number')
            serializer = ArtWorkVersionSerializer(versions, many=True)
            return Response({
                'versions': serializer.data,
                'artwork_title': artwork.title
            })
        
        elif request.method == 'POST':
            # Check if force_create is enabled (for saving current state)
            force_create = request.data.get('force_create', False)
            
            # Check if there are meaningful changes before creating a version
            has_changes = False
            changes_detected = []
            
            # Check for meaningful changes
            if 'image' in request.FILES:
                has_changes = True
                changes_detected.append('image')
            
            if 'title' in request.data and request.data['title'] != artwork.title:
                has_changes = True
                changes_detected.append('title')
                
            if 'description' in request.data and request.data['description'] != artwork.description:
                has_changes = True
                changes_detected.append('description')
                
            if 'medium' in request.data and request.data['medium'] != getattr(artwork, 'medium', ''):
                has_changes = True
                changes_detected.append('medium')
                
            if 'dimensions' in request.data and request.data['dimensions'] != getattr(artwork, 'dimensions', ''):
                has_changes = True
                changes_detected.append('dimensions')
                
            if 'tags' in request.data and request.data['tags'] != getattr(artwork, 'tags', ''):
                has_changes = True
                changes_detected.append('tags')
            
            # Only create a new version if there are meaningful changes OR force_create is true
            if not has_changes and not force_create:
                return Response({
                    'error': 'No changes detected',
                    'message': 'A new version is only created when there are meaningful changes to the artwork.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get the highest version number and increment
            highest_version = artwork.versions.aggregate(
                max_version=Max('version_number')
            )['max_version'] or 0
            new_version_number = highest_version + 1
            
            # Create version notes with detected changes
            if changes_detected:
                auto_notes = f"Changes: {', '.join(changes_detected)}"
            elif force_create:
                auto_notes = "Snapshot: Current state saved"
            else:
                auto_notes = "Version created"
                
            manual_notes = request.data.get('version_notes', '')
            version_notes = f"{auto_notes}. {manual_notes}".strip('. ')
            
            # STEP 1: Create version with CURRENT artwork state (preserves old image)
            version = ArtWorkVersion.objects.create(
                artwork=artwork,
                version_number=new_version_number,
                title=artwork.title,  # Use current artwork values for the version
                description=artwork.description,
                image=artwork.image,  # Preserve the OLD image in the version
                medium=getattr(artwork, 'medium', ''),
                dimensions=getattr(artwork, 'dimensions', ''),
                tags=getattr(artwork, 'tags', ''),
                version_notes=version_notes
            )
            
            # STEP 2: Update artwork with NEW data (including new image if provided)
            if 'title' in request.data:
                artwork.title = request.data['title']
            if 'description' in request.data:
                artwork.description = request.data['description']
            if 'category' in request.data:
                artwork.category = request.data['category']
            if 'medium' in request.data:
                artwork.medium = request.data['medium']
            if 'dimensions' in request.data:
                artwork.dimensions = request.data['dimensions']
            if 'tags' in request.data:
                artwork.tags = request.data['tags']
            
            # STEP 3: Only update artwork with new image (version keeps old image)
            if 'image' in request.FILES:
                new_image = request.FILES['image']
                artwork.image = new_image  # Only update artwork, NOT the version
            
            artwork.save()
            
            serializer = ArtWorkVersionSerializer(version)
            return Response({
                'version': serializer.data,
                'message': f'Version {version.version_number} created successfully with changes: {", ".join(changes_detected)}'
            }, status=status.HTTP_201_CREATED)
        
    except ArtWork.DoesNotExist:
        return Response({'error': 'Artwork not found or not owned by user'}, 
                      status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_artwork_version(request, artwork_id, version_id):
    """Get a specific version of an artwork"""
    try:
        artwork = ArtWork.objects.get(id=artwork_id, author=request.user)
        version = artwork.versions.get(id=version_id)
        serializer = ArtWorkVersionSerializer(version)
        
        return Response({
            'version': serializer.data,
            'artwork_title': artwork.title
        })
    except ArtWork.DoesNotExist:
        return Response({'error': 'Artwork not found or not owned by user'}, 
                      status=status.HTTP_404_NOT_FOUND)
    except ArtWorkVersion.DoesNotExist:
        return Response({'error': 'Version not found'}, 
                      status=status.HTTP_404_NOT_FOUND)

@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def delete_artwork_version(request, version_id):
    """Delete a specific version"""
    try:
        version = ArtWorkVersion.objects.get(id=version_id, artwork__author=request.user)
        artwork = version.artwork
        
        # Prevent deletion if this is the only version
        if artwork.versions.count() <= 1:
            return Response({'error': 'Cannot delete the only version of an artwork'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        version_number = version.version_number
        version.delete()
        
        return Response({
            'message': f'Version {version_number} deleted successfully',
            'success': True
        })
    except ArtWorkVersion.DoesNotExist:
        return Response({'error': 'Version not found or not owned by user'}, 
                      status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def switch_artwork_version(request, artwork_id, version_id):
    """Switch the main artwork display to a specific version."""
    try:
        artwork = ArtWork.objects.get(id=artwork_id)
        
        # Check if user has permission to view this artwork
        if artwork.folder and not artwork.folder.is_viewable_by(request.user):
            return Response(
                {'error': 'Not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get the version
        version = ArtWorkVersion.objects.get(id=version_id, artwork=artwork)
        
        # Check if version contains archived note and user is not the author
        if version.version_notes and '[ARCHIVED:' in version.version_notes and request.user != artwork.author:
            return Response(
                {'error': 'Version not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Return version data for frontend to update the display
        return Response({
            'success': True,
            'version_number': version.version_number,
            'image_url': version.image.url if version.image else version.image_url,
            'title': version.title or artwork.title,
            'description': version.description or artwork.description,
            'total_versions': artwork.versions.count() + 1,  # Include current artwork state
            'message': f'Switched to version {version.version_number}'
        })
        
    except ArtWork.DoesNotExist:
        return Response(
            {'error': 'Artwork not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except ArtWorkVersion.DoesNotExist:
        return Response(
            {'error': 'Version not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def archive_artwork_version(request, version_id):
    """Archive a specific version"""
    try:
        version = ArtWorkVersion.objects.get(id=version_id, artwork__author=request.user)
        reason = request.data.get('reason', 'No reason provided')
        
        # Add archive note to version notes
        if version.version_notes:
            version.version_notes = f"{version.version_notes}\n[ARCHIVED: {reason}]"
        else:
            version.version_notes = f"[ARCHIVED: {reason}]"
        version.save()
        
        return Response({
            'message': f'Version {version.version_number} archived successfully',
            'reason': reason,
            'success': True,
            'status': 'archived',
            'version_id': version.id,
            'version_number': version.version_number
        })
    except ArtWorkVersion.DoesNotExist:
        return Response({'error': 'Version not found or not owned by user'}, 
                      status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def hide_critique(request, critique_id):
    """Hide a critique (only artwork author can hide)"""
    try:
        critique = Critique.objects.get(id=critique_id)
        
        # Check if user is the artwork author
        if request.user != critique.artwork.author:
            return Response(
                {'error': 'Only artwork author can hide critiques'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        critique.is_hidden = True
        critique.save()
        
        return Response({
            'success': True,
            'message': 'Critique hidden successfully',
            'critique_id': critique.id
        })
        
    except Critique.DoesNotExist:
        return Response(
            {'error': 'Critique not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def unhide_critique(request, critique_id):
    """Unhide a critique (only artwork author can unhide)"""
    try:
        critique = Critique.objects.get(id=critique_id)
        
        # Check if user is the artwork author
        if request.user != critique.artwork.author:
            return Response(
                {'error': 'Only artwork author can unhide critiques'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        critique.is_hidden = False
        critique.save()
        
        return Response({
            'success': True,
            'message': 'Critique unhidden successfully',
            'critique_id': critique.id
        })
        
    except Critique.DoesNotExist:
        return Response(
            {'error': 'Critique not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )

class ArtworkVersionViewSet(viewsets.ModelViewSet):
    """ViewSet for artwork version management"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ArtWorkVersionSerializer
    
    def get_queryset(self):
        return ArtWorkVersion.objects.filter(artwork__author=self.request.user)
    
    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        """Archive a specific version"""
        try:
            version = self.get_object()
            reason = request.data.get('reason', '')
            
            # Add archive note to version notes
            if version.version_notes:
                version.version_notes = f"{version.version_notes}\n[ARCHIVED: {reason}]"
            else:
                version.version_notes = f"[ARCHIVED: {reason}]"
            version.save()
            
            return Response({
                'message': f'Version {version.version_number} archived successfully',
                'reason': reason,
                'success': True,
                'status': 'archived',
                'version_id': version.id,
                'version_number': version.version_number
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def unarchive(self, request, pk=None):
        """Unarchive a specific version"""
        try:
            version = self.get_object()
            
            # Remove archive notes from version notes
            if version.version_notes and '[ARCHIVED:' in version.version_notes:
                lines = version.version_notes.split('\n')
                filtered_lines = [line for line in lines if not line.strip().startswith('[ARCHIVED:')]
                version.version_notes = '\n'.join(filtered_lines).strip()
                version.save()
            
            return Response({
                'message': f'Version {version.version_number} unarchived successfully',
                'success': True,
                'status': 'unarchived',
                'version_id': version.id,
                'version_number': version.version_number
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def switch(self, request, pk=None):
        """Switch to a specific version as the current display version"""
        try:
            version = self.get_object()
            artwork = version.artwork
            
            # Only allow the owner to switch versions
            if artwork.author != request.user:
                return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
            
            # Return version data for frontend to update display
            return Response({
                'message': f'Switched to version {version.version_number}',
                'success': True,
                'version': {
                    'id': version.id,
                    'version_number': version.version_number,
                    'image_url': version.image.url if version.image else None,
                    'version_notes': version.version_notes,
                    'created_at': version.created_at
                }
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class ArtworkVersionCompareView(APIView):
    """API endpoint for comparing artwork versions"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, artwork_id):
        """Compare two versions of an artwork"""
        try:
            artwork = ArtWork.objects.get(id=artwork_id, author=request.user)
            version1_id = request.query_params.get('version1')
            version2_id = request.query_params.get('version2')
            
            if not version1_id or not version2_id:
                return Response({'error': 'Both version1 and version2 parameters are required'}, 
                              status=status.HTTP_400_BAD_REQUEST)
            
            # Handle comparing with current version
            if version1_id == 'current':
                version1_data = {
                    'id': 'current',
                    'version_number': 'Current',
                    'title': artwork.title,
                    'description': artwork.description,
                    'image_display_url': artwork.image.url if artwork.image else None,
                    'medium': artwork.medium,
                    'dimensions': artwork.dimensions,
                    'tags': artwork.tags,
                    'created_at': artwork.updated_at or artwork.created_at
                }
            else:
                try:
                    version1 = artwork.versions.get(id=version1_id)
                    version1_data = ArtWorkVersionSerializer(version1).data
                except ArtWorkVersion.DoesNotExist:
                    return Response({'error': 'Version 1 not found'}, 
                                  status=status.HTTP_404_NOT_FOUND)
            
            if version2_id == 'current':
                version2_data = {
                    'id': 'current',
                    'version_number': 'Current',
                    'title': artwork.title,
                    'description': artwork.description,
                    'image_display_url': artwork.image.url if artwork.image else None,
                    'medium': artwork.medium,
                    'dimensions': artwork.dimensions,
                    'tags': artwork.tags,
                    'created_at': artwork.updated_at or artwork.created_at
                }
            else:
                try:
                    version2 = artwork.versions.get(id=version2_id)
                    version2_data = ArtWorkVersionSerializer(version2).data
                except ArtWorkVersion.DoesNotExist:
                    return Response({'error': 'Version 2 not found'}, 
                                  status=status.HTTP_404_NOT_FOUND)
            
            # Generate comparison data
            comparison = {
                'artwork_title': artwork.title,
                'version1': version1_data,
                'version2': version2_data,
                'differences': self._get_differences(version1_data, version2_data)
            }
            
            return Response(comparison)
            
        except ArtWork.DoesNotExist:
            return Response({'error': 'Artwork not found or not owned by user'}, 
                          status=status.HTTP_404_NOT_FOUND)
    
    def _get_differences(self, version1, version2):
        """Calculate meaningful differences between two versions"""
        differences = []
        
        # Check for image differences first (most important)
        img1 = version1.get('image_display_url')
        img2 = version2.get('image_display_url')
        
        if img1 != img2:
            differences.append({
                'field': 'image',
                'version1_value': img1,
                'version2_value': img2,
                'priority': 'high'
            })
        
        # Check text fields with priority ordering
        field_priorities = {
            'title': 'high',
            'medium': 'medium', 
            'dimensions': 'medium',
            'tags': 'low',
            'description': 'low'
        }
        
        for field, priority in field_priorities.items():
            val1 = version1.get(field, '').strip()
            val2 = version2.get(field, '').strip()
            
            # Skip trivial changes (empty to filled descriptions)
            if field == 'description':
                # Only show description changes if both have meaningful content
                if not val1 and val2:
                    continue  # Skip empty -> filled
                if val1 and not val2:
                    continue  # Skip filled -> empty
            
            if val1 != val2 and (val1 or val2):  # At least one must have content
                differences.append({
                    'field': field,
                    'version1_value': val1 or 'Not set',
                    'version2_value': val2 or 'Not set',
                    'priority': priority
                })
        
        # Sort by priority: high, medium, low
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        differences.sort(key=lambda x: priority_order.get(x['priority'], 3))
        
        return differences

class ArtworkVersionRestoreView(APIView):
    """API endpoint for setting an artwork to display a specific version"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, artwork_id, version_id):
        """Set artwork to display a specific version (creates snapshot of current state first)"""
        try:
            artwork = ArtWork.objects.get(id=artwork_id, author=request.user)
            version = artwork.versions.get(id=version_id)
            
            # Create a snapshot of the current state before restoration
            snapshot = artwork.create_version(
                version_notes=f"Auto-snapshot before restoring to version {version.version_number}"
            )
            
            # Update the artwork to match the selected version
            artwork.title = version.title
            artwork.description = version.description
            artwork.image = version.image  # Copy FROM version TO artwork
            if hasattr(version, 'medium') and version.medium:
                artwork.medium = version.medium
            if hasattr(version, 'dimensions') and version.dimensions:
                artwork.dimensions = version.dimensions
            if hasattr(version, 'tags') and version.tags:
                artwork.tags = version.tags
            artwork.save()
            
            return Response({
                'message': f'Artwork set to version {version.version_number}',
                'current_version': version.version_number,
                'success': True,
                'artwork': {
                    'id': artwork.id,
                    'title': artwork.title,
                    'description': artwork.description,
                    'image_url': artwork.image.url if artwork.image else None
                }
            })
            
        except ArtWork.DoesNotExist:
            return Response({'error': 'Artwork not found or not owned by user'}, 
                          status=status.HTTP_404_NOT_FOUND)
        except ArtWorkVersion.DoesNotExist:
            return Response({'error': 'Version not found'}, 
                          status=status.HTTP_404_NOT_FOUND)

class ArtworkVersionReorderView(APIView):
    """API endpoint for reordering artwork versions"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, artwork_id):
        """Reorder versions by updating their version numbers"""
        try:
            artwork = ArtWork.objects.get(id=artwork_id, author=request.user)
            version_order = request.data.get('version_order', [])
            
            if not version_order:
                return Response({'error': 'Version order data is required'}, 
                              status=status.HTTP_400_BAD_REQUEST)
            
            # Use temporary large numbers to avoid constraint violations
            # First, assign temporary large numbers (starting from 1000)
            temp_versions = []
            for index, version_id in enumerate(version_order):
                try:
                    version = artwork.versions.get(id=version_id)
                    old_version_number = version.version_number
                    temp_number = 1000 + index  # Use large numbers as temporary
                    version.version_number = temp_number
                    version.save()
                    temp_versions.append({
                        'version': version,
                        'old_number': old_version_number,
                        'new_number': len(version_order) - index,  # Final number
                        'temp_number': temp_number
                    })
                except ArtWorkVersion.DoesNotExist:
                    continue
            
            # Now assign the final version numbers
            updated_versions = []
            for version_data in temp_versions:
                version = version_data['version']
                version.version_number = version_data['new_number']
                version.save()
                updated_versions.append({
                    'id': version.id,
                    'old_number': version_data['old_number'],
                    'new_number': version_data['new_number']
                })
            
            return Response({
                'message': f'Successfully reordered {len(updated_versions)} versions',
                'updated_versions': updated_versions,
                'success': True
            })
            
        except ArtWork.DoesNotExist:
            return Response({'error': 'Artwork not found or not owned by user'}, 
                          status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def unarchive_artwork_version(request, version_id):
    """Unarchive a specific version"""
    try:
        version = ArtWorkVersion.objects.get(id=version_id, artwork__author=request.user)
        
        # Remove archive note from version notes
        if version.version_notes and '[ARCHIVED:' in version.version_notes:
            # Remove all archive notes
            lines = version.version_notes.split('\n')
            filtered_lines = [line for line in lines if not line.strip().startswith('[ARCHIVED:')]
            version.version_notes = '\n'.join(filtered_lines).strip()
            version.save()
        
        return Response({
            'message': f'Version {version.version_number} unarchived successfully',
            'success': True,
            'status': 'active',
            'version_id': version.id,
            'version_number': version.version_number
        })
    except ArtWorkVersion.DoesNotExist:
        return Response({'error': 'Version not found or not owned by user'}, 
                      status=status.HTTP_404_NOT_FOUND)

@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def delete_critique_reply(request, reply_id):
    """Delete a critique reply - allows users to delete their own replies regardless of engagement"""
    try:
        from critique.models import CritiqueReply
        reply = CritiqueReply.objects.get(id=reply_id, author=request.user)
        
        reply_text_preview = reply.text[:50] + "..." if len(reply.text) > 50 else reply.text
        reply.delete()
        
        return Response({
            'message': 'Reply deleted successfully',
            'success': True,
            'deleted_reply_preview': reply_text_preview
        })
    except CritiqueReply.DoesNotExist:
        return Response({'error': 'Reply not found or not owned by user'}, 
                      status=status.HTTP_404_NOT_FOUND)
