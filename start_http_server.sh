#!/bin/bash
# Start the Django server in HTTP mode using manage.py
export SSL_ENABLED=false
export PORT=8080

echo "Starting Django server in HTTP mode on port $PORT"
echo "This can be used for testing the OAuth functionality"
echo "Press Ctrl+C to stop the server"

python manage.py runserver 0.0.0.0:$PORT
