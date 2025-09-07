"""
ASGI config for Brush Up project (formerly Art Critique).

It exposes the ASGI callable as a module-level variable named ``application``.
Supports both HTTP and WebSocket protocols for real-time notifications.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os
import django
from django.core.asgi import get_asgi_application

# Initialize Django ASGI application early to ensure AppRegistry is populated
# before importing channel routes
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'artcritique.settings.prod')
django_asgi_app = get_asgi_application()

# Now import channels components after Django initialization
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from critique.routing import websocket_urlpatterns

application = ProtocolTypeRouter({
    # Django's ASGI application to handle traditional HTTP requests
    "http": django_asgi_app,
    
    # WebSocket protocol routing for real-time features
    "websocket": AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})

