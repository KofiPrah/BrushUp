#!/usr/bin/env python3
"""
Simple HTTP-only server for the Brush Up application

This script runs Django directly without SSL certificates
to work properly in Replit's environment
"""
import os
import sys

# Configure environment for HTTP mode
os.environ['DJANGO_SETTINGS_MODULE'] = 'artcritique.settings'
os.environ['SSL_ENABLED'] = 'false'
os.environ['HTTP_ONLY'] = 'true'

# Start the server
port = 5000
host = '0.0.0.0'

print(f"Starting HTTP server on http://{host}:{port}")
print("Running in HTTP mode for Replit compatibility")

# Import and run Django application
from django.core.management import execute_from_command_line
sys.argv = [sys.argv[0], "runserver", f"{host}:{port}"]
execute_from_command_line(sys.argv)