#!/usr/bin/env python3
"""
HTTP-only Django server for Brush Up application
This script directly runs Django without SSL certificates
"""
import os
import sys

# Set environment variables for HTTP mode
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "artcritique.settings")
os.environ["HTTPS"] = "off"
os.environ["wsgi.url_scheme"] = "http"
os.environ["SSL_ENABLED"] = "false"
os.environ["HTTP_ONLY"] = "true"

if __name__ == "__main__":
    # Use Django's management commands
    from django.core.management import execute_from_command_line
    
    # Run the server on port 5000
    sys.argv = [sys.argv[0], "runserver", "0.0.0.0:5000"]
    execute_from_command_line(sys.argv)