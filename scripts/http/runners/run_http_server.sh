#!/bin/bash
# Main script to run the Art Critique application in HTTP mode
# This version handles the environment setup and starts Gunicorn without SSL

# Set environment variables for HTTP mode
export SSL_ENABLED=false
export HTTP_ONLY=true

# Print header
echo "======================================================"
echo "  Starting Art Critique in HTTP Mode"
echo "  This mode is compatible with Replit's load balancer"
echo "======================================================"

# Run Gunicorn without SSL certificates
exec gunicorn --bind 0.0.0.0:5000 --workers=1 --threads=2 --reload main:app
