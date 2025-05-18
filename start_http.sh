#!/bin/bash

# HTTP-only server for Brush Up application

echo "====================================="
echo "Starting Brush Up in HTTP-only mode"
echo "====================================="

# Set environment variables to disable SSL and use HTTP
export SSL_ENABLED=false
export HTTP_ONLY=true
export HTTPS=off
export wsgi_url_scheme=http

# Run the Django development server directly
python manage.py runserver 0.0.0.0:8000