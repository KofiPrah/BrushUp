#!/bin/bash
# Run Brush Up in HTTP mode

# Make sure SSL is disabled in the environment
export SSL_ENABLED=false
export HTTP_ONLY=true

# Start Django development server
echo "Starting Brush Up (formerly Art Critique) in HTTP mode..."
python manage.py runserver 0.0.0.0:5000