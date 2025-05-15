#!/bin/bash
# Script to run the Django application using gunicorn without SSL certificates

# Export the SSL_ENABLED environment variable as false
export SSL_ENABLED=false

# Run gunicorn with the Django application
gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app