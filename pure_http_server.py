#!/usr/bin/env python3
"""
Pure HTTP server for Brush Up in Replit

This script runs Django without SSL in a way that works with Replit's environment
"""
import os
import sys
import subprocess

def main():
    """Run Django in HTTP mode"""
    print("Starting Brush Up (formerly Art Critique) in pure HTTP mode...")
    
    # Set environment variables
    os.environ["SSL_ENABLED"] = "false"
    os.environ["HTTP_ONLY"] = "true"
    os.environ["DJANGO_SETTINGS_MODULE"] = "artcritique.settings"
    
    # Run gunicorn with explicit HTTP (no SSL certificates)
    cmd = [
        "gunicorn",
        "--bind", "0.0.0.0:5000",
        "--workers", "1",
        "--timeout", "120",
        "--reload",
        # Important: No certificate files here
        "artcritique.wsgi:application"
    ]
    
    # Run the server
    subprocess.run(cmd)

if __name__ == "__main__":
    main()