#!/usr/bin/env python3
"""
Simple HTTP-only server for Brush Up application
This script runs the Django application without SSL to fix common issues
"""

import os
import sys
import subprocess
import signal

def print_header(message):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f" {message}")
    print("=" * 60 + "\n")

def signal_handler(sig, frame):
    """Handle termination signals gracefully"""
    print("\nShutting down server...")
    sys.exit(0)

def main():
    """Main function to run the HTTP server"""
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print_header("STARTING HTTP-ONLY SERVER")
    
    # Create empty certificate files
    with open("cert.pem", "w") as f:
        f.write("")
    with open("key.pem", "w") as f:
        f.write("")
    
    # Build the command
    cmd = ["gunicorn", "--bind", "0.0.0.0:5000", "--reload", "main:app"]
    
    # Set up environment variables
    env = os.environ.copy()
    env["SSL_ENABLED"] = "false"
    env["HTTP_ONLY"] = "true"
    env["HTTPS"] = "off"
    env["wsgi.url_scheme"] = "http"
    
    # Run the server
    print_header("SERVER STARTING")
    print(f"Running command: {' '.join(cmd)}")
    
    process = subprocess.Popen(cmd, env=env)
    
    try:
        # Wait for the process to complete
        process.wait()
    except KeyboardInterrupt:
        print("\nServer shutdown requested")
        process.terminate()
    except Exception as e:
        print(f"Error: {e}")
        process.terminate()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())