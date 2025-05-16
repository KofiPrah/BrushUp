"""
Simple script to run the Django application over HTTP (no SSL).
This is needed for compatibility with Replit's load balancer.
"""

import os
import subprocess
import sys

def main():
    # Set environment variable to disable SSL
    os.environ["SSL_ENABLED"] = "false"
    
    # Define the command to run Gunicorn without SSL
    cmd = [
        "gunicorn",
        "--bind", "0.0.0.0:5000",
        "--reuse-port",
        "--reload",
        "main:app"
    ]
    
    print("Starting HTTP server (no SSL) for compatibility with Replit's load balancer")
    
    try:
        # Execute the command
        process = subprocess.run(cmd)
        sys.exit(process.returncode)
    except KeyboardInterrupt:
        print("\nServer stopped by user")
        sys.exit(0)

if __name__ == "__main__":
    main()