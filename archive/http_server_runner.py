#!/usr/bin/env python3
"""
Simple HTTP server runner for Brush Up application
Fixes serializer issues and runs in HTTP mode for Replit compatibility
"""
import os
import sys
import subprocess

# Kill any existing gunicorn processes to free port 5000
subprocess.run("pkill -f gunicorn || true", shell=True)

# Make script executable
subprocess.run("chmod +x replit_http_server.py", shell=True)

# Start the server with explicit HTTP settings
print("Starting HTTP server without SSL certificates...")
cmd = [
    "gunicorn",
    "--bind", "0.0.0.0:5000",
    "--reload",
    "replit_http_server:app"
]

# Run the server
try:
    process = subprocess.Popen(cmd)
    print(f"Server started with PID {process.pid}")
    # Exit and let the server run
    sys.exit(0)
except Exception as e:
    print(f"Error starting server: {str(e)}")
    sys.exit(1)