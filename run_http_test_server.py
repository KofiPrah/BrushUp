"""
Simple HTTP server to test image upload functionality
"""
import os
from gunicorn.app.base import BaseApplication

class SimpleGunicornApp(BaseApplication):
    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super().__init__()

    def load_config(self):
        for key, value in self.options.items():
            if key in self.cfg.settings and value is not None:
                self.cfg.set(key.lower(), value)

    def load(self):
        return self.application

def main():
    """Start a simple HTTP server for testing"""
    # Import Flask application 
    from artcritique.wsgi import application
    
    # Get the port from environment or use default
    port = os.environ.get("PORT", "5000")
    
    # Configure Gunicorn with HTTP
    options = {
        "bind": f"0.0.0.0:{port}",
        "workers": 1,
        "timeout": 120,
        "reload": True,
    }
    
    print(f"Starting HTTP server on port {port}")
    print("This server runs without SSL for testing purposes")
    
    SimpleGunicornApp(application, options).run()

if __name__ == "__main__":
    main()