"""
HTTP-only server starter for Brush Up
This script starts the Django application without SSL certificates
"""
import os
import subprocess
import sys

def main():
    """Run the Django application with gunicorn in HTTP-only mode"""
    print("Starting Brush Up in HTTP-only mode...")
    
    cmd = [
        "gunicorn",
        "--bind", "0.0.0.0:5000",
        "--reuse-port",
        "--reload",
        "main:app"
    ]
    
    # Run the server
    process = subprocess.Popen(cmd)
    
    try:
        process.wait()
    except KeyboardInterrupt:
        print("Shutting down server...")
        process.terminate()
        process.wait()
        sys.exit(0)

if __name__ == "__main__":
    main()