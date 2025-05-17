#!/usr/bin/env python
"""
Run the Art Critique app with AWS S3 enabled in HTTP-only mode.
This script configures the application to use S3 storage while running
in HTTP mode to work with Replit's load balancer.
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
    """Run the application with S3 enabled in HTTP-only mode."""
    # Configure environment for HTTP mode and S3 storage
    os.environ["SSL_ENABLED"] = "false"
    os.environ["SECURE_SSL_REDIRECT"] = "false"
    os.environ["USE_S3"] = "True"
    
    logger.info("Starting Art Critique in HTTP mode with S3 storage enabled...")
    
    # Command to run Gunicorn
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