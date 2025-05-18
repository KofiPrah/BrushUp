#!/usr/bin/env python3
"""
Simple HTTP server for Brush Up application that works in Replit
"""
import os
import sys

# Configure environment for HTTP mode
os.environ['DJANGO_SETTINGS_MODULE'] = 'artcritique.settings'
os.environ['SSL_ENABLED'] = 'false'
os.environ['HTTP_ONLY'] = 'true'
os.environ['HTTPS'] = 'off'
os.environ['wsgi.url_scheme'] = 'http'

# Fix the serializer if needed
def fix_critique_serializer():
    try:
        from critique.api.serializers import CritiqueSerializer
        
        # Check the get_helpful_count method to see if it needs fixing
        helpful_method = getattr(CritiqueSerializer, 'get_helpful_count', None)
        if helpful_method and hasattr(helpful_method, '__code__'):
            code = helpful_method.__code__
            if 'reaction_set' in code.co_names or 'reaction_set' in code.co_consts:
                print("Fixing CritiqueSerializer references from reaction_set to reactions...")
                
                # Define the corrected method implementations
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
                setattr(CritiqueSerializer, 'get_helpful_count', get_helpful_count)
                setattr(CritiqueSerializer, 'get_inspiring_count', get_inspiring_count)
                setattr(CritiqueSerializer, 'get_detailed_count', get_detailed_count)
                setattr(CritiqueSerializer, 'get_user_reactions', get_user_reactions)
                
                print("✓ Successfully fixed CritiqueSerializer methods")
            else:
                print("✓ CritiqueSerializer is already using 'reactions' correctly")
    except Exception as e:
        print(f"! Warning: Could not fix serializer: {str(e)}")

# Run the fix
fix_critique_serializer()

# Create KarmaEvent table if needed
def ensure_karmaevent_table():
    try:
        # Check for KarmaEvent table
        from django.db import connection
        cursor = connection.cursor()
        
        # Check if table exists
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
        print(f"! Warning: Could not check KarmaEvent table: {str(e)}")

# Now import and run Django application
try:
    from django.core.wsgi import get_wsgi_application
    
    # Get the WSGI application
    application = get_wsgi_application()
    
    # Create the alias 'app' for gunicorn
    app = application
    
    # Make sure KarmaEvent table exists
    ensure_karmaevent_table()
    
    print("✓ Django application initialized in HTTP mode")
except Exception as e:
    print(f"! Error initializing application: {str(e)}")
    sys.exit(1)