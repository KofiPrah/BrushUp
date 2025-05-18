#!/usr/bin/env python3
"""
Configure gunicorn command for HTTP-only mode in Replit
Remove SSL certificate references
"""
import os
import sys
from gunicorn.app.wsgiapp import run

# Override the command-line arguments
sys.argv = [
    'gunicorn',
    '--bind', '0.0.0.0:5000',
    '--reload',
    'main:application'
]

if __name__ == '__main__':
    # Run gunicorn with the HTTP-specific configuration
    run()