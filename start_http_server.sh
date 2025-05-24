#!/bin/bash

# Remove SSL certificates to force HTTP mode
if [ -f cert.pem ]; then
    mv cert.pem cert.pem.backup
fi
if [ -f key.pem ]; then
    mv key.pem key.pem.backup
fi

# Create empty certificate files
touch cert.pem
touch key.pem

echo "====================================="
echo "Starting Django in HTTP-only mode..."
echo "====================================="

# Run Django development server directly
PYTHONUNBUFFERED=1 python manage.py runserver 0.0.0.0:5000