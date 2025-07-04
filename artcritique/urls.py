"""
URL configuration for Brush Up project (formerly Art Critique).

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from django.db import connection

def health_check(request):
    """Health check endpoint for deployment monitoring"""
    try:
        # Test database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        
        return JsonResponse({
            "status": "healthy",
            "database": "connected",
            "service": "artcritique"
        }, status=200)
    except Exception as e:
        return JsonResponse({
            "status": "unhealthy",
            "error": str(e),
            "service": "artcritique"
        }, status=503)

urlpatterns = [
    path('', include('critique.urls')),  # Main Brush Up art platform at root
    path('health/', health_check, name='health_check'),  # Health check moved to /health/
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('accounts/', include('allauth.urls')),
    path('api/', include('critique.api.urls')),  # DRF API endpoints
]

# Serve static and media files in all environments since we're using local storage
# This ensures media files are accessible in production as well
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
