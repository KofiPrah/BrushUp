#!/usr/bin/env python3
"""
Fix the CritiqueSerializer to add the missing get_reactions_count method
"""
import os
import django

# Configure Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'artcritique.settings')
django.setup()

from critique.models import Critique

def add_missing_method():
    serializer_path = 'critique/api/serializers.py'
    
    with open(serializer_path, 'r') as file:
        content = file.read()
    
    # Find where to insert the missing method
    target_str = '    def get_detailed_count(self, obj):\n        """Return the count of DETAILED reactions for this critique."""\n        return obj.reaction_set.filter(reaction_type=\'DETAILED\').count()\n        \n'
    
    replacement = '''    def get_detailed_count(self, obj):
        """Return the count of DETAILED reactions for this critique."""
        return obj.reaction_set.filter(reaction_type='DETAILED').count()
        
    def get_reactions_count(self, obj):
        """Return the count of reactions for this critique, grouped by type."""
        reactions_count = {
            'HELPFUL': obj.reaction_set.filter(reaction_type='HELPFUL').count(),
            'INSPIRING': obj.reaction_set.filter(reaction_type='INSPIRING').count(),
            'DETAILED': obj.reaction_set.filter(reaction_type='DETAILED').count(),
            'total': obj.reaction_set.count()
        }
        return reactions_count
        
'''
    
    if target_str in content:
        updated_content = content.replace(target_str, replacement)
        with open(serializer_path, 'w') as file:
            file.write(updated_content)
        print("Successfully added the missing get_reactions_count method to CritiqueSerializer")
    else:
        print("Could not find the target location in the serializer file")

if __name__ == "__main__":
    add_missing_method()