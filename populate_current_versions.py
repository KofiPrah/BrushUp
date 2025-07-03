#!/usr/bin/env python
"""
Populate current_version field for existing artworks
This script sets the current_version to the latest version for each artwork
"""
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'artcritique.settings')
django.setup()

from critique.models import ArtWork, ArtWorkVersion

def populate_current_versions():
    """Set current_version to the latest version for all artworks"""
    
    print("Populating current_version fields...")
    
    # Get all artworks that don't have a current_version set
    artworks_without_current = ArtWork.objects.filter(current_version__isnull=True)
    print(f"Found {artworks_without_current.count()} artworks without current_version")
    
    updated_count = 0
    
    for artwork in artworks_without_current:
        # Get the latest version for this artwork
        latest_version = artwork.get_latest_version()
        
        if latest_version:
            artwork.current_version = latest_version
            artwork.save(update_fields=['current_version'])
            updated_count += 1
            print(f"Updated artwork '{artwork.title}' to use version {latest_version.version_number}")
        else:
            # If no versions exist, create one from current artwork state
            if artwork.image:  # Only if artwork has an image
                version = artwork.create_version(version_notes="Initial version created during migration")
                print(f"Created initial version for artwork '{artwork.title}'")
                updated_count += 1
            else:
                print(f"Skipped artwork '{artwork.title}' - no image to create version from")
    
    print(f"\nCompleted! Updated {updated_count} artworks.")

if __name__ == '__main__':
    populate_current_versions()