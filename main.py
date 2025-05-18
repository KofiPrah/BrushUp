
#!/usr/bin/env python3
"""
HTTP-only Django app for Art Critique in Replit environment
"""
import os

# Configure Django for HTTP mode
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "artcritique.settings")
os.environ["SSL_ENABLED"] = "false"
os.environ["HTTP_ONLY"] = "true"
os.environ["HTTPS"] = "off"
os.environ["wsgi.url_scheme"] = "http"

# Import Django application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

# Create app variable for gunicorn
app = application
