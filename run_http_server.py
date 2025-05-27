#!/usr/bin/env python3
"""
Simple HTTP server for Brush Up art platform
Runs Django without SSL to avoid certificate issues
"""

import os
import sys
import django
from django.core.management import execute_from_command_line

def main():
    """Run Django development server in HTTP mode"""
    
    # Set Django settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'artcritique.settings')
    
    # Disable SSL for this run
    os.environ['SSL_ENABLED'] = 'false'
    
    # Setup Django
    django.setup()
    
    print("🎨 Starting Brush Up Art Platform")
    print("📡 Running on HTTP (port 5000)")
    print("🔗 Your art community will be accessible at your Replit URL")
    
    # Run Django development server
    sys.argv = [
        'manage.py',
        'runserver', 
        '0.0.0.0:5000'
    ]
    
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()