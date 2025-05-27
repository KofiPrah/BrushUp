from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CustomPageNumberPagination(PageNumberPagination):
    """
    Custom pagination class optimized for the gallery with infinite scroll.
    
    Features:
    - Configurable page size with maximum limit
    - Rich metadata for frontend pagination controls
    - Optimized for infinite scroll and "Load More" functionality
    """
    page_size = 12  # Default items per page (works well for grid layouts)
    page_size_query_param = 'page_size'
    max_page_size = 50  # Maximum items per page to prevent performance issues
    
    def get_paginated_response(self, data):
        """
        Return a paginated response with comprehensive metadata.
        """
        return Response({
            'count': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'current_page': self.page.number,
            'page_size': self.get_page_size(self.request),
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'has_next': self.page.has_next(),
            'has_previous': self.page.has_previous(),
            'start_index': self.page.start_index(),
            'end_index': self.page.end_index(),
            'results': data
        })


class LargeResultsSetPagination(PageNumberPagination):
    """
    Pagination class for handling very large datasets efficiently.
    
    Uses smaller page sizes and cursor-like behavior for optimal performance
    with thousands of artworks.
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100
    
    def get_paginated_response(self, data):
        """
        Return a streamlined response optimized for large datasets.
        """
        return Response({
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'has_next': self.page.has_next(),
            'results': data
        })


class InfiniteScrollPagination(PageNumberPagination):
    """
    Specialized pagination for infinite scroll functionality.
    
    Optimized for mobile and desktop infinite scroll experiences
    with efficient data loading.
    """
    page_size = 8  # Smaller chunks for smoother infinite scroll
    page_size_query_param = 'page_size'
    max_page_size = 24
    
    def get_paginated_response(self, data):
        """
        Return response optimized for infinite scroll UX.
        """
        has_next = self.page.has_next()
        next_page = self.page.next_page_number() if has_next else None
        
        return Response({
            'results': data,
            'has_next': has_next,
            'next_page': next_page,
            'current_page': self.page.number,
            'total_count': self.page.paginator.count,
            'loaded_count': self.page.end_index(),
            # Include next page URL for easy fetching
            'next_url': self.get_next_link(),
        })