
# Gunicorn configuration for HTTP mode
import os

bind = "0.0.0.0:5000"
workers = 2
threads = 2
reload = True

def on_starting(server):
    """Set environment variables before server starts"""
    os.environ["SSL_ENABLED"] = "false"
    os.environ["HTTP_ONLY"] = "true"
    print("Starting Gunicorn in HTTP mode (SSL handled by Replit's load balancer)")
