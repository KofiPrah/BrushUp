#!/usr/bin/env python3
"""
Main entry point for Brush Up application
Simple HTTP server without SSL to work in Replit
"""
import os
import sys

# Set up environment variables
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "artcritique.settings")
os.environ["SSL_ENABLED"] = "false"
os.environ["HTTP_ONLY"] = "true"

# Import the Django WSGI application
from artcritique.wsgi import application

# Export the application for gunicorn
app = application