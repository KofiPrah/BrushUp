#!/bin/bash
# Run Django in HTTP-only mode
export SSL_ENABLED=false
export HTTP_ONLY=true
export DJANGO_SETTINGS_MODULE=artcritique.settings

echo "Starting Art Critique in HTTP mode..."
gunicorn --bind 0.0.0.0:5000 artcritique.wsgi:application
