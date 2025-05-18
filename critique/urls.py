from django.urls import path
from . import views

app_name = 'critique'

urlpatterns = [
    path('', views.index, name='index'),
    path('api/', views.api_root, name='api-root'),
    path('artworks/', views.ArtWorkListView.as_view(), name='artwork_list'),
    path('artworks/<int:pk>/', views.ArtWorkDetailView.as_view(), name='artwork_detail'),
    path('artworks/upload/', views.artwork_upload_view, name='artwork_upload'),
    path('artworks/<int:pk>/edit/', views.ArtWorkEditView.as_view(), name='artwork_edit'),
    path('artworks/<int:pk>/delete/', views.ArtWorkDeleteView.as_view(), name='artwork_delete'),
    path('artworks/<int:pk>/delete-confirm/', views.delete_artwork, name='artwork_delete_confirm'),
    path('artworks/<int:pk>/like/', views.like_artwork, name='like_artwork'),
    
    # Comment URLs
    path('artworks/<int:pk>/comment/', views.add_comment, name='add_comment'),
    path('artworks/<int:artwork_pk>/comment/<int:comment_pk>/reply/', views.add_reply, name='add_reply'),
    path('comments/<int:pk>/delete/', views.delete_comment, name='delete_comment'),
    
    # Critique URLs
    path('artworks/<int:artwork_id>/critique/', views.create_critique, name='create_critique'),
    path('critiques/<int:critique_id>/react/', views.toggle_reaction, name='toggle_reaction'),
    path('critiques/<int:critique_id>/react/ajax/', views.toggle_reaction_ajax, name='toggle_reaction_ajax'),
    path('critiques/<int:critique_id>/unhide/', views.unhide_critique, name='unhide_critique'),
    
    # User profile URLs
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.ProfileUpdateView.as_view(), name='profile_edit'),
    path('user/<str:username>/', views.user_profile_view, name='user_profile'),
    path('my-artworks/', views.MyArtworksListView.as_view(), name='my_artworks'),
    path('my-karma/', views.karma_view, name='my_karma'),
    path('leaderboard/', views.karma_leaderboard, name='karma_leaderboard'),
    
    # Authentication test
    path('auth-test/', views.auth_test, name='auth_test'),
]
