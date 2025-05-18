#!/usr/bin/env python3
"""
HTTP-only server for Brush Up (no SSL)
"""
import os
import sys

# Configure environment for HTTP mode
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "artcritique.settings")
os.environ["SSL_ENABLED"] = "false"
os.environ["HTTP_ONLY"] = "true"
os.environ["HTTPS"] = "off"
os.environ["wsgi.url_scheme"] = "http"

# Run Django development server directly without SSL
if __name__ == "__main__":
    from django.core.management import execute_from_command_line
    print("Starting Brush Up in HTTP mode...")
    execute_from_command_line(["manage.py", "runserver", "0.0.0.0:5000"])
