#!/usr/bin/env python3
"""
Simple HTTP server for Brush Up application

This script runs gunicorn in HTTP-only mode to work with Replit's environment
(Updated to run without SSL certificates)
"""
import os
import sys
import subprocess

# Configure environment 
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "artcritique.settings")
os.environ["SSL_ENABLED"] = "false"
os.environ["HTTP_ONLY"] = "true"

def main():
    """Run HTTP server for Brush Up"""
    print("Starting Brush Up (formerly Art Critique) in HTTP mode...")
    
    # Run with gunicorn without SSL
    cmd = [
        "gunicorn",
        "--bind", "0.0.0.0:5000",
        "--worker-class", "sync",
        "--workers", "1",
        "--timeout", "120",
        "--reload",
        "artcritique.wsgi:application"
    ]
    
    # Run the server
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\nShutting down server...")
        sys.exit(0)

if __name__ == "__main__":
    main()