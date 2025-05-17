#!/bin/bash
# Start the server in HTTP mode for Replit compatibility

# Configure environment for HTTP mode
export SSL_ENABLED=false
export HTTP_ONLY=true
export USE_S3=True

echo "Starting Art Critique server in HTTP mode..."
echo "S3 storage is enabled"

# Run Gunicorn without SSL certificates
exec gunicorn --bind 0.0.0.0:5000 --workers=1 --threads=2 --reload main:app