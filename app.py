"""
HTTP server app for Brush Up
With serializer fixes applied
"""
import os
import django

# Configure Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'artcritique.settings')
django.setup()

# Fix serializer issues
try:
    from critique.api.serializers import CritiqueSerializer, CritiqueListSerializer
    
    def get_reactions_count(self, obj):
        """Return the total count of all reactions for this critique."""
        return {
            'HELPFUL': obj.reactions.filter(reaction_type='HELPFUL').count(),
            'INSPIRING': obj.reactions.filter(reaction_type='INSPIRING').count(),
            'DETAILED': obj.reactions.filter(reaction_type='DETAILED').count(),
            'TOTAL': obj.reactions.count()
        }
    
    # Add method to both serializers if missing
    if not hasattr(CritiqueSerializer, 'get_reactions_count'):
        setattr(CritiqueSerializer, 'get_reactions_count', get_reactions_count)
    
    if not hasattr(CritiqueListSerializer, 'get_reactions_count'):
        setattr(CritiqueListSerializer, 'get_reactions_count', get_reactions_count)
    
    print("✓ Successfully fixed CritiqueSerializer methods")
except Exception as e:
    print(f"! Error fixing serializers: {e}")

# Import the Django WSGI application
from django.core.wsgi import get_wsgi_application
app = get_wsgi_application()