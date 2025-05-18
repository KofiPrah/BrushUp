#!/bin/bash
# Run Brush Up application in HTTP mode with all necessary fixes

# Kill any existing processes
pkill -f "python main_http.py" || true
pkill -f "runserver" || true
pkill -f gunicorn || true

# Create empty certificate files to prevent errors
touch cert.pem key.pem

# Export environment variables to ensure HTTP mode
export HTTPS="off"
export HTTP_ONLY="true" 
export SSL_ENABLED="false"
export wsgi_url_scheme="http"

# Run the HTTP-only server
exec python main_http.py