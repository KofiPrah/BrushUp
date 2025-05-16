#!/usr/bin/env python
'''
Run the Django application in HTTP mode, with no SSL.
This is specifically designed for environments where SSL termination is handled by a load balancer.
'''

import os
import sys
import subprocess
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Set environment variables for HTTP mode
os.environ["SSL_ENABLED"] = "false"
os.environ["SECURE_SSL_REDIRECT"] = "false"
os.environ["USE_S3"] = "True"

def run_http_server():
    """Run Gunicorn in HTTP mode (no SSL)"""
    logger.info("Starting Art Critique in HTTP mode...")
    logger.info("Running in HTTP mode (SSL handled by Replit's load balancer)")
    
    # Command to run Gunicorn with HTTP configuration (no SSL)
    cmd = [
        "gunicorn",
        "--bind", "0.0.0.0:5000",
        "--worker-class", "sync",
        "--workers", "1",
        "--access-logfile", "-",
        "--error-logfile", "-",
        "--reload",
        "--reuse-port",
        "main:app"
    ]
    
    try:
        # Execute the command
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to start HTTP server: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        sys.exit(0)

if __name__ == "__main__":
    run_http_server()