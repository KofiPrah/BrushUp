#!/usr/bin/env python
"""
Utility script to check for discrepancies between database image paths and 
actual files in the media directory.
"""

import os
import django
from django.conf import settings

# Initialize Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'artcritique.settings')
django.setup()

# Now we can import Django models
from critique.models import ArtWork

def print_header(text):
    """Print formatted header text"""
    print("\n" + "=" * 50)
    print(text)
    print("=" * 50)

def list_files_in_directory(directory):
    """List all files in a directory and its subdirectories"""
    files = []
    for root, _, filenames in os.walk(directory):
        for filename in filenames:
            files.append(os.path.join(root, filename))
    return files

def main():
    """Check for discrepancies between database image paths and actual files"""
    print_header("Media Path Checker")
    
    # Check media root directory
    media_root = getattr(settings, 'MEDIA_ROOT', None)
    print(f"MEDIA_ROOT: {media_root}")
    print(f"MEDIA_URL: {getattr(settings, 'MEDIA_URL', None)}")
    print(f"Media directory exists: {os.path.exists(media_root)}")
    
    # List files in media directory
    print_header("Files in media directory")
    artworks_dir = os.path.join(media_root, 'artworks')
    
    if os.path.exists(artworks_dir):
        files = list_files_in_directory(artworks_dir)
        for file in files:
            print(f"File: {file}")
            # Get relative path from MEDIA_ROOT
            rel_path = os.path.relpath(file, media_root)
            print(f"Relative path: {rel_path}")
            # URL that would be used to access this file
            url = os.path.join(settings.MEDIA_URL, rel_path).replace('\\', '/')
            print(f"URL path: {url}")
    else:
        print(f"Artworks directory does not exist: {artworks_dir}")
        print("Creating directory...")
        os.makedirs(artworks_dir, exist_ok=True)
    
    # Check database records
    print_header("Database records")
    artworks = ArtWork.objects.all()
    print(f"Total artworks in database: {artworks.count()}")
    
    # Check image paths in database
    print_header("Image paths in database vs. files in media directory")
    missing_files = []
    
    for artwork in artworks:
        print(f"\nArtwork ID: {artwork.id}, Title: {artwork.title}")
        
        # Check fields that might contain image paths
        image_fields = {
            'image': getattr(artwork, 'image', None),
            'image_url': getattr(artwork, 'image_url', '')
        }
        
        for field_name, field_value in image_fields.items():
            if not field_value:
                continue
                
            print(f"  {field_name}: {field_value}")
            
            # For ImageField, get the path
            if hasattr(field_value, 'path'):
                file_path = field_value.path
                print(f"  File path: {file_path}")
                file_exists = os.path.exists(file_path)
                print(f"  File exists: {file_exists}")
                
                if not file_exists:
                    missing_files.append((artwork.id, field_name, file_path))
            
            # For image_url, check if it points to a local file
            elif isinstance(field_value, str) and field_value.startswith('/media/'):
                # Strip /media/ prefix
                rel_path = field_value[7:]
                file_path = os.path.join(media_root, rel_path)
                print(f"  File path: {file_path}")
                file_exists = os.path.exists(file_path)
                print(f"  File exists: {file_exists}")
                
                if not file_exists:
                    missing_files.append((artwork.id, field_name, file_path))
    
    # Summarize missing files
    print_header("Missing files summary")
    if missing_files:
        print(f"Total missing files: {len(missing_files)}")
        for artwork_id, field_name, file_path in missing_files:
            print(f"Artwork ID: {artwork_id}, Field: {field_name}, Missing file: {file_path}")
    else:
        print("No missing files found.")

if __name__ == "__main__":
    main()