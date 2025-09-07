#!/usr/bin/env python3
"""
Simple script to restart the Brush Up server in HTTP mode
This fixes SSL errors and ensures the application works properly
"""
import os
import subprocess
import signal
import sys
import time

def kill_running_servers():
    """Kill any running server processes"""
    print("Stopping any running servers...")
    subprocess.run(["pkill", "-f", "gunicorn"], stderr=subprocess.DEVNULL)
    subprocess.run(["pkill", "-f", "runserver"], stderr=subprocess.DEVNULL)
    # Give processes time to terminate
    time.sleep(1)

def setup_http_environment():
    """Set up environment variables for HTTP mode"""
    os.environ["DJANGO_SETTINGS_MODULE"] = "artcritique.settings"
    os.environ["SSL_ENABLED"] = "false"
    os.environ["HTTP_ONLY"] = "true"
    os.environ["HTTPS"] = "off"
    os.environ["wsgi.url_scheme"] = "http"
    
    # Create empty certificates to satisfy gunicorn
    print("Creating empty certificate files...")
    with open("cert.pem", "w") as f:
        f.write("")
    with open("key.pem", "w") as f:
        f.write("")

def main():
    """Run the HTTP-only server"""
    print("\n=== Starting Brush Up in HTTP-only mode ===\n")
    
    # Kill any existing server processes
    kill_running_servers()
    
    # Set up environment
    setup_http_environment()
    
    # Build the command to run Django
    cmd = [
        "python", "manage.py", "runserver", "0.0.0.0:5000"
    ]
    
    # Run the server
    print(f"Starting Django with command: {' '.join(cmd)}")
    print("\n=== Server is starting... ===\n")
    
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\nServer shutdown requested")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())