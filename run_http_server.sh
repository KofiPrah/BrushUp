#!/bin/bash
# Kill any existing server processes
pkill -f gunicorn || true
pkill -f "python manage.py runserver" || true

# Set environment variables for HTTP mode
export SSL_ENABLED=false
export HTTP_ONLY=true
export HTTPS=off
export wsgi_url_scheme=http

# Run Django development server
python manage.py runserver 0.0.0.0:5000