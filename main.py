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

# Apply serializer fixes
try:
    from fix_critique_serializer import add_missing_method
    add_missing_method()
    print("✓ Successfully fixed CritiqueSerializer")
except Exception as e:
    print(f"! Error fixing serializer: {str(e)}")

# Get Django application
from django.core.wsgi import get_wsgi_application
app = get_wsgi_application()  # Named 'app' to match workflow expectations
