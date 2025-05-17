"""
Simple launcher script to run the Art Critique application in HTTP mode.
This ensures compatibility with Replit's environment.
"""
import os
import sys
import subprocess

def main():
    """Run the server in HTTP mode"""
    # Force HTTP mode for compatibility with Replit's load balancer
    os.environ["SSL_ENABLED"] = "false" 
    os.environ["HTTP_ONLY"] = "true"
    
    # Run Gunicorn without SSL certificates
    cmd = [
        "gunicorn",
        "--bind", "0.0.0.0:5000",
        "--reuse-port",
        "--reload",
        "main:app"
    ]
    
    print("Starting server in HTTP mode...")
    subprocess.run(cmd)

if __name__ == "__main__":
    main()