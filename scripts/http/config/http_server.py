"""
A simple HTTP server for the Art Critique application.
This server runs without SSL certificates to work with Replit's load balancer.
"""

import os
import sys
from gunicorn.app.base import BaseApplication


class GunicornApp(BaseApplication):
    """Gunicorn application for running the Art Critique server."""
    
    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super().__init__()

    def load_config(self):
        """Load the Gunicorn configuration."""
        for key, value in self.options.items():
            if key in self.cfg.settings and value is not None:
                self.cfg.set(key.lower(), value)

    def load(self):
        """Return the WSGI application."""
        return self.application


def main():
    """Run Gunicorn server with HTTP configuration"""
    
    # Import main app while setting SSL_ENABLED to False
    os.environ['SSL_ENABLED'] = 'false'
    from main import app
    
    print("Running in HTTP mode (SSL handled by Replit's load balancer)")
    
    # Configure the Gunicorn options
    options = {
        'bind': '0.0.0.0:5000',
        'workers': 1,
        'reload': True,
        'reuse_port': True,
        'accesslog': '-',  # Log to stdout
        'errorlog': '-',   # Log errors to stdout
    }
    
    GunicornApp(app, options).run()


if __name__ == '__main__':
    main()