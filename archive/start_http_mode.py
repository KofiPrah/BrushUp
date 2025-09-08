#!/usr/bin/env python3
"""
HTTP-only server starter that doesn't require SSL certificates
"""
import os
import sys
import subprocess

# Set environment variables for HTTP mode
os.environ['DJANGO_SETTINGS_MODULE'] = 'artcritique.settings'
os.environ['SSL_ENABLED'] = 'false'
os.environ['HTTP_ONLY'] = 'true' 
os.environ['HTTPS'] = 'off'
os.environ['wsgi.url_scheme'] = 'http'

# Run Django directly through manage.py to avoid gunicorn's SSL requirements
cmd = [sys.executable, "manage.py", "runserver", "0.0.0.0:5000"]
print(f"Starting server with command: {' '.join(cmd)}")
subprocess.run(cmd)
