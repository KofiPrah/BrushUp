#!/usr/bin/env python
"""
HTTP-only server for Art Critique that works with Replit's load balancer.
This script doesn't use SSL/TLS certificates since the load balancer
handles SSL termination.
"""

import os
import sys
import logging
from gunicorn.app.base import BaseApplication

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

class GunicornHTTPApp(BaseApplication):
    """Custom Gunicorn Application for HTTP-only mode"""
    
    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super().__init__()
    
    def load_config(self):
        """Load Gunicorn configuration"""
        for key, value in self.options.items():
            if key in self.cfg.settings and value is not None:
                self.cfg.set(key.lower(), value)
    
    def load(self):
        """Return the WSGI application"""
        return self.application

def main():
    """Run HTTP-only server for Art Critique"""
    # Configure environment for HTTP mode
    os.environ["SSL_ENABLED"] = "false"
    os.environ["SECURE_SSL_REDIRECT"] = "false"
    
    # Import the Flask app
    from main import app
    
    logger.info("Starting Art Critique in HTTP-only mode...")
    print("Running in HTTP mode (SSL handled by Replit's load balancer)")
    
    # Gunicorn options for HTTP-only mode
    options = {
        "bind": "0.0.0.0:5000",
        "workers": 1,
        "reload": True,
        "reuse_port": True,
        "accesslog": "-",
        "errorlog": "-",
        "loglevel": "info",
        # Disable SSL for HTTP-only mode
        "certfile": None,
        "keyfile": None
    }
    
    try:
        # Run Gunicorn with HTTP configuration
        GunicornHTTPApp(app, options).run()
    except Exception as e:
        logger.error(f"Failed to start HTTP server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()