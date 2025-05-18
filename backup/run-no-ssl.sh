#!/bin/bash
# Start Brush Up application without SSL certificates

# Stop any existing servers
pkill -f gunicorn || true

# Set environment variables
export HTTP_ONLY=true
export HTTPS=off
export SSL_ENABLED=false

# Start the server without SSL certificates
echo "Starting Brush Up in HTTP mode (no SSL)..."
gunicorn --bind 0.0.0.0:5000 app:app