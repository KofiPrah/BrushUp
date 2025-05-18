"""
Simple HTTP server for the Brush Up application (no SSL)
Designed to work with Replit's environment
"""
import sys
import os

# Set environment variables for HTTP mode
os.environ['SSL_ENABLED'] = 'false'
os.environ['HTTP_ONLY'] = 'true'
os.environ['wsgi.url_scheme'] = 'http'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'artcritique.settings')

# Apply CritiqueSerializer fixes
try:
    from fix_critique_serializer import add_missing_method
    add_missing_method()
    print("✓ Fixed CritiqueSerializer's get_reactions_count method")
except Exception as e:
    print(f"! Error fixing CritiqueSerializer: {str(e)}")

# Create the Brush Up application using Django
try:
    import django
    django.setup()
    from django.core.management import execute_from_command_line
    
    # Use the standard Django development server
    args = [sys.argv[0], 'runserver', '0.0.0.0:5000']
    execute_from_command_line(args)
except Exception as e:
    print(f"! Error starting server: {str(e)}")