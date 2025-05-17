#!/usr/bin/env python
"""
Run Flask with plain HTTP server.
This script is designed to work with Replit's load balancer
which handles SSL termination before requests reach the application.
"""

import os
import sys
import subprocess
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def main():
    """Run a plain HTTP Flask server."""
    # Set environment variables for HTTP mode
    os.environ["SSL_ENABLED"] = "false"
    os.environ["SECURE_SSL_REDIRECT"] = "false"
    
    logger.info("Starting Art Critique in plain HTTP mode...")
    print("Running in plain HTTP mode (SSL handled by Replit's load balancer)")
    
    # Import app here, after environment variables are set
    from main import app
    
    # Start Flask development server without SSL
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        ssl_context=None  # Explicitly disable SSL
    )

if __name__ == "__main__":
    main()