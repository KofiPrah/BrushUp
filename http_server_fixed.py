"""
Simple HTTP server for Art Critique - Fixed SSL issues

This script runs a pure HTTP server for the Art Critique app,
making it compatible with Replit's load balancer which handles the SSL termination.
"""
import os
import sys

# Force HTTP mode environment variables
os.environ["SSL_ENABLED"] = "false"
os.environ["HTTP_ONLY"] = "true" 

# Import the Django WSGI application
from artcritique.wsgi import application

# Make this available for Gunicorn to import
app = application

if __name__ == "__main__":
    # Display configuration information
    print("SSL_ENABLED:", os.environ.get("SSL_ENABLED"))
    print("HTTP_ONLY:", os.environ.get("HTTP_ONLY"))
    print("Running in HTTP-only mode (SSL handled by Replit's load balancer)")

    # If you want to run this script directly with Python (not via Gunicorn)
    from django.core.management import execute_from_command_line
    execute_from_command_line(["manage.py", "runserver", "0.0.0.0:5000"])