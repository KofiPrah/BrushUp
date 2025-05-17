from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, UpdateView, CreateView, DeleteView
from django.http import JsonResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy, reverse
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Count, Q, Sum
from .models import ArtWork, Review, Profile, Comment, KarmaEvent
from .forms import CommentForm, ReplyForm
from .karma import award_like_karma

# Create your views here.
def index(request):
    """
    Home page view for the Art Critique application.
    Awards daily visit karma points for logged-in users.
    """
    # Count objects for display
    artwork_count = ArtWork.objects.count()
    review_count = Review.objects.count()
    
    # Award daily visit karma if user is logged in
    if request.user.is_authenticated:
        from .karma import award_daily_visit_karma
        award_daily_visit_karma(request.user)
    
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
    View for displaying details of a specific artwork including its reviews and comments.
    """
    model = ArtWork
    template_name = 'critique/artwork_detail.html'
    context_object_name = 'artwork'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add comment form to context
        context['comment_form'] = CommentForm()
        # Add reply form to context
        context['reply_form'] = ReplyForm()
        # Get only top-level comments (not replies)
        context['comments'] = self.object.comments.filter(parent=None).order_by('-created_at')
        return context

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


@login_required
def add_comment(request, pk):
    """
    View for adding comments to an artwork.
    """
    artwork = get_object_or_404(ArtWork, pk=pk)
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.artwork = artwork
            comment.author = request.user
            comment.save()
            messages.success(request, "Comment added successfully!")
        else:
            messages.error(request, "There was an error with your comment.")
    
    return redirect('critique:artwork_detail', pk=artwork.pk)


@login_required
def add_reply(request, artwork_pk, comment_pk):
    """
    View for adding replies to existing comments.
    """
    artwork = get_object_or_404(ArtWork, pk=artwork_pk)
    parent_comment = get_object_or_404(Comment, pk=comment_pk)
    
    if request.method == 'POST':
        form = ReplyForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.artwork = artwork
            reply.author = request.user
            reply.parent = parent_comment
            reply.save()
            messages.success(request, "Reply added successfully!")
        else:
            messages.error(request, "There was an error with your reply.")
    
    return redirect('critique:artwork_detail', pk=artwork_pk)


@login_required
def delete_comment(request, pk):
    """
    View for deleting comments. Only comment author can delete their comments.
    """
    comment = get_object_or_404(Comment, pk=pk)
    artwork_pk = comment.artwork.pk
    
    # Check if the user is the comment author
    if comment.author != request.user:
        messages.error(request, "You don't have permission to delete this comment.")
        return redirect('critique:artwork_detail', pk=artwork_pk)
    
    if request.method == 'POST':
        comment.delete()
        messages.success(request, "Comment deleted successfully!")
    
    return redirect('critique:artwork_detail', pk=artwork_pk)


@login_required
def like_artwork(request, pk):
    """
    View for liking/unliking an artwork.
    If the user has already liked the artwork, unlike it.
    If the user hasn't liked the artwork, like it.
    
    Supports both GET and POST requests, but POST is preferred for security.
    """
    artwork = get_object_or_404(ArtWork, pk=pk)
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    # Only allow POST and GET methods
    if request.method not in ['POST', 'GET']:
        if is_ajax:
            return JsonResponse({'error': 'Method not allowed'}, status=405)
        messages.error(request, "Method not allowed.")
        return redirect('critique:artwork_detail', pk=pk)
    
    # Check if user already likes this artwork
    if request.user in artwork.likes.all():
        # Remove the like
        artwork.likes.remove(request.user)
        liked = False
        messages.success(request, "You unliked this artwork.")
    else:
        # Add the like
        artwork.likes.add(request.user)
        liked = True
        # Award karma for liking
        award_like_karma(artwork, request.user)
        messages.success(request, "You liked this artwork!")
    
    # Handle AJAX requests
    if is_ajax:
        return JsonResponse({
            'liked': liked,
            'total_likes': artwork.total_likes(),
            'message': "Artwork unliked." if not liked else "Artwork liked!"
        })
    
    # For non-AJAX requests, redirect back to the artwork detail page
    return redirect('critique:artwork_detail', pk=pk)


@login_required
def karma_view(request):
    """
    View to display user's karma points and karma history.
    """
    # Get karma events for the current user
    karma_events = KarmaEvent.objects.filter(user=request.user).order_by('-created_at')[:50]
    
    # Calculate karma statistics
    karma_by_category = KarmaEvent.objects.filter(user=request.user).values('action').annotate(
        total=Sum('points'),
        count=Count('id')
    ).order_by('-total')
    
    # Get total karma
    total_karma = request.user.profile.karma
    
    context = {
        'karma_events': karma_events,
        'karma_by_category': karma_by_category,
        'total_karma': total_karma,
    }
    
    return render(request, 'critique/karma_detail.html', context)


def karma_leaderboard(request):
    """
    View to display top users by karma points.
    """
    # Get top users by karma points
    top_profiles = Profile.objects.select_related('user').order_by('-karma')[:20]
    
    # Get user's rank if logged in
    user_rank = None
    if request.user.is_authenticated:
        higher_karma_count = Profile.objects.filter(karma__gt=request.user.profile.karma).count()
        user_rank = higher_karma_count + 1  # Add 1 because ranks start at 1, not 0
    
    context = {
        'top_profiles': top_profiles,
        'user_rank': user_rank,
    }
    
    return render(request, 'critique/karma_leaderboard.html', context)
