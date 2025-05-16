#!/usr/bin/env python
"""
Run the Django application with Gunicorn in plain HTTP mode.
This script is needed for compatibility with Replit's load balancer.
"""

import os
import sys
import subprocess
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def main():
    """Run Gunicorn server without SSL"""
    # Set environment variables
    os.environ["SSL_ENABLED"] = "false"
    os.environ["SECURE_SSL_REDIRECT"] = "false"
    
    logger.info("Starting Gunicorn in plain HTTP mode")
    print("Running in plain HTTP mode (SSL handled by Replit's load balancer)")
    
    # Command to run Gunicorn without SSL
    cmd = [
        "gunicorn",
        "--bind", "0.0.0.0:5000",
        "--worker-class", "sync",
        "--workers", "1",
        "--reload",
        "--reuse-port",
        "--access-logfile", "-",
        "--error-logfile", "-",
        # Explicitly remove SSL options
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