#!/bin/bash
# Run Django in HTTP-only mode

# Set environment variables
export SSL_ENABLED=false
export SECURE_SSL_REDIRECT=false
export USE_S3=True

# Kill any existing server processes
pkill -f gunicorn || echo "No existing server processes"

echo "Starting Art Critique in HTTP-only mode..."

# Start Gunicorn without SSL
exec gunicorn \
  --bind 0.0.0.0:5000 \
  --worker-class sync \
  --workers 1 \
  --reload \
  --reuse-port \
  --access-logfile - \
  --error-logfile - \
  --log-level debug \
  main:app