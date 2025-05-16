#!/bin/bash
# Run HTTP server without SSL for Art Critique

echo "Starting HTTP server for Art Critique (no SSL)"
cd "$(dirname "$0")"
python setup_http_server.py