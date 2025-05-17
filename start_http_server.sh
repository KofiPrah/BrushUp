#!/bin/bash
# Script to start the HTTP server without SSL for Replit compatibility

# Kill any existing gunicorn processes
pkill -9 gunicorn
pkill -9 python

# Set environment variables
export SSL_ENABLED=false
export HTTP_ONLY=true

# Start the server without SSL
echo "Starting Django app in HTTP-only mode..."
gunicorn --bind 0.0.0.0:5000 --workers 1 --reload http_server_config:app