#!/bin/bash
# Start the Django server in HTTP mode without SSL certificates

echo "Starting Brush Up in HTTP-only mode"
echo "This will fix the reaction button issues"

# Use the HTTP server script
gunicorn --bind 0.0.0.0:5000 --reload http_server:app