#!/bin/bash
# Run Django server in HTTP mode (no SSL)
# This script avoids using certificates which solves the SSL PEM lib errors

# Set environment variables for HTTP mode
export SSL_ENABLED=false
export HTTP_ONLY=true

# Start the server (HTTP only, no SSL)
echo "Starting server in HTTP mode (without SSL certificates)"
gunicorn --bind 0.0.0.0:5000 --worker-class=sync --workers=1 main:app