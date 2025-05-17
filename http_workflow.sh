#!/bin/bash
# Script to start the server in HTTP mode
# This is used by the workflow to ensure proper Replit compatibility

# Force HTTP mode for compatibility with Replit
export SSL_ENABLED="false"
export HTTP_ONLY="true"

# Run gunicorn without SSL certificates
exec gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app