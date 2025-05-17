#!/bin/bash
# Simple script to start the Django app in HTTP-only mode

# Set environment variables
export SSL_ENABLED=false
export HTTP_ONLY=true

echo "Starting Django app in HTTP-only mode..."
gunicorn --bind 0.0.0.0:5000 --config gunicorn_http_config.py main:app
