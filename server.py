#!/usr/bin/env python3
"""
Simple HTTP server for Brush Up in Replit
Runs Django directly without SSL certificates
"""
import os
import sys
import django

# Set environment variables for HTTP mode
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'artcritique.settings')
os.environ['SSL_ENABLED'] = 'false'
os.environ['HTTP_ONLY'] = 'true'
os.environ['HTTPS'] = 'off'

# Configure Django
django.setup()

# Import after Django setup
from django.core.management import call_command

# Run the server
if __name__ == "__main__":
    print("Starting Django development server in HTTP mode...")
    call_command('runserver', '0.0.0.0:5000')