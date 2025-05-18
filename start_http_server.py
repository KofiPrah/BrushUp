#!/usr/bin/env python3
"""
Complete HTTP server setup for Brush Up application
Fixes serializer issues and runs in HTTP mode for Replit compatibility
"""
import os
import sys

# Set environment variables for HTTP mode
os.environ['DJANGO_SETTINGS_MODULE'] = 'artcritique.settings'
os.environ['SSL_ENABLED'] = 'false'
os.environ['HTTP_ONLY'] = 'true'
os.environ['HTTPS'] = 'off'
os.environ['wsgi.url_scheme'] = 'http'

# Setup Django and related components
print("Initializing application in HTTP mode...")

# Initialize Django
import django
django.setup()

# Fix the serializer
from critique.api.serializers import CritiqueSerializer

# Check if we need to fix the serializer methods
def fix_serializer():
    print("Checking and fixing CritiqueSerializer methods...")
    
    # Define corrected methods that use 'reactions' instead of 'reaction_set'
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
    
    # Apply the fixes by replacing the methods
    CritiqueSerializer.get_helpful_count = get_helpful_count
    CritiqueSerializer.get_inspiring_count = get_inspiring_count
    CritiqueSerializer.get_detailed_count = get_detailed_count
    CritiqueSerializer.get_user_reactions = get_user_reactions
    
    print("✓ Successfully fixed CritiqueSerializer methods")

# Fix database tables if needed
def ensure_database_tables():
    print("Checking database tables...")
    
    # Import models
    from django.db import connection
    from django.db.utils import ProgrammingError
    
    # Check for KarmaEvent table
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT EXISTS (
                   SELECT FROM information_schema.tables 
                   WHERE table_name = 'critique_karmaevent'
                );
            """)
            exists = cursor.fetchone()[0]
            
            if not exists:
                print("Creating KarmaEvent table...")
                cursor.execute("""
                    CREATE TABLE critique_karmaevent (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER NOT NULL,
                        points INTEGER NOT NULL,
                        action VARCHAR(50) NOT NULL,
                        reason TEXT,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES auth_user(id)
                    );
                """)
                print("✓ Created KarmaEvent table")
            else:
                print("✓ KarmaEvent table already exists")
    except Exception as e:
        print(f"! Warning with KarmaEvent table: {str(e)}")
    
    # Check for Reaction table
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT EXISTS (
                   SELECT FROM information_schema.tables 
                   WHERE table_name = 'critique_reaction'
                );
            """)
            exists = cursor.fetchone()[0]
            
            if not exists:
                print("! Warning: Reaction table doesn't exist!")
            else:
                print("✓ Reaction table exists")
    except Exception as e:
        print(f"! Warning with Reaction table: {str(e)}")

# Apply all fixes
try:
    fix_serializer()
    ensure_database_tables()
    
    # Get Django WSGI application
    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()
    
    # For gunicorn compatibility
    app = application
    
    print("✓ Server initialized and ready for HTTP requests")
    
except Exception as e:
    print(f"! Error initializing application: {str(e)}")
    sys.exit(1)