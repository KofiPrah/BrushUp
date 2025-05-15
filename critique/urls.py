from django.urls import path
from . import views

app_name = 'critique'

urlpatterns = [
    path('', views.index, name='index'),
    path('api/', views.api_root, name='api-root'),
    path('artworks/', views.ArtWorkListView.as_view(), name='artwork_list'),
    path('artworks/<int:pk>/', views.ArtWorkDetailView.as_view(), name='artwork_detail'),
    
    # User profile URLs
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.ProfileUpdateView.as_view(), name='profile_edit'),
    
    # Authentication test
    path('auth-test/', views.auth_test, name='auth_test'),
]
