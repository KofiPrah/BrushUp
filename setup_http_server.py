"""
Setup script to configure Gunicorn for HTTP mode (without SSL).
This addresses the SSL protocol error with Replit's load balancer.
"""

import os
import subprocess
import sys

def main():
    """Configure and start HTTP server"""
    # Remove SSL certificates from Gunicorn command
    cmd = [
        "gunicorn",
        "--bind", "0.0.0.0:5000",
        "--reload",
        "main:app"
    ]
    
    print("Starting server in HTTP mode for compatibility with Replit's load balancer")
    print("(SSL will be handled by Replit's load balancer)")
    
    try:
        # Execute the command
        process = subprocess.run(cmd)
        sys.exit(process.returncode)
    except KeyboardInterrupt:
        print("\nServer stopped")
        sys.exit(0)

if __name__ == "__main__":
    main()