#!/usr/bin/env python3
"""
Simple HTTP server for Brush Up application

This is a reliable HTTP-only configuration that works with Replit
by running Django without SSL certificates.
"""
import os
import sys
import subprocess

# Set environment variables for Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "artcritique.settings")
os.environ["SSL_ENABLED"] = "false"
os.environ["HTTP_ONLY"] = "true"

if __name__ == "__main__":
    print("Starting Brush Up (formerly Art Critique) in HTTP mode...")
    
    # Run Django directly
    from django.core.management import execute_from_command_line
    sys.argv = [sys.argv[0], "runserver", "0.0.0.0:5000"]
    execute_from_command_line(sys.argv)