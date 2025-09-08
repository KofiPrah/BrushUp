#!/bin/bash
# HTTP-only starter script for Brush Up

# Kill existing servers
pkill -f gunicorn || true
pkill -f runserver || true

# Create empty certificate files
touch cert.pem key.pem

# Start the server without SSL certificates
exec gunicorn --bind 0.0.0.0:5000 --reload main:app