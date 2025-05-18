#!/usr/bin/env python3
"""
Simple HTTP server for the Brush Up application
Runs Django directly in HTTP mode without SSL certificates
"""
import os
import sys

# Configure Django for HTTP mode
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'artcritique.settings')
os.environ['HTTPS'] = 'off'
os.environ['wsgi.url_scheme'] = 'http'
os.environ['SSL_ENABLED'] = 'false'
os.environ['HTTP_ONLY'] = 'true'

# Set up Django environment
try:
    import django
    django.setup()
    
    # Update settings dynamically
    from django.conf import settings
    settings.CSRF_COOKIE_SECURE = False
    settings.SESSION_COOKIE_SECURE = False
    settings.CORS_ALLOW_CREDENTIALS = True
    
    # Log configuration
    print("Django configured for HTTP mode")
except Exception as e:
    print(f"Error setting up Django: {e}")
    sys.exit(1)

if __name__ == "__main__":
    # Run Django without SSL
    from django.core.management import execute_from_command_line
    
    # Use plain HTTP server that works with Replit
    print("Starting Brush Up in HTTP mode...")
    execute_from_command_line(["manage.py", "runserver", "0.0.0.0:5000"])