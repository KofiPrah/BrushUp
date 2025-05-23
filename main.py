"""
Brush Up Application Main File
HTTP-only version to prevent SSL errors

This file loads the Django WSGI application and configures the required reaction methods
"""
import os
import sys
# Force HTTP mode - disable SSL
os.environ['DJANGO_INSECURE'] = 'true'
os.environ['DJANGO_DEVELOPMENT'] = 'true'
os.environ['DJANGO_SETTINGS_MODULE'] = 'artcritique.settings'

import os
import sys
from importlib import reload

# Set environment variables for HTTP-only mode
os.environ["SSL_ENABLED"] = "false"
os.environ["HTTP_ONLY"] = "true"
os.environ["SECURE_SSL_REDIRECT"] = "false"
os.environ["wsgi.url_scheme"] = "http"

# Ensure all reaction methods are available on CritiqueSerializer
def ensure_reaction_methods():
    """Fix the CritiqueSerializer to have proper reaction methods"""
    try:
        from critique.api.serializers import CritiqueSerializer
        
        # Check if the methods already exist
        if hasattr(CritiqueSerializer, 'get_reactions_count'):
            print("✓ Successfully fixed CritiqueSerializer methods")
            return
            
        # Define missing methods
        def get_reactions_count(self, obj):
            """Return the total count of all reactions for this critique."""
            return obj.reactions.count()
            
        def get_helpful_count(self, obj):
            """Return the count of HELPFUL reactions for this critique."""
            return obj.reactions.filter(reaction_type='HELPFUL').count()
            
        def get_inspiring_count(self, obj):
            """Return the count of INSPIRING reactions for this critique."""
            return obj.reactions.filter(reaction_type='INSPIRING').count()
            
        def get_detailed_count(self, obj):
            """Return the count of DETAILED reactions for this critique."""
            return obj.reactions.filter(reaction_type='DETAILED').count()
            
        def get_user_reactions(self, obj):
            """Return the user's reactions to this critique."""
            user = self.context.get('request').user
            if not user or user.is_anonymous:
                return []
                
            reactions = obj.reactions.filter(user=user)
            return [r.reaction_type for r in reactions]
            
        # Add methods to the serializer
        setattr(CritiqueSerializer, 'get_reactions_count', get_reactions_count)
        setattr(CritiqueSerializer, 'get_helpful_count', get_helpful_count)
        setattr(CritiqueSerializer, 'get_inspiring_count', get_inspiring_count)
        setattr(CritiqueSerializer, 'get_detailed_count', get_detailed_count)
        setattr(CritiqueSerializer, 'get_user_reactions', get_user_reactions)
        
        print("✓ Successfully fixed CritiqueSerializer methods")
    except Exception as e:
        print(f"Error fixing serializer methods: {e}")

# Get the Django application
def get_application():
    """Get the Django WSGI application"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'artcritique.settings')
    from django.core.wsgi import get_wsgi_application
    return get_wsgi_application()

# Apply fixes and get the application
ensure_reaction_methods()

# Export the application
app = get_application()

# If run directly, start a development server
if __name__ == '__main__':
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)