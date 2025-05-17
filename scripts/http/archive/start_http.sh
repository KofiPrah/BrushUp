#!/bin/bash
# Start the Art Critique application in HTTP-only mode
# This script is designed for Replit's load balancer

# Set environment variables
export SSL_ENABLED=false
export HTTP_ONLY=true
export PYTHONUNBUFFERED=1

# Run Gunicorn without SSL certificates
echo "Starting Art Critique in HTTP mode (SSL handled by Replit's load balancer)..."
exec gunicorn --bind 0.0.0.0:5000 --workers=1 --threads=2 --reload main:app
