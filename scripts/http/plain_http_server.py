"""
Script to start a plain HTTP server that works with Replit's load balancer.
"""

import os
import sys
import subprocess

def main():
    """Start plain HTTP server"""
    # Set environment variable to disable SSL
    os.environ['SSL_ENABLED'] = 'false'
    
    print("Starting plain HTTP server (no SSL certificates)")
    
    # Use subprocess to run gunicorn without SSL certificates
    subprocess.run([
        "gunicorn",
        "--bind", "0.0.0.0:5000",
        "--reload",
        "--reuse-port",
        "--access-logfile", "-",
        "--error-logfile", "-",
        "main:app"
    ])

if __name__ == "__main__":
    main()