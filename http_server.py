#!/usr/bin/env python3
"""
HTTP server for Art Critique (without SSL)
This script runs a Django application in HTTP mode to work 
with Replit's load balancer which handles SSL termination.
"""
import os
import sys

# Set environment variables to enable HTTP mode
os.environ["SSL_ENABLED"] = "false"
os.environ["HTTP_ONLY"] = "true" 
os.environ["DJANGO_SETTINGS_MODULE"] = "artcritique.settings"

# Import the Django WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

# Export for Gunicorn
app = application

if __name__ == "__main__":
    # If running directly, start a simple server
    from wsgiref.simple_server import make_server
    
    port = 8000
    print(f"Starting HTTP server on port {port}...")
    httpd = make_server('0.0.0.0', port, application)
    httpd.serve_forever()