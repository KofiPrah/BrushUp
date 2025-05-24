"""
Simple HTTP server for Brush Up application

This script runs Django directly without SSL certificates to fix common issues.
"""
import os
import sys
import subprocess
import signal
import time

def print_banner(message):
    """Print a formatted banner message"""
    line = "=" * (len(message) + 4)
    print(f"\n{line}")
    print(f"| {message} |")
    print(f"{line}\n")

def signal_handler(sig, frame):
    """Handle termination signals gracefully"""
    print_banner("Shutting down Brush Up server...")
    sys.exit(0)

def main():
    """Run Django directly in HTTP mode"""
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print_banner("Starting Brush Up in HTTP-only mode")
    
    # Set environment variables to use HTTP
    os.environ["DJANGO_SETTINGS_MODULE"] = "artcritique.settings"
    os.environ["HTTPS"] = "off"
    os.environ["USE_SSL"] = "false"
    
    # Fix serializer methods issue
    print("Ensuring serializer methods are available...")
    try:
        # Import Django modules to fix serializer methods
        import django
        django.setup()
        
        # Fix the serializer methods
        from critique.api.serializers import CritiqueSerializer
        
        # Check if the methods already exist
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
        
        print("Serializer methods fixed successfully!")
    except Exception as e:
        print(f"Error fixing serializer methods: {str(e)}")
    
    # Run Django using gunicorn on HTTP
    print_banner("Starting Django server on HTTP port 5000")
    cmd = [
        "gunicorn",
        "--bind", "0.0.0.0:5000",
        "--workers", "1",
        "--threads", "4",
        "--reload",
        "artcritique.wsgi:application"
    ]
    
    try:
        process = subprocess.Popen(cmd)
        print(f"Server running on port 5000")
        # Keep the script running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print_banner("Shutting down server...")
    finally:
        if 'process' in locals():
            process.terminate()
            process.wait()

if __name__ == "__main__":
    main()