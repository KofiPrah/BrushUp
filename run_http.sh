#!/bin/bash
# Start the application in HTTP mode (without SSL/TLS)
# This script is designed to work with Replit's load balancer

# Set HTTP mode environment variable
export SSL_ENABLED=false
export HTTP_ONLY=true

# Run Gunicorn without SSL certificates
echo "Starting server in HTTP mode (SSL handled by Replit's load balancer)..."
exec gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app