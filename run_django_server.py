#!/usr/bin/env python3
"""
Run Django directly in HTTP mode without gunicorn
"""
import os
import sys

# Set up environment variables for HTTP mode
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'artcritique.settings')
os.environ['SSL_ENABLED'] = 'false'
os.environ['HTTP_ONLY'] = 'true'
os.environ['HTTPS'] = 'off'
os.environ['wsgi.url_scheme'] = 'http'

# Import Django and run the server
if __name__ == '__main__':
    from django.core.management import execute_from_command_line
    print("Starting Django development server in HTTP mode...")
    execute_from_command_line(['manage.py', 'runserver', '0.0.0.0:5000'])