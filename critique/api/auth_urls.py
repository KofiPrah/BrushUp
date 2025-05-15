from django.urls import path
from . import auth

urlpatterns = [
    # Authentication endpoints
    path('user/', auth.UserProfileView.as_view(), name='api-auth-user'),
    path('session/', auth.session_check, name='api-auth-session'),
    path('csrf/', auth.get_csrf_token, name='api-auth-csrf'),
    path('login/', auth.login_view, name='api-auth-login'),
    path('logout/', auth.logout_view, name='api-auth-logout'),
]