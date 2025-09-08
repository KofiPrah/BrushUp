#!/usr/bin/env python3
"""
Custom Django HTTP server for Brush Up
Runs without SSL certificates for Replit compatibility
"""
import os
import sys
import signal
import subprocess

# Set environment variables
os.environ["DJANGO_SETTINGS_MODULE"] = "artcritique.settings"
os.environ["SSL_ENABLED"] = "false"
os.environ["HTTP_ONLY"] = "true"
os.environ["HTTPS"] = "off"
os.environ["wsgi.url_scheme"] = "http"

# Run Django using the "runserver" command
command = ["python", "manage.py", "runserver", "0.0.0.0:5000"]
print(f"Starting Django in HTTP mode with: {' '.join(command)}")

# Run the server
try:
    process = subprocess.Popen(command)
    process.wait()
except KeyboardInterrupt:
    # Handle graceful shutdown
    print("Shutting down server...")
    process.send_signal(signal.SIGTERM)
    process.wait()