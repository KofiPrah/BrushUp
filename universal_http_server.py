"""
Universal HTTP/HTTPS server for Art Critique

This script runs the Django application with a configuration that works
correctly in the Replit environment with its load balancer.
"""
import os
import sys

# Set environment variables to work with Replit's environment
os.environ["SSL_ENABLED"] = "false"
os.environ["HTTP_ONLY"] = "true"

# Import the Django WSGI application
from artcritique.wsgi import application as django_app

# Make it available for Gunicorn
app = django_app

# Display current configuration
print("Running Art Critique in HTTP-compatible mode...")
print("SSL_ENABLED:", os.environ.get("SSL_ENABLED"))
print("HTTP_ONLY:", os.environ.get("HTTP_ONLY"))

# To run directly with Python
if __name__ == "__main__":
    from django.core.management import execute_from_command_line
    execute_from_command_line(["manage.py", "runserver", "0.0.0.0:5000"])