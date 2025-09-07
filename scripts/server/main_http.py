"""
Simple HTTP-only main file for Brush Up application

This file bypasses SSL certificate requirements and runs Django directly
"""
import os
import sys

# Set environment variables
os.environ['DJANGO_SETTINGS_MODULE'] = 'artcritique.settings'
os.environ['PYTHONUNBUFFERED'] = '1'
os.environ['HTTP_ONLY'] = 'true'
os.environ['SSL_ENABLED'] = 'false'

# Print banner
print("\n" + "=" * 70)
print(" BRUSH UP - HTTP SERVER ".center(70, '='))
print("=" * 70)
print("Starting Django in HTTP-only mode...")

# Import Django management commands
from django.core.management import execute_from_command_line

# Run the Django development server
sys.argv = ['manage.py', 'runserver', '0.0.0.0:5000']
execute_from_command_line(sys.argv)