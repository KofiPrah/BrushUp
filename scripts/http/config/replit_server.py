#!/usr/bin/env python
"""
Replit-specific server script that works with Replit's load balancer.
This handles the SSL termination at the load balancer level without
requiring SSL certificates in the application itself.
"""

import os
import sys
import django
import logging
from gunicorn.app.base import BaseApplication

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Add the project path to sys.path
PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_PATH)

# Set Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "artcritique.settings")

# Configure environment for HTTP mode
os.environ["SSL_ENABLED"] = "false"
os.environ["USE_HTTP"] = "true"
os.environ["SECURE_SSL_REDIRECT"] = "false"

# Initialize Django
logger.info("Initializing Django in HTTP mode")
django.setup()

# Explicitly configure Django settings for HTTP mode
from django.conf import settings
settings.SECURE_SSL_REDIRECT = False
settings.CSRF_COOKIE_SECURE = False
settings.SESSION_COOKIE_SECURE = False


class GunicornApp(BaseApplication):
    """Custom Gunicorn Application for Replit"""
    
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
    """Run the Replit server"""
    logger.info("Starting Art Critique server in HTTP mode for Replit")
    
    # Import the Django WSGI application
    from artcritique.wsgi import application
    
    # Configure Gunicorn options for HTTP mode
    options = {
        'bind': '0.0.0.0:5000',
        'workers': 2,
        'reload': True,
        'reuse_port': True,
        'timeout': 120,
        'accesslog': '-',
        'errorlog': '-',
        'loglevel': 'info',
        # Explicitly disable SSL
        'certfile': None,
        'keyfile': None,
    }
    
    # Run the Gunicorn server
    GunicornApp(application, options).run()


if __name__ == "__main__":
    main()