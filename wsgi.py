"""
WSGI configuration for Brush Up application
"""
import os
import django

# Configure Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'artcritique.settings')
django.setup()

# Apply serializer fixes
try:
    from fix_critique_serializer import add_missing_method
    add_missing_method()
    print("✓ Successfully fixed CritiqueSerializer")
except Exception as e:
    print(f"! Error fixing serializer: {str(e)}")

# Get Django application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()