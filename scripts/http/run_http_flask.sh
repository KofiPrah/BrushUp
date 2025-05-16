#!/bin/bash
# Run the Art Critique application in HTTP mode

# Stop any existing server
pkill -f gunicorn || echo "No existing server processes"

# Set environment variables
export SSL_ENABLED=false
export SECURE_SSL_REDIRECT=false
export USE_S3=True

# Start the server
exec gunicorn -c gunicorn_http_config.py main:app
