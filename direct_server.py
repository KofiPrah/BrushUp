#!/usr/bin/env python3
"""
Direct HTTP server for Brush Up application

This script runs Django directly without any proxy layers or SSL certificates.
"""
import os
import sys

# Configure Django for HTTP mode
os.environ["DJANGO_SETTINGS_MODULE"] = "artcritique.settings"
os.environ["SSL_ENABLED"] = "false"
os.environ["HTTP_ONLY"] = "true"

# Add Django app import
print("Starting Brush Up application server...")

# Import Django's command executor
from django.core.management import execute_from_command_line

# Configure to run server directly
if __name__ == "__main__":
    # Set arguments for runserver
    sys.argv = [sys.argv[0], "runserver", "0.0.0.0:5000"]
    
    # Run Django server
    execute_from_command_line(sys.argv)