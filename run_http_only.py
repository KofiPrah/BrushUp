"""
HTTP-only server for Brush Up application

This script runs the Django app directly in HTTP mode without SSL.
"""
import os
import sys
import django
from django.core.management import call_command

# Configure Django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "artcritique.settings")
os.environ["HTTPS"] = "off"
os.environ["USE_SSL"] = "false"

# Disable SSL
print("Disabling SSL for HTTP-only mode...")
with open("cert.pem.disabled", "w") as f:
    f.write("# SSL disabled for HTTP mode")
with open("key.pem.disabled", "w") as f:
    f.write("# SSL disabled for HTTP mode")

# Setup Django
django.setup()

# Fix serializer methods
try:
    from critique.api.serializers import CritiqueSerializer
    
    # Add missing methods to CritiqueSerializer
    if not hasattr(CritiqueSerializer, 'get_reactions_count'):
        def get_reactions_count(self, obj):
            """Return the total count of all reactions for this critique."""
            return obj.reactions.count()
        CritiqueSerializer.get_reactions_count = get_reactions_count
    
    if not hasattr(CritiqueSerializer, 'get_helpful_count'):
        def get_helpful_count(self, obj):
            """Return the count of HELPFUL reactions for this critique."""
            return obj.reactions.filter(reaction_type='HELPFUL').count()
        CritiqueSerializer.get_helpful_count = get_helpful_count
    
    if not hasattr(CritiqueSerializer, 'get_inspiring_count'):
        def get_inspiring_count(self, obj):
            """Return the count of INSPIRING reactions for this critique."""
            return obj.reactions.filter(reaction_type='INSPIRING').count()
        CritiqueSerializer.get_inspiring_count = get_inspiring_count
    
    if not hasattr(CritiqueSerializer, 'get_detailed_count'):
        def get_detailed_count(self, obj):
            """Return the count of DETAILED reactions for this critique."""
            return obj.reactions.filter(reaction_type='DETAILED').count()
        CritiqueSerializer.get_detailed_count = get_detailed_count
    
    if not hasattr(CritiqueSerializer, 'get_user_reactions'):
        def get_user_reactions(self, obj):
            """Return the user's reactions to this critique."""
            user = self.context.get('request').user if self.context.get('request') else None
            if not user or not user.is_authenticated:
                return []
            return obj.reactions.filter(user=user).values_list('reaction_type', flat=True)
        CritiqueSerializer.get_user_reactions = get_user_reactions
    
    print("Serializer methods added successfully!")
except Exception as e:
    print(f"Error adding serializer methods: {str(e)}")

# Run the Django server
print("\n=================================")
print("| Starting Brush Up in HTTP mode |")
print("=================================\n")

sys.argv = ["manage.py", "runserver", "0.0.0.0:5000"]
call_command("runserver", "0.0.0.0:5000")