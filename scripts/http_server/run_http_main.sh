#!/bin/bash
# Run Django with HTTP-only configuration

# Kill any existing server processes
pkill -f gunicorn || echo "No existing server processes"

echo "Starting Art Critique in HTTP-only mode..."
echo "Using HTTP-only WSGI module to bypass SSL"

# Run gunicorn with our specialized HTTP-only module
exec gunicorn --bind 0.0.0.0:5000 --worker-class sync --workers 1 --reload --log-level info main_http:app