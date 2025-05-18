#!/usr/bin/env python3
"""
Configure Django application to run in HTTP mode
This script removes SSL certificates from gunicorn configuration
"""
import os

# Set environment variables for HTTP mode
os.environ["SSL_ENABLED"] = "false"
os.environ["HTTP_ONLY"] = "true"
os.environ["DJANGO_SETTINGS_MODULE"] = "artcritique.settings"

# Import the Django WSGI application
from artcritique.wsgi import application

# Export app variable for Gunicorn
app = application

if __name__ == "__main__":
    print("HTTP configuration applied for Art Critique")
    print("The application is configured to run in HTTP mode")
    print("Use gunicorn without SSL certificates")