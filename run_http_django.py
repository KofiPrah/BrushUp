#!/usr/bin/env python3
"""
HTTP-only Django starter script for Brush Up

This script runs Django directly using the development server
without requiring SSL certificates, suitable for Replit's environment.
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

def main():
    """Run Django in HTTP mode"""
    # Run Django development server directly
    cmd = [sys.executable, "manage.py", "runserver", "0.0.0.0:5000"]
    print(f"Starting Django HTTP server with: {' '.join(cmd)}")
    subprocess.run(cmd)

if __name__ == "__main__":
    main()