#!/bin/bash
# Run Brush Up application in HTTP mode (no SSL)
# Kill any existing gunicorn processes
pkill -f gunicorn || true

# Start the server in HTTP mode without SSL certificates
exec gunicorn --bind 0.0.0.0:5000 --reload main:app
