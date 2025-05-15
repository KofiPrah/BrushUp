from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, UpdateView
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from .models import ArtWork, Review, Profile

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
    
    context = {
        'profile': profile,
        'user': request.user,
        'artworks': artworks,
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
