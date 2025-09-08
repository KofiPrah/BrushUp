#!/bin/bash
# Start Brush Up application in HTTP mode (no SSL certificates)

# Set environment variables
export SSL_ENABLED=false
export HTTP_ONLY=true

# Run Django with gunicorn in HTTP mode
exec gunicorn --bind 0.0.0.0:5000 --workers 1 --timeout 120 --reload main:app
