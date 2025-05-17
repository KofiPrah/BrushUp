#!/usr/bin/env python
"""
Script to modify Django server settings and environment variables
to ensure proper operation in HTTP mode with Replit's load balancer
"""
import os

# Import the Django WSGI application for Gunicorn to use
from artcritique.wsgi import application

# Set this variable to be used by Gunicorn
app = application

# Force SSL off and HTTP mode on for compatibility
os.environ['SSL_ENABLED'] = 'false'
os.environ['HTTP_ONLY'] = 'true'

print("Server configured for HTTP mode with SSL handled by Replit load balancer")