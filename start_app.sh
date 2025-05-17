#!/bin/bash
# Script to start the Art Critique application in HTTP mode
# This script uses port 8000 to avoid conflicts with port 5000

# Kill any existing gunicorn processes
pkill -9 gunicorn 2>/dev/null || true
sleep 1

echo "Starting Art Critique in HTTP mode on port 8000..."
gunicorn --bind 0.0.0.0:8000 --reload gunicorn_no_ssl:app