#!/bin/bash
# Run Django in HTTP mode with Gunicorn

# Set environment variables for HTTP mode
export SSL_ENABLED=false
export HTTP_ONLY=true

# Remove the SSL certificate options from Gunicorn
echo "Starting Django server in HTTP mode..."
exec gunicorn --bind 0.0.0.0:5000 --workers 1 --reload main:app
