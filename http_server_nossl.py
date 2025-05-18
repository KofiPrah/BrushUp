#!/usr/bin/env python3
"""
Pure HTTP server for Art Critique application

This script runs Django in HTTP mode (no SSL)
"""
import os
import sys
import subprocess

# Set environment variables for HTTP mode
os.environ['DJANGO_SETTINGS_MODULE'] = 'artcritique.settings'
os.environ['HTTP_ONLY'] = 'true'
os.environ['SSL_ENABLED'] = 'false'

# Use port 5000 for compatibility with Replit
host = '0.0.0.0'
port = 5000

print(f"Starting HTTP server on http://{host}:{port}")
print("Running in HTTP mode (SSL handled by Replit's load balancer)")

# Run Django server
from django.core.management import execute_from_command_line
sys.argv = ['manage.py', 'runserver', f'{host}:{port}', '--noreload']
execute_from_command_line(sys.argv)