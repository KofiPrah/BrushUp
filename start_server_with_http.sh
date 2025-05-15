#!/bin/bash
# Run Django with gunicorn in HTTP mode
# This script can be run directly: bash start_server_with_http.sh

echo "Starting server in HTTP mode (no SSL certificates)"
export SSL_ENABLED=false
killall gunicorn 2>/dev/null  # Kill any running gunicorn processes
gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app