"""
Setup script to configure Gunicorn for HTTP mode (without SSL).
This addresses the SSL protocol error with Replit's load balancer.
"""

import os
import sys
import subprocess

def main():
    """Configure and start HTTP server"""
    # Set environment variables to control application behavior
    os.environ['SSL_ENABLED'] = 'false'
    
    print("Starting HTTP server (no SSL) for Art Critique")
    
    # Build the command to run Gunicorn without SSL certificates
    cmd = [
        "gunicorn",
        "--bind", "0.0.0.0:5000",
        "--reload",
        "--worker-class", "sync",
        "--workers", "1",
        "--access-logfile", "-",
        "--error-logfile", "-",
        "main:app"
    ]
    
    print(f"Running command: {' '.join(cmd)}")
    
    # Execute the command
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error starting HTTP server: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("Server stopped by user.")

if __name__ == "__main__":
    main()