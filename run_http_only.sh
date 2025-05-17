#!/bin/bash

# Force HTTP mode
export SSL_ENABLED=false
export HTTP_ONLY=true

# Run HTTP-only server
echo "Starting HTTP-only server for Art Critique (no SSL)"
gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app