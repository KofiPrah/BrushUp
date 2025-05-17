#!/bin/bash
# Start Django in HTTP mode

# Run patch script first
python fix_server.py

# Start server without SSL
echo "Starting Django app in HTTP-only mode..."
gunicorn --bind 0.0.0.0:5000 main:app
