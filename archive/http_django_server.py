#!/usr/bin/env python3
"""
HTTP-only Django server for Brush Up

This script runs Django in HTTP mode without SSL certificates
to work correctly in Replit's environment.
"""
import os
import sys
import subprocess

# Configure environment
os.environ['DJANGO_SETTINGS_MODULE'] = 'artcritique.settings'
os.environ['SSL_ENABLED'] = 'false'
os.environ['HTTP_ONLY'] = 'true'

# Run Django with proper settings
port = 5000
host = '0.0.0.0'

print(f"Starting HTTP server on http://{host}:{port}")
print("Running in HTTP mode (no SSL certificates)")

# Run Django server
from django.core.management import execute_from_command_line
sys.argv = ['manage.py', 'runserver', f'{host}:{port}', '--noreload']
execute_from_command_line(sys.argv)