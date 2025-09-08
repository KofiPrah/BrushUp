#!/usr/bin/env python3
"""
Direct HTTP Django server for Brush Up application
Runs Django development server directly in HTTP mode
"""
import os
import sys

# Configure Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'artcritique.settings')
os.environ['SSL_ENABLED'] = 'false'
os.environ['HTTP_ONLY'] = 'true'

# Add the current directory to the path so Django can find the settings
if '' not in sys.path:
    sys.path.insert(0, '')

if __name__ == '__main__':
    # Import Django modules after setting environment variables
    from django.core.management import execute_from_command_line
    
    # Run the Django development server on all interfaces
    print("Starting Brush Up application in HTTP mode...")
    sys.argv = ['manage.py', 'runserver', '0.0.0.0:5000']
    execute_from_command_line(sys.argv)