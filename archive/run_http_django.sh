#!/bin/bash
# Run Django without SSL certificates

# Disable SSL by setting environment variables
export SSL_ENABLED=false
export HTTP_ONLY=true

# Run the server using the plain HTTP mode
python manage.py runserver 0.0.0.0:5000
