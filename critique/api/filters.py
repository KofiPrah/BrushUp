import django_filters
from django.db import models
from critique.models import ArtWork, Critique
from django.contrib.auth.models import User


class ArtWorkFilter(django_filters.FilterSet):
    """
    Custom filter set for ArtWork model with advanced filtering capabilities
    """
    # Text search fields
    title = django_filters.CharFilter(lookup_expr='icontains', help_text="Search by artwork title")
    description = django_filters.CharFilter(lookup_expr='icontains', help_text="Search by artwork description")
    
    # Author filtering
    author = django_filters.ModelChoiceFilter(
        queryset=User.objects.all(),
        help_text="Filter by specific author"
    )
    author__username = django_filters.CharFilter(
        lookup_expr='icontains',
        help_text="Filter by author username (partial match)"
    )
    
    # Medium and tags filtering
    medium = django_filters.CharFilter(lookup_expr='icontains', help_text="Filter by medium")
    tags = django_filters.CharFilter(lookup_expr='icontains', help_text="Filter by tags")
    
    # Date range filtering
    created_after = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='gte',
        help_text="Filter artworks created after this date (YYYY-MM-DD)"
    )
    created_before = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='lte',
        help_text="Filter artworks created before this date (YYYY-MM-DD)"
    )
    
    # Popularity filtering
    min_likes = django_filters.NumberFilter(
        field_name='likes_count',
        lookup_expr='gte',
        help_text="Minimum number of likes"
    )
    min_critiques = django_filters.NumberFilter(
        field_name='critiques_count',
        lookup_expr='gte',
        help_text="Minimum number of critiques"
    )
    
    # Visibility filtering (for Phase 12 - private/public artworks)
    # This field doesn't exist yet but is prepared for future use
    # visibility = django_filters.ChoiceFilter(
    #     choices=[('public', 'Public'), ('private', 'Private')],
    #     help_text="Filter by visibility"
    # )
    
    class Meta:
        model = ArtWork
        fields = {
            'title': ['exact', 'icontains'],
            'description': ['icontains'],
            'author': ['exact'],
            'author__username': ['exact', 'icontains'],
            'medium': ['exact', 'icontains'],
            'tags': ['icontains'],
            'created_at': ['exact', 'gte', 'lte'],
        }


class CritiqueFilter(django_filters.FilterSet):
    """
    Custom filter set for Critique model
    """
    # Text search
    text = django_filters.CharFilter(lookup_expr='icontains', help_text="Search critique text")
    
    # Author filtering
    author = django_filters.ModelChoiceFilter(
        queryset=User.objects.all(),
        help_text="Filter by critique author"
    )
    author__username = django_filters.CharFilter(
        lookup_expr='icontains',
        help_text="Filter by author username"
    )
    
    # Artwork filtering
    artwork = django_filters.ModelChoiceFilter(
        queryset=ArtWork.objects.all(),
        help_text="Filter critiques for specific artwork"
    )
    artwork__title = django_filters.CharFilter(
        lookup_expr='icontains',
        help_text="Filter by artwork title"
    )
    
    # Score filtering
    min_composition_score = django_filters.NumberFilter(
        field_name='composition_score',
        lookup_expr='gte',
        help_text="Minimum composition score"
    )
    min_technique_score = django_filters.NumberFilter(
        field_name='technique_score',
        lookup_expr='gte',
        help_text="Minimum technique score"
    )
    min_originality_score = django_filters.NumberFilter(
        field_name='originality_score',
        lookup_expr='gte',
        help_text="Minimum originality score"
    )
    
    # Date filtering
    created_after = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='gte',
        help_text="Filter critiques created after this date"
    )
    created_before = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='lte',
        help_text="Filter critiques created before this date"
    )
    
    # Reaction filtering
    min_helpful_reactions = django_filters.NumberFilter(
        method='filter_by_helpful_reactions',
        help_text="Minimum number of helpful reactions"
    )
    
    def filter_by_helpful_reactions(self, queryset, name, value):
        """Custom filter method for helpful reactions count"""
        return queryset.annotate(
            helpful_count=models.Count('reactions', filter=models.Q(reactions__reaction_type='HELPFUL'))
        ).filter(helpful_count__gte=value)
    
    class Meta:
        model = Critique
        fields = {
            'text': ['icontains'],
            'author': ['exact'],
            'author__username': ['exact', 'icontains'],
            'artwork': ['exact'],
            'artwork__title': ['icontains'],
            'composition_score': ['exact', 'gte', 'lte'],
            'technique_score': ['exact', 'gte', 'lte'],
            'originality_score': ['exact', 'gte', 'lte'],
            'created_at': ['exact', 'gte', 'lte'],
            'is_hidden': ['exact'],
        }