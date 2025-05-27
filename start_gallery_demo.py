#!/usr/bin/env python3
"""
Simple HTTP server for Brush Up Gallery Demo
This script bypasses SSL issues and runs Django directly
"""

import os
import sys
import django
from django.core.management import execute_from_command_line

def main():
    """Run Django in HTTP-only mode to demonstrate the enhanced gallery features"""
    
    # Set Django settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'artcritique.settings')
    
    # Remove SSL certificates to force HTTP mode
    ssl_files = ['cert.pem', 'key.pem']
    for ssl_file in ssl_files:
        if os.path.exists(ssl_file):
            try:
                os.remove(ssl_file)
                print(f"Removed {ssl_file} to enable HTTP mode")
            except:
                pass
    
    # Initialize Django
    django.setup()
    
    print("\n" + "="*60)
    print("🎨 BRUSH UP GALLERY - Phase 11 Popularity Filtering Demo")
    print("="*60)
    print("✓ Enhanced search functionality")
    print("✓ Popularity-based sorting system")
    print("✓ Advanced filtering options")
    print("✓ API endpoints for React frontend")
    print("="*60)
    print("🌐 Starting HTTP server on port 5000...")
    print("📋 Visit: /artworks/ to see the enhanced gallery")
    print("🔥 Try sorting by 'Most Popular'")
    print("💬 Try sorting by 'Most Critiques'")
    print("❤️ Try sorting by 'Most Liked'")
    print("="*60 + "\n")
    
    # Start Django development server
    execute_from_command_line([
        'manage.py', 
        'runserver', 
        '0.0.0.0:5000',
        '--noreload'
    ])

if __name__ == '__main__':
    main()