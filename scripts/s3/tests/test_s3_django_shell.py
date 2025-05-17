#!/usr/bin/env python3
"""
S3 Upload Test Script for Django Shell

This script should be run in the Django shell context:
python manage.py shell < scripts/s3/tests/test_s3_django_shell.py
"""

import os
import sys
import requests
from io import BytesIO
from PIL import Image, ImageDraw
from datetime import datetime
from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from critique.models import ArtWork, Profile

# Set up basic print formatting
print("\n========== Django S3 Upload Test ==========\n")

# Check if S3 is enabled
if not settings.USE_S3:
    print("❌ S3 storage is not enabled in settings (USE_S3 is not True)")
    print("This test requires S3 storage to be enabled.")
    sys.exit(1)

# Print S3 configuration
print(f"S3 Configuration:")
print(f"  Storage backend: {settings.DEFAULT_FILE_STORAGE}")
print(f"  Media URL: {settings.MEDIA_URL}")
print(f"  S3 Bucket: {settings.AWS_STORAGE_BUCKET_NAME}")

# Get or create test user
username = "testuser"
try:
    user = User.objects.get(username=username)
    print(f"✅ Using existing test user: {username}")
except User.DoesNotExist:
    user = User.objects.create_user(
        username=username,
        email="testuser@example.com",
        password="testpassword"
    )
    # Create a profile for the user
    Profile.objects.create(user=user)
    print(f"✅ Created new test user: {username}")

# Create a test image
def create_test_image(width=500, height=400, text="Test Artwork"):
    # Create a blank image with a colored background
    image = Image.new('RGB', (width, height), color=(73, 109, 137))
    
    # Get a drawing context
    draw = ImageDraw.Draw(image)
    
    # Add text
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    draw.text((10, 10), f"{text}", fill=(255, 255, 255))
    draw.text((10, 50), f"Created: {timestamp}", fill=(255, 255, 255))
    
    # Add shapes
    draw.rectangle([(50, 150), (450, 350)], outline=(255, 255, 255), width=2)
    
    # Convert to bytes
    img_byte_arr = BytesIO()
    image.save(img_byte_arr, format='JPEG')
    img_byte_arr.seek(0)
    
    return img_byte_arr.getvalue()

# Create test image data
print("\nCreating test image...")
image_data = create_test_image(text="Django S3 Upload Test")

# Create a SimpleUploadedFile from the image data
image_file = SimpleUploadedFile(
    name="test_artwork.jpg",
    content=image_data,
    content_type="image/jpeg"
)

# Create timestamp for unique title
timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

# Create the artwork
print("Creating test artwork with image...")
artwork = ArtWork.objects.create(
    title=f"Test Artwork {timestamp}",
    description="This is a test artwork uploaded directly to S3 by a Django test script.",
    author=user,
    medium="Digital",
    tags="test, s3, django"
)

# Set the image
artwork.image = image_file
artwork.save()

print(f"✅ Created test artwork: {artwork.title}")

# Print image information
print("\nImage Information:")
print(f"  Image field: {artwork.image}")
print(f"  Image URL: {artwork.image.url}")

# Verify image URL
print("\nVerifying image URL...")
try:
    response = requests.head(artwork.image.url, timeout=5)
    
    if response.status_code == 200:
        print(f"✅ Image is accessible at URL: {artwork.image.url}")
        print("\n✅ TEST PASSED: Image was successfully uploaded to S3 and is accessible.")
    else:
        print(f"❌ Image is not accessible. Status code: {response.status_code}")
        print(f"URL: {artwork.image.url}")
        print("\n❌ TEST FAILED: Image was uploaded but is not accessible.")
except Exception as e:
    print(f"❌ Error checking image URL: {e}")
    print(f"URL: {artwork.image.url}")
    print("\n❌ TEST FAILED: Error occurred while verifying image URL.")