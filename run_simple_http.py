"""
Simple HTTP-only server for Brush Up application
"""
import os
import sys

# Set Django to run in development mode
os.environ['DJANGO_SETTINGS_MODULE'] = 'artcritique.settings'
os.environ['DJANGO_DEVELOPMENT'] = 'true'
os.environ['PYTHONUNBUFFERED'] = '1'

# Import Django
from django.core.management import execute_from_command_line

# Print banner
print("\n" + "=" * 70)
print(" BRUSH UP - HTTP SERVER ".center(70, '='))
print("=" * 70)
print("Starting Django in HTTP-only mode...")

# Run Django development server
if __name__ == "__main__":
    sys.argv = ['manage.py', 'runserver', '0.0.0.0:5000']
    execute_from_command_line(sys.argv)