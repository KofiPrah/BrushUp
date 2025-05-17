#!/bin/bash
# Run the Django application in HTTP mode
# This script helps ensure the application works correctly with Replit's load balancer

echo "Starting Art Critique in HTTP-only mode..."

# Set environment variables for HTTP mode
export SSL_ENABLED=false
export HTTP_ONLY=true
export DJANGO_SETTINGS_MODULE=artcritique.settings

# Run with gunicorn without SSL
gunicorn --bind 0.0.0.0:5000 --workers 1 --timeout 120 --reload artcritique.wsgi:application