#!/bin/bash
# Deployment script for Replit Autoscale

# If PORT environment variable is not set, use default 5000
export PORT="${PORT:-5000}"

echo "Starting server on port $PORT"
gunicorn --bind "0.0.0.0:$PORT" --reuse-port main:app