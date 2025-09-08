#!/usr/bin/env python3
"""
Special HTTP-only runner for Brush Up application in Replit

This script runs a standard Django development server without SSL
to work properly in Replit's environment.
"""
import os
import sys

# Configure environment variables for Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "artcritique.settings")
os.environ["SSL_ENABLED"] = "false"
os.environ["HTTP_ONLY"] = "true"

# Import Django's management module
from django.core.management import execute_from_command_line

if __name__ == "__main__":
    # Set up Django server arguments
    sys.argv = [sys.argv[0], "runserver", "0.0.0.0:5000"]
    
    print("Starting Brush Up (formerly Art Critique) in HTTP mode...")
    print("Server will be available at port 5000")
    
    # Run Django development server
    execute_from_command_line(sys.argv)