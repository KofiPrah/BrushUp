#!/bin/bash
# Kill any existing server processes
pkill -f gunicorn || true
pkill -f "python manage.py runserver" || true

# Run the HTTP server
python run_fixed_server.py
