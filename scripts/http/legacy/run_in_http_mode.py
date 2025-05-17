#!/usr/bin/env python
'''
Run the application in HTTP mode for the Replit workflow.
Handles environment variables and starts Gunicorn in HTTP-only mode.
'''

import os
import sys
import subprocess

# Set environment variables for HTTP mode
os.environ["SSL_ENABLED"] = "false"
os.environ["SECURE_SSL_REDIRECT"] = "false"
os.environ["USE_S3"] = "True"

print("Starting Art Critique in HTTP-only mode...")
print("Running in HTTP mode (SSL handled by Replit's load balancer)")

# Command to run Gunicorn with HTTP configuration
cmd = [
    "gunicorn",
    "--bind", "0.0.0.0:5000",     # Bind to all interfaces on port 5000
    "--worker-class", "sync",     # Synchronous worker class
    "--workers", "1",             # Single worker process
    "--reload",                   # Auto-reload on code changes
    "--reuse-port",               # Allow port reuse
    "--log-level", "debug",       # Detailed logging
    "--access-logfile", "-",      # Log access to stdout
    "--error-logfile", "-",       # Log errors to stdout
    "main:app"                    # WSGI application
]

try:
    # Execute the command
    subprocess.run(cmd, check=True)
except subprocess.CalledProcessError as e:
    print(f"Failed to start HTTP server: {e}")
    sys.exit(1)
except KeyboardInterrupt:
    print("Shutting down...")
    sys.exit(0)