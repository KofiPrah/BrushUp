#!/bin/bash
# Start script that uses HTTP mode for compatibility

# Set environment variables to force HTTP mode
export SSL_ENABLED="false"
export HTTP_ONLY="true"

# Start Gunicorn with HTTP mode
exec gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app