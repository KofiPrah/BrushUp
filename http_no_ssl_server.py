#!/usr/bin/env python3
"""
HTTP-only server for Art Critique (no SSL)
This script configures and runs the Art Critique app with Gunicorn
in HTTP-only mode without SSL.
"""
import os
import sys
import subprocess

def main():
    """Configure and run HTTP server"""
    # First, configure environment
    os.environ["SSL_ENABLED"] = "false"
    os.environ["HTTP_ONLY"] = "true"
    os.environ["DJANGO_SETTINGS_MODULE"] = "artcritique.settings"
    
    print("Environment configured for HTTP-only mode")
    
    # Command to run the server without SSL
    cmd = ["gunicorn", "--bind", "0.0.0.0:5000", "--reload", 
           "--certfile=", "--keyfile=", 
           "artcritique.wsgi:application"]
    
    print(f"Starting server with command: {' '.join(cmd)}")
    
    # Execute the command
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("Server stopped")
    except Exception as e:
        print(f"Error starting server: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())