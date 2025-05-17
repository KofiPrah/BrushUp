#!/bin/bash
# Run Django development server directly

# Set environment variables for HTTP mode
export SSL_ENABLED=false
export HTTP_ONLY=true
export DJANGO_SETTINGS_MODULE=artcritique.settings

echo "Starting Django development server..."
python manage.py runserver 0.0.0.0:5000
