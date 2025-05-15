from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
from django.middleware.csrf import get_token
from django.contrib.auth import authenticate, login, logout
from .serializers import UserProfileSerializer

class UserProfileView(APIView):
    """
    API endpoint for retrieving and updating the authenticated user's profile.
    GET: Returns the currently authenticated user's details.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Return the authenticated user's details"""
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)

@api_view(['GET'])
def get_csrf_token(request):
    """
    Get a CSRF token for use with session authentication.
    This endpoint should be called before making any POST requests
    that require CSRF protection.
    """
    csrf_token = get_token(request)
    return Response({'csrfToken': csrf_token})

@api_view(['GET'])
def session_check(request):
    """
    Check if the user is authenticated via session.
    Returns user information if authenticated, otherwise returns an error status.
    """
    if request.user.is_authenticated:
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)
    return Response({'authenticated': False, 'detail': 'Not authenticated'}, 
                    status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
@permission_classes([permissions.AllowAny])  # Explicitly allow any user (even unauthenticated)
def login_view(request):
    """
    Login a user using username and password.
    Returns user information if authenticated, otherwise returns an error status.
    """
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response({'error': 'Please provide both username and password'},
                        status=status.HTTP_400_BAD_REQUEST)
                        
    user = authenticate(username=username, password=password)
    
    if user is not None:
        login(request, user)
        serializer = UserProfileSerializer(user)
        return Response({'user': serializer.data})
    else:
        return Response({'error': 'Invalid credentials'}, 
                        status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout_view(request):
    """
    Logout the current user by invalidating their session.
    """
    logout(request)
    return Response({'detail': 'Successfully logged out'})