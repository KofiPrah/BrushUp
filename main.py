#!/usr/bin/env python3
"""
Main entry point for Art Critique application
Configured for HTTP mode to work with Replit's load balancer
"""
import os
import sys

# Configure for HTTP mode (SSL handled by Replit load balancer)
os.environ["SSL_ENABLED"] = "false"
os.environ["HTTP_ONLY"] = "true"
os.environ["DJANGO_SETTINGS_MODULE"] = "artcritique.settings"

# Import the Django WSGI application
from artcritique.wsgi import application

# Export for Gunicorn
app = application

if __name__ == "__main__":
    print("Starting Art Critique application in HTTP mode...")
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)