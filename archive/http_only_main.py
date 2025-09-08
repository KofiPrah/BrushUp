"""
HTTP-only server for Brush Up application to work with Replit
"""
import os
import sys
import django
from django.core.wsgi import get_wsgi_application
from django.core.management import execute_from_command_line

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "artcritique.settings")
os.environ["HTTPS"] = "off"
os.environ["wsgi.url_scheme"] = "http"
os.environ["SSL_ENABLED"] = "false"
os.environ["HTTP_ONLY"] = "true"

# Initialize Django
django.setup()

if __name__ == '__main__':
    # Run the Django development server directly
    sys.argv = [sys.argv[0], "runserver", "0.0.0.0:5000"]
    execute_from_command_line(sys.argv)