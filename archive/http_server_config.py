"""
HTTP server configuration for Art Critique
Handles HTTP requests in Replit environment
"""
import os

# Set environment variables for HTTP mode
os.environ["SSL_ENABLED"] = "false"
os.environ["HTTP_ONLY"] = "true"

# Import Django WSGI application
from artcritique.wsgi import application as django_app

# Create WSGI app
app = django_app

print("Art Critique server configured for HTTP mode")