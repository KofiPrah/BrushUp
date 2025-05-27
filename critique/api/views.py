from rest_framework import viewsets, permissions, status, filters, parsers
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.db import models
from critique.models import ArtWork, Profile, Critique, Reaction, Notification, CritiqueReply
from .serializers import (
    UserSerializer, ProfileSerializer, ProfileUpdateSerializer, ArtWorkSerializer, 
    ArtWorkListSerializer, CritiqueSerializer, CritiqueListSerializer,
    ReactionSerializer, NotificationSerializer, CritiqueReplySerializer
)
from .permissions import (
    IsAuthorOrReadOnly, IsOwnerOrReadOnly, IsModeratorOrOwner, 
    IsModeratorOrAdmin, IsAdminOnly
)
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
    Only authenticated users can create artworks.
    
    Permissions:
    - Anyone can view artworks (GET)
    - Only authenticated users can create artworks (POST)
    - Only the artwork's author can update it (PUT/PATCH)
    - Only the artwork's author or users with MODERATOR/ADMIN role can delete it (DELETE)
    
    For image uploads:
    - POST to /api/artworks/ with multipart/form-data
    - Include 'image' field with the image file
    - Other fields (title, description, etc.) can be included in the same request
    """
    queryset = ArtWork.objects.all().order_by('-created_at')
    serializer_class = ArtWorkSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'tags', 'author__username']
    ordering_fields = ['created_at', 'updated_at', 'title']
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]
    
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
    """API endpoint for viewing and editing critiques.
    
    Allows list, retrieve, create, update, and delete operations on critiques.
    
    Permissions:
    - Anyone can view critiques (GET)
    - Only authenticated users can create critiques (POST)
    - Only the critique's author can update it (PUT/PATCH)
    - Only the critique's author or users with MODERATOR/ADMIN role can delete it (DELETE)
    - Only the artwork's author can hide critiques (POST to /api/critiques/{id}/hide/)
    - Only users with MODERATOR/ADMIN role can flag critiques as inappropriate (POST to /api/critiques/{id}/flag/)
    """
    queryset = Critique.objects.all().order_by('-created_at')
    serializer_class = CritiqueSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    search_fields = ['text']
    ordering_fields = ['created_at', 'updated_at']
    
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
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def reply(self, request, pk=None):
        """
        Add a reply to a critique.
        Only the artwork owner can reply to critiques.
        
        Example: POST /api/critiques/5/reply/
        Payload: { "text": "Thank you for your feedback!" }
        """
        critique = self.get_object()
        
        # Check if user is the artwork owner
        if request.user != critique.artwork.author:
            return Response(
                {"error": "Only the artwork owner can reply to critiques"},
                status=status.HTTP_403_FORBIDDEN
            )
        
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
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def toggle_reaction(self, request, pk=None):
        """
        Toggle a reaction on this critique.
        
        Example: POST /api/critiques/5/toggle_reaction/
        Payload: {"type": "HELPFUL"}
        
        This will create the reaction if it doesn't exist or remove it if it does,
        effectively toggling the reaction status.
        """
        critique = self.get_object()
        
        # Validate reaction type
        reaction_type = request.data.get('type')
        if not reaction_type or reaction_type not in [choice[0] for choice in Reaction.ReactionType.choices]:
            return Response(
                {"error": f"Invalid reaction type. Allowed values: {[choice[0] for choice in Reaction.ReactionType.choices]}"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Check if user already gave this reaction type to this critique
        existing_reaction = Reaction.objects.filter(
            user=request.user,
            critique=critique,
            reaction_type=reaction_type
        ).first()
        
        # Toggle reaction: remove if exists, add if doesn't
        created = False
        if existing_reaction:
            # Remove the reaction (toggle off)
            existing_reaction.delete()
        else:
            # Create the reaction (toggle on)
            Reaction.objects.create(
                user=request.user,
                critique=critique,
                reaction_type=reaction_type
            )
            created = True
        
        # Get updated reaction counts
        critique_serializer = CritiqueSerializer(critique, context={'request': request})
        
        response_data = {
            'created': created,
            'reaction_type': reaction_type,
            'critique_id': critique.id,
            'helpful_count': critique_serializer.get_helpful_count(critique),
            'inspiring_count': critique_serializer.get_inspiring_count(critique),
            'detailed_count': critique_serializer.get_detailed_count(critique),
            'user_reactions': critique_serializer.get_user_reactions(critique)
        }
            
        return Response(response_data, status=status.HTTP_200_OK)
        
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def react(self, request, pk=None):
        """
        Add a reaction to this critique.
        
        Example: POST /api/critiques/5/react/
        Payload: {"reaction_type": "HELPFUL"}
        
        Note: This endpoint is deprecated. Use toggle_reaction instead.
        """
        critique = self.get_object()
        
        # Validate reaction type
        reaction_type = request.data.get('reaction_type')
        if not reaction_type or reaction_type not in [choice[0] for choice in Reaction.ReactionType.choices]:
            return Response(
                {"error": f"Invalid reaction_type. Allowed values: {[choice[0] for choice in Reaction.ReactionType.choices]}"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Check if user already gave this reaction type to this critique
        existing = Reaction.objects.filter(
            user=request.user,
            critique=critique,
            reaction_type=reaction_type
        ).exists()
        
        if existing:
            return Response(
                {"error": f"You have already given a {reaction_type} reaction to this critique."},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Create the reaction
        reaction = Reaction.objects.create(
            user=request.user,
            critique=critique,
            reaction_type=reaction_type
        )
        
        # Get updated reaction counts
        critique_serializer = CritiqueSerializer(critique, context={'request': request})
        
        response_data = {
            'reaction': ReactionSerializer(reaction, context={'request': request}).data,
            'helpful_count': critique_serializer.get_helpful_count(critique),
            'inspiring_count': critique_serializer.get_inspiring_count(critique),
            'detailed_count': critique_serializer.get_detailed_count(critique)
        }
        
        return Response(response_data, status=status.HTTP_201_CREATED)
        
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