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

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def main():
    """Run the application in HTTP-only mode."""
    # Set environment variables for HTTP mode
    os.environ["SSL_ENABLED"] = "false"
    os.environ["SECURE_SSL_REDIRECT"] = "false"
    
    # Configure S3 if enabled
    if os.environ.get("USE_S3") == "True":
        logger.info("S3 storage is enabled")
    else:
        logger.info("Using local file storage")
    
    logger.info("Starting Art Critique in HTTP-only mode...")
    print("Running in HTTP mode (SSL handled by Replit's load balancer)")
    
    # Command to run Gunicorn without SSL
    cmd = [
        "gunicorn",
        "--bind", "0.0.0.0:5000",
        "--workers", "1",
        "--reload",
        "--reuse-port",
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