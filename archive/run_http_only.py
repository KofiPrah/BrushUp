#!/usr/bin/env python3
"""
Simple HTTP server for the Art Critique application
Uses regular HTTP instead of HTTPS for Replit compatibility
"""
import os
import sys

# Configure environment for HTTP mode
os.environ['DJANGO_SETTINGS_MODULE'] = 'artcritique.settings'
os.environ['SSL_ENABLED'] = 'false'
os.environ['HTTP_ONLY'] = 'true'

# Start the server on port 8080 (to avoid conflicts)
port = 8080
host = '0.0.0.0'

print(f"Starting HTTP server on http://{host}:{port}")
print("Running in HTTP mode (SSL handled by Replit's load balancer)")

# Import and run Django application
from django.core.management import execute_from_command_line
sys.argv = [sys.argv[0], "runserver", f"{host}:{port}"]
execute_from_command_line(sys.argv)