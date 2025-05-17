#!/bin/bash

# Set environment variables for HTTP mode
export SSL_ENABLED=false
export HTTP_ONLY=true

# Start gunicorn in HTTP mode without SSL certificates
exec gunicorn --bind 0.0.0.0:5000 --reuse-port --reload http_server_updated:app