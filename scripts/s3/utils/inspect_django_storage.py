#!/usr/bin/env python3
"""
Inspect Django Storage Configuration

This script inspects the Django storage configuration to understand
how files are stored in S3 and what paths are used.
"""
import os
import sys
import json

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'artcritique.settings')
import django
django.setup()

# Now we can import Django-related modules
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from critique.models import ArtWork

# Import the storage backend directly
from artcritique.storage_backends import PublicMediaStorage, PrivateMediaStorage

def inspect_django_settings():
    """Display relevant Django settings for S3 storage"""
    print("\n=== Django S3 Storage Settings ===")
    
    # Check if S3 is enabled
    print(f"S3 enabled: {settings.USE_S3}")
    
    if settings.USE_S3:
        # Display S3 settings
        print(f"Default file storage: {settings.DEFAULT_FILE_STORAGE}")
        print(f"Media URL: {settings.MEDIA_URL}")
        print(f"S3 bucket name: {settings.AWS_STORAGE_BUCKET_NAME}")
        print(f"S3 region: {settings.AWS_S3_REGION_NAME}")
        print(f"Public media location: {settings.PUBLIC_MEDIA_LOCATION}")
        
        # Show ACL settings
        print(f"AWS default ACL: {settings.AWS_DEFAULT_ACL}")
        print(f"Query string auth: {settings.AWS_QUERYSTRING_AUTH}")
        
        # Check for custom domain
        if hasattr(settings, 'AWS_S3_CUSTOM_DOMAIN'):
            print(f"S3 custom domain: {settings.AWS_S3_CUSTOM_DOMAIN}")

def analyze_storage_backend():
    """Analyze the storage backend classes"""
    print("\n=== Storage Backend Analysis ===")
    
    # Analyze public media storage
    public_storage = PublicMediaStorage()
    print("Public Storage (DEFAULT_FILE_STORAGE):")
    print(f"  Location: {public_storage.location}")
    print(f"  Base URL: {public_storage.url('')}")
    print(f"  Default ACL: {public_storage.default_acl}")
    
    # Check how it builds paths and URLs
    test_path = "test_image.jpg"
    s3_path = public_storage._normalize_name(test_path)
    print(f"  Test file path: {test_path}")
    print(f"  S3 normalized path: {s3_path}")
    
    # Print attributes of the class
    print("\nPublic Storage Attributes:")
    for attr in dir(public_storage):
        if not attr.startswith('_') and not callable(getattr(public_storage, attr)):
            try:
                value = getattr(public_storage, attr)
                print(f"  {attr}: {value}")
            except Exception as e:
                print(f"  {attr}: <Error: {e}>")

def test_storage_operations():
    """Test basic storage operations"""
    print("\n=== Storage Operations Testing ===")
    
    # Create a test file
    test_content = b"This is a test file for S3 storage."
    test_path = "storage_test/test_file.txt"
    
    try:
        # Save the test file
        path = default_storage.save(test_path, ContentFile(test_content))
        print(f"File saved at: {path}")
        
        # Get the URL
        url = default_storage.url(path)
        print(f"File URL: {url}")
        
        # Analyze URL components
        url_parts = url.split("/")
        print(f"URL structure: {'/'.join(url_parts[:-1])}/{url_parts[-1]}")
        
        # Check if the file exists
        exists = default_storage.exists(path)
        print(f"File exists: {exists}")
        
        # Display generated paths
        storage = default_storage
        full_path = storage._normalize_name(path)
        print(f"Normalized path: {full_path}")
        
        # Get object parameters that would be sent to S3
        if hasattr(storage, 'get_object_parameters'):
            try:
                params = storage.get_object_parameters(path)
                print(f"Object parameters: {json.dumps(params, indent=2)}")
            except Exception as e:
                print(f"Could not get object parameters: {e}")
        
    except Exception as e:
        print(f"Error testing storage operations: {e}")

def inspect_artwork_images():
    """Inspect existing artwork images"""
    print("\n=== Existing Artwork Images ===")
    
    # Get all artworks with images
    artworks = ArtWork.objects.exclude(image='').order_by('-created_at')[:5]
    
    if not artworks:
        print("No artworks with images found.")
        return
    
    for artwork in artworks:
        print(f"\nArtwork: {artwork.title}")
        print(f"  Image field value: {artwork.image}")
        print(f"  Image URL: {artwork.image.url}")
        
        # Get storage info for this image
        storage = artwork.image.storage
        storage_class = storage.__class__.__name__
        print(f"  Storage class: {storage_class}")
        
        # Check if the file exists in storage
        exists = storage.exists(artwork.image.name)
        print(f"  File exists in storage: {exists}")
        
        # Analyze custom URL generation if any
        if hasattr(storage, '_normalize_name'):
            normalized = storage._normalize_name(artwork.image.name)
            print(f"  Normalized name: {normalized}")

def main():
    """Main function"""
    print("\n========== Django S3 Storage Inspection ==========")
    
    # Display Django settings
    inspect_django_settings()
    
    # Analyze storage backend
    analyze_storage_backend()
    
    # Test storage operations
    test_storage_operations()
    
    # Inspect existing artwork images
    inspect_artwork_images()
    
    print("\n========== Inspection Complete ==========\n")
    return 0

if __name__ == "__main__":
    sys.exit(main())