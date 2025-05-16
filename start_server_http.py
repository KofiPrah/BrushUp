#!/usr/bin/env python
"""
Start the Art Critique server in HTTP mode (no SSL).
This script is used to work around issues with Replit's load balancer
which handles SSL termination, so we don't need to use certificates.
"""

import os
import sys
import subprocess

def main():
    """Start the server in HTTP mode (no SSL)"""
    # Set environment variable to disable SSL
    os.environ["SSL_ENABLED"] = "false"
    
    # Start Gunicorn with HTTP configuration
    cmd = [
        "gunicorn",
        "--bind", "0.0.0.0:5000",
        "--reuse-port",
        "--reload",
        "main:app"
    ]
    
    print("Starting Art Critique server in HTTP mode...")
    print(f"Command: {' '.join(cmd)}")
    subprocess.run(cmd)

if __name__ == "__main__":
    main()