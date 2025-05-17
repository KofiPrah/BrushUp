#!/usr/bin/env python3
"""
Enforce S3 Storage for Django Models

This script enforces the use of S3 storage for Django models that handle file uploads.
It updates models to explicitly use the PublicMediaStorage backend.
"""
import os
import sys
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'artcritique.settings')
django.setup()

from django.conf import settings
from django.apps import apps
from django.db.models.fields.files import FileField, ImageField
from artcritique.storage_backends import PublicMediaStorage
from critique.models import ArtWork, Profile

def print_header(text):
    """Print a header with the given text."""
    print("\n" + "=" * 50)
    print(text)
    print("=" * 50)

def examine_models():
    """Examine all models with file fields to check their storage backends."""
    print_header("EXAMINING MODELS WITH FILE FIELDS")
    
    models_with_file_fields = []
    
    # Find all models with file fields
    for app_config in apps.get_app_configs():
        for model in app_config.get_models():
            file_fields = []
            for field in model._meta.get_fields():
                if isinstance(field, (FileField, ImageField)):
                    file_fields.append(field)
            
            if file_fields:
                models_with_file_fields.append((model, file_fields))
    
    # Print information about found models
    for model, fields in models_with_file_fields:
        print(f"\nModel: {model.__name__}")
        for field in fields:
            storage_class = field.storage.__class__.__name__
            print(f"  Field: {field.name}")
            print(f"  Storage: {storage_class}")
            print(f"  Upload to: {field.upload_to}")

def fix_artwork_model():
    """Fix the ArtWork model to use S3 storage explicitly."""
    print_header("FIXING ARTWORK MODEL")
    
    if not settings.USE_S3:
        print("S3 storage is not enabled. Set USE_S3=True to enable.")
        return False
    
    # Get examples before the fix
    artworks = ArtWork.objects.exclude(image='').order_by('-created_at')[:2]
    if artworks:
        print("\nBefore the fix:")
        for artwork in artworks:
            storage_class = artwork.image.storage.__class__.__name__
            print(f"  Artwork: {artwork.title}")
            print(f"  Storage class: {storage_class}")
            print(f"  Image URL: {artwork.image.url}")
    
    # Get the image field
    try:
        image_field = ArtWork._meta.get_field('image')
        original_storage = image_field.storage.__class__.__name__
        
        # Create a new PublicMediaStorage instance
        s3_storage = PublicMediaStorage()
        
        # Set the storage for the image field
        image_field.storage = s3_storage
        
        print(f"\nUpdated storage for ArtWork.image:")
        print(f"  Original storage: {original_storage}")
        print(f"  New storage: {s3_storage.__class__.__name__}")
        
        # Check if the fix worked
        artworks = ArtWork.objects.exclude(image='').order_by('-created_at')[:2]
        if artworks:
            print("\nAfter the fix:")
            for artwork in artworks:
                storage_class = artwork.image.storage.__class__.__name__
                print(f"  Artwork: {artwork.title}")
                print(f"  Storage class: {storage_class}")
                print(f"  Image URL: {artwork.image.url}")
        
        return True
    except Exception as e:
        print(f"Error fixing ArtWork model: {e}")
        return False

def check_file_access():
    """Check if files are publicly accessible after the fix."""
    print_header("CHECKING FILE ACCESS AFTER FIX")
    
    import requests
    
    artworks = ArtWork.objects.exclude(image='').order_by('-created_at')[:2]
    if not artworks:
        print("No artworks with images found.")
        return
    
    for artwork in artworks:
        print(f"\nChecking access for: {artwork.title}")
        print(f"  URL: {artwork.image.url}")
        
        try:
            response = requests.head(artwork.image.url, timeout=5)
            status = f"✅ ACCESSIBLE (Status: {response.status_code})" if response.status_code == 200 else f"❌ NOT ACCESSIBLE (Status: {response.status_code})"
            print(f"  Access: {status}")
        except Exception as e:
            print(f"  Error checking access: {e}")

def update_s3_bucket_policy():
    """Update the S3 bucket policy to allow public read access."""
    print_header("UPDATING S3 BUCKET POLICY")
    
    import boto3
    import json
    from botocore.exceptions import ClientError
    
    # Get AWS credentials from environment
    aws_access_key = os.environ.get('AWS_ACCESS_KEY_ID')
    aws_secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
    bucket_name = os.environ.get('AWS_STORAGE_BUCKET_NAME')
    
    if not (aws_access_key and aws_secret_key and bucket_name):
        print("Missing required AWS credentials in environment variables")
        return False
    
    print(f"Updating policy for bucket: {bucket_name}")
    
    # Create S3 client
    s3_client = boto3.client('s3',
                            aws_access_key_id=aws_access_key,
                            aws_secret_access_key=aws_secret_key)
    
    # Create policy document to allow public read access to media files
    policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "PublicReadForMediaObjects",
                "Effect": "Allow",
                "Principal": "*",
                "Action": "s3:GetObject",
                "Resource": [
                    f"arn:aws:s3:::{bucket_name}/media/*",
                    f"arn:aws:s3:::{bucket_name}/direct_uploads/*"
                ]
            }
        ]
    }
    
    try:
        # Apply the policy to the bucket
        s3_client.put_bucket_policy(
            Bucket=bucket_name,
            Policy=json.dumps(policy)
        )
        print("Successfully updated bucket policy")
        return True
    except ClientError as e:
        print(f"Error updating bucket policy: {e}")
        return False

def main():
    """Main function to fix S3 storage issues."""
    print_header("S3 STORAGE FIX")
    
    # Check if S3 is enabled
    if not settings.USE_S3:
        print("S3 storage is not enabled. Set USE_S3=True to enable.")
        return 1
    
    # Examine models with file fields
    examine_models()
    
    # Update S3 bucket policy
    update_s3_bucket_policy()
    
    # Fix the ArtWork model
    fix_artwork_model()
    
    # Check file access after the fix
    check_file_access()
    
    print_header("FIX COMPLETE")
    print("Remember to reload your application for the changes to take effect.")
    return 0

if __name__ == "__main__":
    sys.exit(main())