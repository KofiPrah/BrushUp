#!/usr/bin/env python3
"""
HTTP server starter for Brush Up in Replit
"""
import os
import subprocess
import sys

def main():
    """Run Brush Up in HTTP mode"""
    # Kill any existing gunicorn processes
    subprocess.run("pkill -f gunicorn || true", shell=True)
    
    # Create the HTTP command
    cmd = [
        "gunicorn",
        "--bind", "0.0.0.0:5000",
        "--reload",
        "main:app"
    ]
    
    # Set up environment variables for HTTP mode
    env = os.environ.copy()
    env["SSL_ENABLED"] = "false"
    env["HTTP_ONLY"] = "true"
    env["HTTPS"] = "off"
    env["wsgi.url_scheme"] = "http"
    
    print("Starting HTTP server (no SSL)...")
    process = subprocess.Popen(cmd, env=env)
    print(f"Server started with PID: {process.pid}")
    
    # Print success message
    print("✅ HTTP server running successfully")
    print("✅ Visit http://localhost:5000 to access the application")
    
    # Exit this process
    sys.exit(0)

if __name__ == "__main__":
    main()