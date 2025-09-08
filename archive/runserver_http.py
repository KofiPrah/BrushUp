#!/usr/bin/env python3
"""
Django development server without SSL for Brush Up
"""
import os
import sys

# Set environment variables for HTTP mode
os.environ['DJANGO_SETTINGS_MODULE'] = 'artcritique.settings'
os.environ['SSL_ENABLED'] = 'false'
os.environ['HTTP_ONLY'] = 'true'
os.environ['DJANGO_DEBUG'] = 'true'

if __name__ == "__main__":
    from django.core.management import execute_from_command_line
    
    # Run Django server directly
    sys.argv = ['manage.py', 'runserver', '0.0.0.0:5000']
    execute_from_command_line(sys.argv)
