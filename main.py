import os
import django

# Configure Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'artcritique.settings')
os.environ['SSL_ENABLED'] = 'false'
os.environ['HTTP_ONLY'] = 'true'
os.environ['HTTPS'] = 'off'
os.environ['wsgi.url_scheme'] = 'http'

# Initialize Django
django.setup()

# Import and configure WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
app = application

# Fix the CritiqueSerializer to use 'reactions' instead of 'reaction_set'
try:
    from critique.api.serializers import CritiqueSerializer
    
    # Define fixed methods
    def get_reactions_count(self, obj):
        """Return the total count of all reactions for this critique."""
        return {
            'HELPFUL': obj.reactions.filter(reaction_type='HELPFUL').count(),
            'INSPIRING': obj.reactions.filter(reaction_type='INSPIRING').count(),
            'DETAILED': obj.reactions.filter(reaction_type='DETAILED').count(),
            'TOTAL': obj.reactions.count()
        }
        
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
    
    # Replace the methods
    CritiqueSerializer.get_reactions_count = get_reactions_count
    CritiqueSerializer.get_helpful_count = get_helpful_count
    CritiqueSerializer.get_inspiring_count = get_inspiring_count
    CritiqueSerializer.get_detailed_count = get_detailed_count
    CritiqueSerializer.get_user_reactions = get_user_reactions
    
    # Fix the CritiqueListSerializer as well
    from critique.api.serializers import CritiqueListSerializer
    CritiqueListSerializer.get_reactions_count = get_reactions_count
    CritiqueListSerializer.get_helpful_count = get_helpful_count
    CritiqueListSerializer.get_inspiring_count = get_inspiring_count
    CritiqueListSerializer.get_detailed_count = get_detailed_count
    CritiqueListSerializer.get_user_reactions = get_user_reactions
    
    print("✓ Successfully fixed CritiqueSerializer methods")
except Exception as e:
    print(f"Warning: Unable to fix serializer: {e}")

# Run the server if executed directly
if __name__ == '__main__':
    import sys
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)