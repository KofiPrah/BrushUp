#!/usr/bin/env python3
"""
Pure HTTP server for Brush Up (formerly Art Critique)

This script runs Django directly without SSL certificates
for compatibility with Replit's environment.
"""
import os
import sys

# Configure environment for Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'artcritique.settings')
os.environ['SSL_ENABLED'] = 'false'
os.environ['HTTP_ONLY'] = 'true'

# Import Django's management command system
import django
from django.core.management import execute_from_command_line

if __name__ == '__main__':
    # Initialize Django
    django.setup()
    
    # Print startup message
    print("Starting Brush Up (formerly Art Critique) in HTTP mode")
    print(f"Running on: {os.environ.get('REPLIT_DOMAIN', 'localhost')}")
    
    # Run the Django development server on port 5000
    sys.argv = [sys.argv[0], 'runserver', '0.0.0.0:5000']
    execute_from_command_line(sys.argv)