#!/bin/bash

# Flexible server startup script that can run in either HTTP or HTTPS mode
# Usage:
#   SSL_ENABLED=true ./run_flexible_server.sh   # Run with HTTPS (default)
#   SSL_ENABLED=false ./run_flexible_server.sh  # Run with HTTP only

# Check if SSL is enabled or not
SSL_MODE="${SSL_ENABLED:-true}"

if [ "$SSL_MODE" = "true" ]; then
  # Run with SSL for local development
  echo "Starting server with SSL/HTTPS..."
  exec gunicorn --bind 0.0.0.0:5000 --certfile=cert.pem --keyfile=key.pem --reuse-port --reload main:app
else
  # Run without SSL for Replit deployment
  echo "Starting server with plain HTTP..."
  exec gunicorn --bind 0.0.0.0:${PORT:-5000} --reuse-port --reload main:app
fi