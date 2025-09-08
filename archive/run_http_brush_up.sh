#!/bin/bash
# HTTP server starter for Brush Up application
# Fixes serializer issues and runs without SSL for Replit compatibility

# Make sure all required packages are installed
echo "Ensuring dependencies are installed..."

# First run the serializer fixes and database checks
python fix_serializer.py

# Start the server in HTTP mode
echo "Starting HTTP server for Brush Up..."
gunicorn --bind 0.0.0.0:5000 --reload start_http_server:app