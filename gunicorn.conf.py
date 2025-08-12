# Gunicorn configuration for Replit deployment
import os

# Port configuration - use environment variable or default to 5000
port = int(os.environ.get("PORT", 5000))
bind = f"0.0.0.0:{port}"

# Worker configuration
workers = 2
worker_class = "sync"
worker_connections = 1000

# Timeout configuration
timeout = 30
keepalive = 60

# Preload app for better performance
preload_app = True

# Enable reloading in development
reload = os.environ.get("DJANGO_DEBUG", "false").lower() == "true"

# Logging configuration
loglevel = "info"
accesslog = "-"
errorlog = "-"

# Process naming
proc_name = "artcritique"

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

print(f"Gunicorn configured to bind to {bind}")