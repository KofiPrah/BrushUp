#!/bin/bash
# Script to restart the Art Critique server in HTTP-only mode

echo "Stopping any existing server processes..."
pkill -f gunicorn || echo "No existing server processes found."

echo "Setting environment variables..."
export USE_S3=True
export SSL_ENABLED=false
export SECURE_SSL_REDIRECT=false

echo "Starting HTTP-only server..."
python http_only_server.py