#!/bin/bash
# Start Art Critique in HTTP mode (no SSL)

# Set environment variables
export SSL_ENABLED=false
export SECURE_SSL_REDIRECT=false
export USE_S3=True

# Kill any existing server processes
pkill -f gunicorn || echo "No existing server processes"

echo "Starting Art Critique in HTTP mode..."
echo "Running in HTTP mode (SSL handled by Replit's load balancer)"

# Start Gunicorn without SSL certificates
exec gunicorn \
  --bind 0.0.0.0:5000 \
  --worker-class sync \
  --workers 1 \
  --reload \
  --access-logfile - \
  --error-logfile - \
  main:app
