#!/usr/bin/env python3
"""
Simple HTTP server for the Brush Up application (formerly Art Critique)
Works with Replit's environment without requiring SSL
"""
import os
import sys

# Configure environment for HTTP mode
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "artcritique.settings")
os.environ["HTTPS"] = "off"
os.environ["wsgi.url_scheme"] = "http"
os.environ["SSL_ENABLED"] = "false"
os.environ["HTTP_ONLY"] = "true"

# Make sure Django settings are properly configured
try:
    import django
    django.setup()
    
    # Add CORS settings to ensure API works properly
    from django.conf import settings
    settings.CORS_ALLOW_ALL_ORIGINS = True
    settings.CORS_ALLOW_CREDENTIALS = True
    settings.CSRF_COOKIE_SECURE = False
    settings.SESSION_COOKIE_SECURE = False
    
    # Print confirmation
    print("Django configured for HTTP mode")
except Exception as e:
    print(f"Error setting up Django: {e}")
    sys.exit(1)

if __name__ == "__main__":
    # Use Django's management commands
    from django.core.management import execute_from_command_line
    
    # Run the server directly without SSL 
    print("Starting Brush Up HTTP server...")
    execute_from_command_line(["manage.py", "runserver", "0.0.0.0:5000"])