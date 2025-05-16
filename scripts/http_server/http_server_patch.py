#!/usr/bin/env python
'''
Force Gunicorn to use HTTP by removing SSL certificates from configuration.
This script is used as a helper for run_patched_server.sh.
'''

import os
import sys
import logging
import ssl
import importlib
from functools import wraps

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('http_patch')

def force_gunicorn_http_mode():
    """
    Apply monkey patches to force Gunicorn to use HTTP.
    This disables SSL-related functionality so that HTTP requests
    from the Replit load balancer will be accepted.
    """
    logger.info("Forcing Gunicorn to use HTTP mode")
    
    # Patch 1: Modify SSL module behavior
    # Create a dummy SSL context that doesn't actually use SSL
    dummy_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    
    # Store the original SSLContext constructor
    original_sslcontext = ssl.SSLContext
    
    # Create a patched version that returns our dummy context
    @wraps(original_sslcontext)
    def patched_sslcontext(*args, **kwargs):
        logger.info("HTTP Patch: Returning dummy SSL context")
        return dummy_context
    
    # Apply the patch
    ssl.SSLContext = patched_sslcontext
    
    # Patch 2: Modify Gunicorn's use of certificates
    # This ensures that even if the server is started with SSL options, they're ignored
    from gunicorn import config
    original_validate_cert = getattr(config.Config, "validate_cert", lambda self, cert: True)
    
    @wraps(original_validate_cert)
    def patched_validate_cert(self, cert):
        logger.info(f"HTTP Patch: Ignoring certificate validation for {cert}")
        return True
    
    setattr(config.Config, "validate_cert", patched_validate_cert)

if __name__ == "__main__":
    force_gunicorn_http_mode()
    
    # If a command was provided, execute it
    if len(sys.argv) > 1:
        cmd = sys.argv[1:]
        logger.info(f"Executing command: {' '.join(cmd)}")
        os.execvp(cmd[0], cmd)