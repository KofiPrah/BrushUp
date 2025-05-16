"""
Script to start a plain HTTP server that works with Replit's load balancer.
"""

import os
import sys
import subprocess

def main():
    """Start plain HTTP server"""
    # Define the command
    cmd = [
        "gunicorn",
        "--bind", "0.0.0.0:5000", 
        # No SSL certificates
        "--reload",
        "main:app"
    ]
    
    print("Starting server with plain HTTP (SSL handled by Replit's load balancer)")
    
    # Run the command
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("Server stopped")
        sys.exit(0)

if __name__ == "__main__":
    main()