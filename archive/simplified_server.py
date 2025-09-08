#!/usr/bin/env python3
"""
Simple HTTP-only server for Brush Up application in Replit
Avoids SSL certificate issues and allows proper API functionality
"""
import os
import sys
import django
from django.core.management import execute_from_command_line

# Set environment variables for HTTP mode
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "artcritique.settings")
os.environ["SSL_ENABLED"] = "false"
os.environ["HTTP_ONLY"] = "true" 
os.environ["HTTPS"] = "off"
os.environ["wsgi.url_scheme"] = "http"

# Initialize Django
django.setup()

if __name__ == "__main__":
    # Run Django development server directly without SSL
    print("Starting Brush Up with HTTP (no SSL)...")
    execute_from_command_line(["manage.py", "runserver", "0.0.0.0:5000"])