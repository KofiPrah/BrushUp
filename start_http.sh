#!/bin/bash
# Simple shell script to run Django without SSL certificates
export SSL_ENABLED=false
export HTTP_ONLY=true
export HTTPS=off
export wsgi_url_scheme=http

echo "Starting Brush Up in HTTP-only mode..."
gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app