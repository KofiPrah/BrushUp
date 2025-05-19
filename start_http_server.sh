#!/bin/bash
# Start the HTTP-only server for Brush Up application
# This script runs the server without SSL certificates
# which avoids the SSL errors when running in Replit

echo "Starting Brush Up in HTTP-only mode..."
python fix_server_ssl.py