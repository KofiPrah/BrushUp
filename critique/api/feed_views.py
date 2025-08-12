"""
Two-at-a-time critique feed API views.
Provides endpoints for the intelligent artwork pairing system with quick critique tags.
"""

import random
from datetime import timedelta
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Count, Q, F
from django_filters.rest_framework import DjangoFilterBackend

from critique.models import ArtWork, PairSession, Tag, QuickCrit, QuickCritTag
from .serializers import ArtworkCardSerializer, TagSerializer, QuickCritSerializer


def _candidate_qs(user):
    """Get candidate artworks for the two-at-a-time feed."""
    # High-need (few critiques), fresh, different from user's recent engagements
    recent = timezone.now() - timedelta(days=14)
    qs = (ArtWork.objects.filter(
            is_published=True, 
            visibility=ArtWork.VISIBILITY_PUBLIC
        )
        .annotate(crit_count=Count("quick_crits"))
        .order_by("-created_at")
    )

    if user.is_authenticated:
        # Avoid user's own art and recently seen pairs
        seen_ids = PairSession.objects.filter(user=user).order_by("-created_at").values_list("spotlight_id", flat=True)[:200]
        seen2_ids = PairSession.objects.filter(user=user).order_by("-created_at").values_list("counter_id", flat=True)[:200]
        qs = qs.exclude(Q(author=user) | Q(id__in=seen_ids) | Q(id__in=seen2_ids))

    return qs


def _pick_pair(user):
    """Pick a pair of artworks for the critique feed."""
    qs = _candidate_qs(user)

    # Score = need_weight * freshness * diversity; here we approximate with ordering & random
    top_need = list(qs.order_by("crit_count", "-created_at")[:80])
    if not top_need:
        return None, None
    
    spotlight = random.choice(top_need)

    # Counterpoint: different author/style/medium if possible
    counter = (qs.exclude(author=spotlight.author)
                 .exclude(medium=spotlight.medium)
                 .exclude(id=spotlight.id)
                 .order_by("crit_count", "-created_at")
                 .first())
    
    if not counter:
        # Fallback
        pool = list(qs.exclude(id=spotlight.id)[:80])
        counter = random.choice(pool) if pool else None
    
    return spotlight, counter


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticatedOrReadOnly])
def feed_next_pair(request):
    """
    Get the next pair of artworks for critique with available tags.
    
    Returns a JSON response with:
    - pair_id: Unique identifier for this pairing session
    - spotlight: Primary artwork for focus
    - counterpoint: Secondary artwork for comparison  
    - chips: Available pro/con tags for quick critique
    """
    spotlight, counter = _pick_pair(request.user)
    if not spotlight or not counter:
        return Response({
            "pair_id": None, 
            "spotlight": None, 
            "counterpoint": None, 
            "chips": {"pro": [], "con": []}
        })

    if request.user.is_authenticated:
        PairSession.objects.create(user=request.user, spotlight=spotlight, counter=counter)

    data = {
        "pair_id": f"{spotlight.id}-{counter.id}-{int(timezone.now().timestamp())}",
        "spotlight": ArtworkCardSerializer(spotlight).data,
        "counterpoint": ArtworkCardSerializer(counter).data,
        "chips": {
            "pro": TagSerializer(Tag.objects.filter(polarity=Tag.PRO).order_by("is_system", "category", "label"), many=True).data,
            "con": TagSerializer(Tag.objects.filter(polarity=Tag.CON).order_by("is_system", "category", "label"), many=True).data
        }
    }
    return Response(data)


class QuickCritViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing quick critiques.
    Supports both single and batch critique creation for the two-at-a-time feed.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = QuickCritSerializer
    queryset = QuickCrit.objects.select_related("artwork", "author").all()
    
    def get_queryset(self):
        """Filter queryset based on permissions."""
        user = self.request.user
        if user.is_staff:
            return self.queryset
        # Users can see their own quick critiques and those on their artworks
        return self.queryset.filter(Q(author=user) | Q(artwork__author=user))

    def create(self, request, *args, **kwargs):
        """Allow single or batch (left/right) submissions."""
        payload = request.data
        many = isinstance(payload, list)
        
        serializer = self.get_serializer(data=payload, many=many)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for listing critique tags.
    Supports filtering by polarity, category, and search by label.
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['polarity', 'category', 'is_system']
    search_fields = ['label']
    
    def get_queryset(self):
        """Order tags by system tags first, then alphabetically."""
        return Tag.objects.order_by('-is_system', 'polarity', 'category', 'label')