#!/usr/bin/env python3
"""
HTTP server for Art Critique (without SSL)
This script configures the Django app to run in HTTP mode,
working with Replit's load balancer.
"""
import os
import sys

# Configure environment for HTTP mode
os.environ["SSL_ENABLED"] = "false"
os.environ["HTTP_ONLY"] = "true"
os.environ["DJANGO_SETTINGS_MODULE"] = "artcritique.settings"

# Import the Django WSGI application
from artcritique.wsgi import application

# Export for Gunicorn
app = application

print("Art Critique server configured for HTTP mode (no SSL)")