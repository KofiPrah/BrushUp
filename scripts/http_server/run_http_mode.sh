#!/bin/bash
# Run the Art Critique application in HTTP mode

# Set environment variables
export SSL_ENABLED=false
export SECURE_SSL_REDIRECT=false
export USE_S3=True

# Stop any existing server
pkill -f gunicorn || echo "No existing server processes"

# Start Gunicorn in HTTP mode
echo "Starting Art Critique in HTTP mode..."
echo "Running in HTTP mode (SSL handled by Replit's load balancer)"

exec gunicorn --bind 0.0.0.0:5000 --worker-class sync --workers 1 --reload --reuse-port main:app
