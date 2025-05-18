#!/bin/bash
# Start Brush Up application without SSL certificates
# This script is designed to be used by the Replit workflow system

# Kill any existing gunicorn processes
pkill -f gunicorn || true

# Export environment variables to ensure HTTP mode
export HTTPS="off"
export HTTP_ONLY="true"
export SSL_ENABLED="false"
export wsgi_url_scheme="http"

# Create empty certificate files if they don't exist (to satisfy workflow)
touch cert.pem
touch key.pem

# Run the Python script that fixes the serializer and starts the server in HTTP mode
exec python start_brushup.py