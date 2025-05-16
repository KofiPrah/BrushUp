#!/usr/bin/env python
'''
Run the application in HTTP mode for the Replit workflow.
This script is designed to be used in the workflow configuration.
'''

import os
import sys
import subprocess

# Set environment variables for HTTP mode
os.environ["SSL_ENABLED"] = "false"
os.environ["SECURE_SSL_REDIRECT"] = "false"
os.environ["USE_S3"] = "True"

print("Starting Art Critique in HTTP mode...")
print("Running in HTTP mode (SSL handled by Replit's load balancer)")

# Command to run Gunicorn with HTTP configuration
cmd = [
    "gunicorn",
    "--bind", "0.0.0.0:5000",
    "--worker-class", "sync",
    "--workers", "1",
    "--access-logfile", "-",
    "--error-logfile", "-",
    "--reload",
    "--reuse-port",
    "main:app"
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
