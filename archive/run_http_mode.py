#!/usr/bin/env python3
"""
A simple HTTP server for Brush Up (without SSL)
"""
import os
import sys
import subprocess

# Disable SSL certificates
os.environ['DJANGO_SETTINGS_MODULE'] = 'artcritique.settings'
os.environ['SSL_ENABLED'] = 'false'
os.environ['HTTP_ONLY'] = 'true'
os.environ['HTTPS'] = 'off'
os.environ['wsgi.url_scheme'] = 'http'

# Make sure db tables exist
try:
    from fix_database import main as fix_db
    fix_db()
    print("✓ Database tables verified")
except Exception as e:
    print(f"! Warning: Database check failed: {str(e)}")

# Run the server with gunicorn in HTTP mode (no SSL)
print("Starting HTTP server without SSL certificates...")
cmd = [
    "gunicorn",
    "--bind", "0.0.0.0:5000",
    "--reload",
    "--log-level", "debug",
    "wsgi:application"
]

try:
    # Run the command and make it replace this process
    os.execvp(cmd[0], cmd)
except Exception as e:
    print(f"Error starting server: {str(e)}")
    sys.exit(1)