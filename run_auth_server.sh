#!/bin/bash

# Run a dedicated HTTP server for testing authentication pages
# This allows bypassing SSL issues that can occur with the HTTPS server

# Set environment variable to disable SSL
export SSL_ENABLED=false
export ACCOUNT_DEFAULT_HTTP_PROTOCOL=http
export USE_HTTP=true

# Define the port to use
PORT=8080

echo "Starting Django server in HTTP mode on port ${PORT}"
echo "This server is specifically for previewing authentication pages"
echo "Access the server at: http://localhost:${PORT}"
echo "Press Ctrl+C to stop the server"

# Create a modified settings file for HTTP mode
cat << EOF > http_settings.py
from artcritique.settings import *

# Force HTTP protocol for development
ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'http'
USE_SSL = False
SSL_ENABLED = False

# Add the template directories explicitly
import os
TEMPLATES[0]['DIRS'] = [
    os.path.join(BASE_DIR, 'templates'),
    os.path.join(BASE_DIR, 'critique', 'templates'),
]

# Debug template loading
TEMPLATES[0]['OPTIONS']['debug'] = True
EOF

# Run the Django development server with custom settings
python manage.py runserver 0.0.0.0:${PORT} --settings=http_settings