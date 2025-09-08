#!/bin/bash
# Run Django app without SSL for better compatibility

# Set environment variables
export SSL_ENABLED="false"
export HTTP_ONLY="true"

# Run gunicorn without SSL certificates
exec gunicorn --bind "0.0.0.0:5000" --reuse-port --reload main:app