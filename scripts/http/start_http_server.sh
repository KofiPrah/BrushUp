#!/bin/bash
# Start the server in HTTP mode without SSL certificates
# This is needed for compatibility with Replit's load balancer which
# handles the SSL termination.

# Set environment variables
export SSL_ENABLED=false
export SECURE_SSL_REDIRECT=false

echo "Starting server in HTTP mode..."
gunicorn --bind 0.0.0.0:5000 --workers 1 --reload --reuse-port main:app