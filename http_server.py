"""
A simple HTTP server for the Art Critique application.
This server runs without SSL certificates to work with Replit's load balancer.
"""

import os
import sys
from gunicorn.app.wsgiapp import WSGIApplication

# Configure environment variables
os.environ["SSL_ENABLED"] = "false"

def main():
    """Run Gunicorn server with HTTP configuration"""
    # Set up the arguments for Gunicorn
    sys.argv = [
        "gunicorn",
        "--bind", "0.0.0.0:5000",
        "--reuse-port",
        "--reload",
        "main:app"
    ]
    
    # Run Gunicorn
    print("Starting HTTP server on port 5000 (no SSL)")
    print("SSL will be handled by Replit's load balancer")
    WSGIApplication().run()

if __name__ == "__main__":
    main()