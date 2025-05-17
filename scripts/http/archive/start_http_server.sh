#!/bin/bash
# Start the Art Critique application in HTTP mode
# This script is designed for Replit's load balancer

# Set environment variables
export SSL_ENABLED=false
export HTTP_ONLY=true

# Run Gunicorn with our HTTP main module
echo "Starting Art Critique in HTTP-only mode..."
exec gunicorn --bind 0.0.0.0:5000 --reuse-port --reload http_main:app