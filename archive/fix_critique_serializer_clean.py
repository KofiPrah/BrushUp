#!/usr/bin/env python3
"""
Fix the CritiqueSerializer to have only one clean get_reactions_count method
"""
import os
import re
import django

# Configure Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'artcritique.settings')
django.setup()

def remove_duplicates():
    """Remove duplicate get_reactions_count methods from CritiqueSerializer"""
    serializer_path = 'critique/api/serializers.py'
    
    with open(serializer_path, 'r') as file:
        content = file.read()
    
    # Find all get_reactions_count method definitions in CritiqueSerializer
    pattern = r'def get_reactions_count\(self, obj\):.*?return reactions_count\s+'
    matches = re.findall(pattern, content, re.DOTALL)
    
    if len(matches) <= 1:
        print("No duplicate get_reactions_count methods found.")
        return
    
    # Keep only the first occurrence of the method
    first_method = matches[0]
    for match in matches[1:]:
        content = content.replace(match, '')
    
    with open(serializer_path, 'w') as file:
        file.write(content)
    
    print("Successfully removed duplicate get_reactions_count methods.")

if __name__ == "__main__":
    remove_duplicates()