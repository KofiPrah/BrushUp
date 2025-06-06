"""
Main entry point for Brush Up Django application
Optimized for Replit Autoscale deployment
"""

import os
import sys
import logging

# Configure basic logging for debugging deployment issues
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Set deployment environment variables
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'artcritique.settings')
os.environ.setdefault('SSL_ENABLED', 'false')
os.environ.setdefault('HTTP_ONLY', 'true')

# Django setup
try:
    import django
    django.setup()
    logger.info("Django setup completed successfully")
except Exception as e:
    logger.error(f"Django setup failed: {e}")
    raise

# Import the Django WSGI application
from django.core.wsgi import get_wsgi_application

# Create WSGI application
application = get_wsgi_application()

# Export for Gunicorn compatibility
app = application

logger.info("WSGI application created and ready for deployment")

# If run directly, start Django development server
if __name__ == '__main__':
    logger.info("Starting Django development server")
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)