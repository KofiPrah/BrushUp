#!/bin/bash
# Run the Django application in HTTP mode with Gunicorn
# This script uses a custom Gunicorn configuration for HTTP

# Set environment variables
export SSL_ENABLED=false
export HTTP_ONLY=true

# Run Gunicorn with HTTP configuration
echo "Starting Django in HTTP mode (SSL handled by Replit's load balancer)..."
exec gunicorn --config gunicorn_http.conf.py main:app
