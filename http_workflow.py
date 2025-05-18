#!/usr/bin/env python3
"""
HTTP-specific gunicorn configuration for Replit
"""
import os
import sys
from gunicorn.app.wsgiapp import run

# Environment variables for HTTP mode
os.environ['SSL_ENABLED'] = 'false'
os.environ['HTTP_ONLY'] = 'true'
os.environ['HTTPS'] = 'off'
os.environ['wsgi.url_scheme'] = 'http'

# Override the command-line arguments to remove SSL
sys.argv = [
    'gunicorn',
    '--bind', '0.0.0.0:5000',
    '--reload',
    'main:application'
]

if __name__ == '__main__':
    run()
