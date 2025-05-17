#!/bin/bash
# Run Brush Up application in HTTP mode

# Set environment variables
export SSL_ENABLED=false
export HTTP_ONLY=true
export DJANGO_SETTINGS_MODULE=artcritique.settings

# Start gunicorn without SSL certificates
gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app