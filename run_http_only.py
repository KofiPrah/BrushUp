#!/usr/bin/env python
"""
Run the Django application with Gunicorn in HTTP-only mode.
This script is designed to work with Replit's load balancer, which handles
SSL termination before requests reach the application.
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
    """Run the application in HTTP-only mode."""
    # Configure the environment for HTTP mode
    os.environ["SSL_ENABLED"] = "false"
    os.environ["SECURE_SSL_REDIRECT"] = "false"
    
    logger.info("Starting Gunicorn in HTTP-only mode...")
    
    # Command to run Gunicorn without SSL
    cmd = [
        "gunicorn",
        "--bind", "0.0.0.0:5000",
        "--workers", "1",
        "--reload",
        "--reuse-port",
        "--timeout", "120",
        "--access-logfile", "-",
        "--error-logfile", "-",
        "--log-level", "info",
        "main:app"
    ]
    
    logger.info(f"Command: {' '.join(cmd)}")
    
    try:
        # Execute the command
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to start Gunicorn: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        sys.exit(0)

if __name__ == "__main__":
    main()