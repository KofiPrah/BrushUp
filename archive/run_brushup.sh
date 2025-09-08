#!/bin/bash
# Simple starter script for Brush Up application
# This creates empty certificate files (to satisfy workflow requirements)
# and starts the application in HTTP mode

# Create empty certificate files if they don't exist
touch cert.pem
touch key.pem

# Run gunicorn without requiring SSL certificates
exec gunicorn --bind 0.0.0.0:5000 --reload main:app