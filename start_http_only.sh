#!/bin/bash

# HTTP-only startup script for Brush Up application
# This script ensures the application runs without SSL configuration

echo "====================================="
echo "Starting Brush Up in HTTP-only mode"
echo "====================================="

# Set environment variables to disable SSL
export SSL_ENABLED=false
export HTTP_ONLY=true
export HTTPS=off
export wsgi_url_scheme=http

# Start the application using gunicorn without SSL certificates
python -m gunicorn --bind 0.0.0.0:5000 --reload main:app