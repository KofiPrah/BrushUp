#!/usr/bin/env python3
"""
HTTP-only server for Brush Up application in Replit

This script runs Django without SSL certificates to work in Replit's environment
(Modified to update the workflow command)
"""
import os
import sys
import subprocess

# Set up environment variables
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "artcritique.settings")
os.environ["SSL_ENABLED"] = "false"
os.environ["HTTP_ONLY"] = "true"

# Get the Replit domain if available
REPLIT_DOMAIN = os.environ.get("REPLIT_DOMAIN", "")
print(f"Brush Up running on domain: {REPLIT_DOMAIN or 'localhost'}")

# Explicitly remove SSL certificate arguments from gunicorn command
def main():
    """Run Django in HTTP mode"""
    print("Starting Brush Up in HTTP mode...")

    # Build the command with no SSL certificates
    cmd = [
        "python", "-m", "gunicorn",
        "--bind", "0.0.0.0:5000",
        "--worker-class", "sync",
        "--workers", "1",
        "--reload",
        "artcritique.wsgi:application"
    ]
    
    # Run the server
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\nShutting down server...")
    except Exception as e:
        print(f"Error running server: {e}")

if __name__ == "__main__":
    main()