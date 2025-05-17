#!/bin/bash
# Run the Art Critique application with HTTP mode
# This script works around the SSL issue with Replit's load balancer

# Force HTTP mode
export SSL_ENABLED=false
export HTTP_ONLY=true

# Run Gunicorn with the fixed configuration
echo "Starting Art Critique in HTTP-only mode..."
echo "This is compatible with Replit's load balancer which handles SSL"

# Run Gunicorn without SSL certificates
exec gunicorn --bind 0.0.0.0:5000 --reload main:app