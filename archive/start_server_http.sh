#!/bin/bash

echo "Starting HTTP server for Art Critique (no SSL)"

# Set environment variable to enable HTTP mode
export HTTP_ONLY=true

# Run Gunicorn without SSL certificates, binding to all interfaces
exec gunicorn --bind 0.0.0.0:5000 --reuse-port --reload run_http:app