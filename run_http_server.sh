#!/bin/bash
# Script to run Django with Gunicorn in HTTP mode
# Sets environment variables to disable SSL and uses HTTP-only mode

export SSL_ENABLED=false
export HTTP_ONLY=true

echo "Starting Art Critique in HTTP-only mode..."
exec gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app
