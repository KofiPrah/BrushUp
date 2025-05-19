#!/bin/bash
# Start Brush Up in HTTP-only mode
# This avoids SSL certificate errors in Replit

# Kill any existing server processes
pkill -f 'gunicorn|runserver' || true

# Create empty certificate files
echo "" > cert.pem
echo "" > key.pem

# Set environment variables for HTTP mode
export DJANGO_SETTINGS_MODULE="artcritique.settings"
export SSL_ENABLED="false"
export HTTP_ONLY="true"
export HTTPS="off"

# Start Django with gunicorn in HTTP mode
echo "Starting Brush Up in HTTP-only mode..."
exec gunicorn --bind 0.0.0.0:5000 artcritique.wsgi:application