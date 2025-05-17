from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, UpdateView, CreateView, DeleteView
from django.http import JsonResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy, reverse
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Count, Q, Sum
from .models import ArtWork, Review, Profile, Comment

# Create your views here.
def index(request):
    """
    Home page view for the Art Critique application.
    """
    # Count objects for display
    artwork_count = ArtWork.objects.count()
    review_count = Review.objects.count()
    
    context = {
        'artwork_count': artwork_count,
        'review_count': review_count,
        'app_name': 'Art Critique Platform',
        'app_version': '1.0.0',
    }
    
    return render(request, 'critique/index.html', context=context)

def api_root(request):
    """
    Simple JSON response for the API root to verify it's working.
    """
    data = {
        'status': 'success',
        'message': 'Welcome to the Art Critique API',
        'version': '1.0.0',
        'endpoints': {
            'artworks': '/api/artworks/',
            'reviews': '/api/reviews/',
            'users': '/api/users/',
            'health': '/api/health/',
        }
    }
    return JsonResponse(data)

def auth_test(request):
    """
    View for testing authentication functionality.
    """
    return render(request, 'critique/auth_test.html')

class ArtWorkListView(ListView):
    """
    View for displaying a list of all artworks.
    """
    model = ArtWork
    template_name = 'critique/artwork_list.html'
    context_object_name = 'artworks'
    ordering = ['-created_at']

class ArtWorkDetailView(DetailView):
    """
    View for displaying details of a specific artwork including its reviews.
    """
    model = ArtWork
    template_name = 'critique/artwork_detail.html'
    context_object_name = 'artwork'

@login_required
def profile_view(request):
    """
    View for displaying the logged-in user's profile.
    """
    profile = request.user.profile
    artworks = ArtWork.objects.filter(author=request.user).order_by('-created_at')
    
    # Get activity statistics
    reviews_count = Review.objects.filter(reviewer=request.user).count()
    likes_count = ArtWork.objects.filter(likes=request.user).count()
    
    context = {
        'profile': profile,
        'user': request.user,
        'artworks': artworks,
        'reviews_count': reviews_count,
        'likes_count': likes_count,
    }
    
    return render(request, 'critique/profile.html', context=context)

class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """
    View for updating a user's profile.
    """
    model = Profile
    template_name = 'critique/profile_edit.html'
    fields = ['bio', 'location', 'birth_date', 'profile_picture', 'website']
    success_url = reverse_lazy('critique:profile')
    
    def get_object(self, queryset=None):
        """Get the current user's profile."""
        return self.request.user.profile

@login_required
def artwork_upload_view(request):
    """
    View for displaying the artwork upload form. 
    The actual upload will be handled by the API.
    """
    return render(request, 'critique/artwork_upload.html')

class MyArtworksListView(LoginRequiredMixin, ListView):
    """
    View for displaying all artworks of the logged-in user with pagination and sorting.
    """
    model = ArtWork
    template_name = 'critique/my_artworks.html'
    context_object_name = 'artworks'
    paginate_by = 12  # Show 12 artworks per page
    
    def get_queryset(self):
        """Return only the user's artworks."""
        # Get the sort parameter, default to '-created_at' (newest first)
        sort_param = self.request.GET.get('sort', '-created_at')
        
        # Map frontend sort options to model fields
        sort_mapping = {
            'newest': '-created_at',
            'oldest': 'created_at',
            'most_likes': '-likes',  # This might need to be aggregated if using annotate
            'title_asc': 'title',
            'title_desc': '-title',
        }
        
        # If the sort parameter is in our mapping, use it, otherwise use the parameter directly
        sort_field = sort_mapping.get(sort_param, sort_param)
        
        # Get the search query parameter
        search_query = self.request.GET.get('search', '')
        
        # Start with all artworks for the current user
        queryset = ArtWork.objects.filter(author=self.request.user)
        
        # Apply search filter if provided
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) | 
                Q(description__icontains=search_query) |
                Q(tags__icontains=search_query)
            )
        
        # Apply sorting
        if sort_field == '-likes':
            # For likes, we need to use annotation since it's a ManyToMany field
            queryset = queryset.annotate(like_count=Count('likes')).order_by('-like_count')
        else:
            queryset = queryset.order_by(sort_field)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add current sort parameter to context
        context['current_sort'] = self.request.GET.get('sort', 'newest')
        
        # Add current search query to context
        context['search_query'] = self.request.GET.get('search', '')
        
        return context


class ArtWorkDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    View for deleting an artwork. This view ensures that only the owner of the artwork
    can delete it by using the UserPassesTestMixin.
    """
    model = ArtWork
    template_name = 'critique/artwork_confirm_delete.html'
    success_url = reverse_lazy('critique:my_artworks')
    context_object_name = 'artwork'
    
    def test_func(self):
        """Test that ensures only the author can delete their artwork"""
        artwork = self.get_object()
        return self.request.user == artwork.author
    
    def delete(self, request, *args, **kwargs):
        """Override delete to add a success message"""
        artwork = self.get_object()
        messages.success(self.request, f'Artwork "{artwork.title}" has been deleted.')
        return super().delete(request, *args, **kwargs)


@login_required
def delete_artwork(request, pk):
    """
    Function-based view for deleting artwork (alternative to class-based view).
    This provides a simpler interface for AJAX requests.
    """
    artwork = get_object_or_404(ArtWork, pk=pk)
    
    # Check if the user is the author
    if request.user != artwork.author:
        messages.error(request, "You don't have permission to delete this artwork.")
        return redirect('critique:artwork_detail', pk=pk)
    
    if request.method == 'POST':
        artwork_title = artwork.title
        artwork.delete()
        messages.success(request, f'Artwork "{artwork_title}" has been deleted.')
        
        # Check if the request is AJAX
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success'})
        
        return redirect('critique:my_artworks')
    
    return render(request, 'critique/artwork_confirm_delete.html', {'artwork': artwork})
