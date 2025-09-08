"""
HTTP-only starter script for Brush Up application
"""
import os
import django
import sys
import subprocess

# Set environment settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'artcritique.settings')
os.environ['SSL_ENABLED'] = 'false'
os.environ['HTTPS'] = 'off'
os.environ['wsgi.url_scheme'] = 'http'

# Initialize Django
django.setup()

# Fix serializer issues
try:
    from critique.api.serializers import CritiqueSerializer, CritiqueListSerializer
    
    # Define the missing method
    def get_reactions_count(self, obj):
        """Return the total count of all reactions for this critique."""
        return {
            'HELPFUL': obj.reactions.filter(reaction_type='HELPFUL').count(),
            'INSPIRING': obj.reactions.filter(reaction_type='INSPIRING').count(),
            'DETAILED': obj.reactions.filter(reaction_type='DETAILED').count(),
            'TOTAL': obj.reactions.count()
        }
    
    # Add the method to both serializers
    CritiqueSerializer.get_reactions_count = get_reactions_count
    CritiqueListSerializer.get_reactions_count = get_reactions_count
    
    print("✓ Fixed CritiqueSerializer with get_reactions_count method")
except Exception as e:
    print(f"! Error fixing serializers: {e}")

# Run Django directly
print("\n🚀 Starting Brush Up application in HTTP mode...")
os.environ['PYTHONUNBUFFERED'] = '1'
command = [sys.executable, 'manage.py', 'runserver', '0.0.0.0:5000']
subprocess.call(command)