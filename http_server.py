"""
Simple HTTP server for Brush Up application

This script runs Django directly without SSL certificates to fix the reactions issues
"""
import os
import sys
import django
from django.core.wsgi import get_wsgi_application
from django.http import HttpResponseForbidden, JsonResponse
import json

# Set environment variables
os.environ['DJANGO_SETTINGS_MODULE'] = 'artcritique.settings'
os.environ['DJANGO_INSECURE'] = 'true'
os.environ['DJANGO_DEVELOPMENT'] = 'true'

print("Starting server in HTTP mode...")

application = get_wsgi_application()

# Export the application for gunicorn
app = application