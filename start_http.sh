#!/bin/bash

# Force HTTP mode
export SSL_ENABLED=false
export HTTP_ONLY=true

# Start gunicorn in HTTP mode (no SSL certificates)
exec gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app