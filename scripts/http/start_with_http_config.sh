#!/bin/bash
# Start the server using our HTTP-only Gunicorn config

export SSL_ENABLED=false
export SECURE_SSL_REDIRECT=false

echo "Starting Art Critique in HTTP mode with configuration file..."
gunicorn -c gunicorn_http_config.py main:app