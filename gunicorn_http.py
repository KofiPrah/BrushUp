"""
HTTP-only Gunicorn configuration for Brush Up
"""
# Server socket
bind = "0.0.0.0:5000"
backlog = 2048

# Worker processes
workers = 3
worker_class = "sync"
worker_connections = 1000
timeout = 120
keepalive = 5

# Server mechanics
daemon = False
raw_env = [
    "SSL_ENABLED=false",
    "HTTP_ONLY=true",
    "HTTPS=off",
    "wsgi.url_scheme=http"
]

# Logging
loglevel = "info"
accesslog = "-"
errorlog = "-"

# Don't use SSL certificate configuration
keyfile = None
certfile = None
ca_certs = None

# Process naming
proc_name = "brush-up-app"

# Server hooks
def on_starting(server):
    print("Starting HTTP-only Brush Up application (no SSL)")
    
    # Ensure database tables exist
    try:
        import django
        django.setup()
        
        # Apply CritiqueSerializer fixes
        from fix_critique_serializer import add_missing_method
        add_missing_method()
        print("✓ Added missing get_reactions_count method to CritiqueSerializer")
        
        # Verify KarmaEvent table
        from fix_karma_db import create_karma_tables
        create_karma_tables()
        print("✓ Verified KarmaEvent table exists")
    except Exception as e:
        print(f"! Error during fixes: {str(e)}")

def on_exit(server):
    print("Shutting down Brush Up application")