from django.urls import path
from . import views

app_name = 'critique'

urlpatterns = [
    path('', views.index, name='index'),
    path('api/', views.api_root, name='api-root'),
    path('artworks/', views.ArtWorkListView.as_view(), name='artwork_list'),
    path('artworks/<int:pk>/', views.ArtWorkDetailView.as_view(), name='artwork_detail'),
    path('artworks/upload/', views.artwork_upload_view, name='artwork_upload'),
    
    # User profile URLs
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.ProfileUpdateView.as_view(), name='profile_edit'),
    path('my-artworks/', views.MyArtworksListView.as_view(), name='my_artworks'),
    
    # Authentication test
    path('auth-test/', views.auth_test, name='auth_test'),
]
