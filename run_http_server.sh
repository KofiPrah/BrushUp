#!/bin/bash
# HTTP server starter for Brush Up without SSL certificates

# Kill any existing gunicorn processes
pkill -f gunicorn || true

# Start the server in HTTP mode
exec gunicorn --bind 0.0.0.0:5000 --reload main:app