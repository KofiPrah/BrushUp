#!/bin/bash
# Run the Art Critique application with HTTP patch

# Set environment variables
export SSL_ENABLED=false
export SECURE_SSL_REDIRECT=false
export USE_S3=True

# Kill any existing server processes
pkill -f gunicorn || echo "No existing server processes"

echo "Starting Art Critique with HTTP patch..."
echo "Running in HTTP mode (SSL handled by Replit's load balancer)"

# Run through the patch script, which will forward to gunicorn
python http_server_patch.py \
  gunicorn \
  --bind 0.0.0.0:5000 \
  --worker-class sync \
  --workers 1 \
  --reload \
  --log-level info \
  --access-logfile - \
  --error-logfile - \
  main:app