#!/bin/bash
# Start the Art Critique application in HTTP mode with S3 storage enabled
# This works with Replit's load balancer which handles SSL termination

# Configure environment
export SSL_ENABLED=false
export SECURE_SSL_REDIRECT=false
export USE_S3=True

# Print configuration
echo "Starting Art Critique with configuration:"
echo "- HTTP mode (SSL handled by Replit's load balancer)"
echo "- S3 storage enabled for media files"

# Start Gunicorn in HTTP mode
gunicorn \
  --bind 0.0.0.0:5000 \
  --workers 1 \
  --reload \
  --reuse-port \
  --timeout 120 \
  --access-logfile - \
  --error-logfile - \
  --log-level info \
  main:app