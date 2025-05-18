#!/usr/bin/env python3
"""
HTTP-only server script for Brush Up application in Replit
"""
import os
import subprocess

# Stop any existing server
subprocess.run("pkill -f gunicorn || true", shell=True)

# Set environment variables for HTTP mode
os.environ['HTTPS'] = 'off'
os.environ['wsgi.url_scheme'] = 'http'
os.environ['HTTP_ONLY'] = 'true'
os.environ['SSL_ENABLED'] = 'false'

# Run the server without SSL certificates
print("Starting HTTP server (no SSL)...")
cmd = [
    "gunicorn",
    "--bind", "0.0.0.0:5000",
    "--reload",
    "--access-logfile", "-",
    "--error-logfile", "-",
    "http_workflow_server:app"
]

# Start the server process
subprocess.run(cmd, env=os.environ)