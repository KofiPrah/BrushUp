        """
        Two-at-a-time critique feed API views.
        Provides endpoints for the intelligent artwork pairing system with quick critique tags.
        """

        import random
        from datetime import timedelta

        from django.utils import timezone
        from django.db.models import Count, Q
        from rest_framework import viewsets, permissions, status, filters
        from rest_framework.decorators import api_view, permission_classes
        from rest_framework.response import Response
        from django_filters.rest_framework import DjangoFilterBackend

        from critique.models import ArtWork, PairSession, Tag, QuickCrit
        from .serializers import ArtworkCardSerializer, TagSerializer, QuickCritSerializer


        def _candidate_qs(user):
            """Get candidate artworks for the two-at-a-time feed."""
            # High-need (few critiques), fresh, different from user's recent engagements
            recent = timezone.now() - timedelta(days=14)
            qs = (
                ArtWork.objects.filter(
                    is_published=True,
                    visibility=ArtWork.VISIBILITY_PUBLIC,
                )
                .annotate(crit_count=Count("quick_crits"))
                .order_by("crit_count", "-created_at")
            )

            if user.is_authenticated:
                # Avoid user's own art and recently seen pairs
                seen = PairSession.objects.filter(user=user).order_by("-created_at")[:300]
                seen_ids = set(
                    list(seen.values_list("spotlight_id", flat=True))
                    + list(seen.values_list("counter_id", flat=True))
                )
                qs = qs.exclude(Q(author=user) | Q(id__in=seen_ids))

            return qs


        def _pick_pair(user):
            """Pick a pair of artworks for the critique feed."""
            qs = _candidate_qs(user)
            top_need = list(qs[:80])
            if not top_need:
                return None, None

            spotlight = random.choice(top_need)

            # Counterpoint: different author/medium if possible
            counter = (
                qs.exclude(author=spotlight.author)
                .exclude(medium=spotlight.medium)
                .exclude(id=spotlight.id)
                .first()
            )
            if not counter:
                pool = list(qs.exclude(id=spotlight.id)[:80])
                counter = random.choice(pool) if pool else None

            return spotlight, counter


        @api_view(["GET"])
        @permission_classes([permissions.IsAuthenticatedOrReadOnly])
        def feed_next_pair(request):
            """
            Get the next pair of artworks for critique with available tags.
            """
            spotlight, counter = _pick_pair(request.user)
            if not spotlight or not counter:
                return Response(
                    {
                        "pair_id": None,
                        "spotlight": None,
                        "counterpoint": None,
                        "chips": {"pro": [], "con": []},
                    }
                )

            if request.user.is_authenticated:
                PairSession.objects.create(user=request.user, spotlight=spotlight, counter=counter)

            data = {
                "pair_id": f"{spotlight.id}-{counter.id}-{int(timezone.now().timestamp())}",
                # IMPORTANT: pass request context so image_url resolves properly
                "spotlight": ArtworkCardSerializer(spotlight, context={"request": request}).data,
                "counterpoint": ArtworkCardSerializer(counter, context={"request": request}).data,
                "chips": {
                    "pro": TagSerializer(
                        Tag.objects.filter(polarity=Tag.PRO).order_by("is_system", "category", "label"),
                        many=True,
                    ).data,
                    "con": TagSerializer(
                        Tag.objects.filter(polarity=Tag.CON).order_by("is_system", "category", "label"),
                        many=True,
                    ).data,
                },
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
                user = self.request.user
                if user.is_staff:
                    return self.queryset
                # Users can see their own quick critiques and those on their artworks
                return self.queryset.filter(Q(author=user) | Q(artwork__author=user))

            def create(self, request, *args, **kwargs):
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
            filterset_fields = ["polarity", "category", "is_system"]
            search_fields = ["label"]

            def get_queryset(self):
                return Tag.objects.order_by("-is_system", "polarity", "category", "label")
