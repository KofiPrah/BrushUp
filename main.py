#!/usr/bin/env python3
"""
HTTP-only server for Brush Up application
Serves Django application without SSL certificates
"""
import os
import sys

# Set environment variables for HTTP mode
os.environ['DJANGO_SETTINGS_MODULE'] = 'artcritique.settings'
os.environ['SSL_ENABLED'] = 'false'
os.environ['HTTP_ONLY'] = 'true' 
os.environ['HTTPS'] = 'off'
os.environ['wsgi.url_scheme'] = 'http'

# Import Django and run the server
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
