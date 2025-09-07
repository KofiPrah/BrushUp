#!/usr/bin/env python3
"""
Fix server SSL issues to enable proper HTTP-only mode
Improves compatibility with Replit's load balancer
"""

import os
import subprocess
import sys
import signal

def print_banner(message):
    """Print a formatted banner message"""
    width = len(message) + 4
    print("\n" + "=" * width)
    print(f"  {message}")
    print("=" * width + "\n")

def handle_signal(sig, frame):
    """Handle termination signals gracefully"""
    print("\nShutting down server...")
    sys.exit(0)

def main():
    """Configure and run the server in HTTP-only mode"""
    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)
    
    print_banner("Configuring HTTP-only Server")
    
    # Stop any existing server processes
    subprocess.run("pkill -f 'gunicorn|runserver' || true", shell=True)
    
    # Fix serializer methods for critiques
    fix_serializer_methods()
    
    # Disable SSL by setting environment variables
    os.environ["SSL_ENABLED"] = "false"
    os.environ["HTTP_ONLY"] = "true"
    os.environ["SECURE_SSL_REDIRECT"] = "false"
    
    # Start Gunicorn without SSL certificates
    print_banner("Starting server in HTTP-only mode")
    cmd = [
        "gunicorn",
        "--bind", "0.0.0.0:5000",
        "--reuse-port",
        "--reload",
        "main:app"
    ]
    
    print(f"Running: {' '.join(cmd)}")
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\nServer shutdown requested")
    except Exception as e:
        print(f"Error starting server: {e}")
    
    return 0

def fix_serializer_methods():
    """Fix the CritiqueSerializer to have all required methods"""
    try:
        # Import the serializer and models
        from django.apps import apps
        from django.conf import settings
        
        # Configure Django settings if not already done
        if not settings.configured:
            os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'artcritique.settings')
            import django
            django.setup()
        
        # Get the CritiqueSerializer
        from critique.api.serializers import CritiqueSerializer
        
        # Check if the methods already exist
        if hasattr(CritiqueSerializer, 'get_reactions_count'):
            print("✓ CritiqueSerializer methods already exist")
            return
        
        # Define the reaction count methods
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
        
        # Add the methods to the serializer
        setattr(CritiqueSerializer, 'get_reactions_count', get_reactions_count)
        setattr(CritiqueSerializer, 'get_helpful_count', get_helpful_count)
        setattr(CritiqueSerializer, 'get_inspiring_count', get_inspiring_count)
        setattr(CritiqueSerializer, 'get_detailed_count', get_detailed_count)
        setattr(CritiqueSerializer, 'get_user_reactions', get_user_reactions)
        
        print("✓ Successfully fixed CritiqueSerializer methods")
    except Exception as e:
        print(f"Error fixing serializer methods: {e}")
        # Continue anyway, as this is not critical

if __name__ == "__main__":
    sys.exit(main())