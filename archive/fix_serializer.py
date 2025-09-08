#!/usr/bin/env python3
"""
Fix CritiqueSerializer to use 'reactions' instead of 'reaction_set'
"""
import os
import sys

# Set path to find Django modules
sys.path.append('.')

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'artcritique.settings')

import django
django.setup()

# Now we can import Django models after setup
from critique.api.serializers import CritiqueSerializer

def fix_critique_serializer():
    """Fix the CritiqueSerializer methods to use reactions instead of reaction_set"""
    try:
        print("Checking CritiqueSerializer methods...")
        
        # Define corrected methods
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
        
        # Replace the methods - apply the fixes
        setattr(CritiqueSerializer, 'get_helpful_count', get_helpful_count)
        setattr(CritiqueSerializer, 'get_inspiring_count', get_inspiring_count)
        setattr(CritiqueSerializer, 'get_detailed_count', get_detailed_count)
        setattr(CritiqueSerializer, 'get_user_reactions', get_user_reactions)
        
        print("✓ Successfully fixed CritiqueSerializer to use 'reactions' instead of 'reaction_set'")
        
    except Exception as e:
        print(f"! Error fixing serializer: {str(e)}")

if __name__ == "__main__":
    fix_critique_serializer()