#!/bin/bash
# Run Django app in HTTP mode (no SSL)

# Set environment variables
export SSL_ENABLED="false"
export HTTP_ONLY="true"
export PORT=5000

echo "Starting Art Critique in HTTP mode on port $PORT"
echo "================================================="

# Run Gunicorn without SSL certificates
exec gunicorn --bind "0.0.0.0:$PORT" --reuse-port --reload main:app