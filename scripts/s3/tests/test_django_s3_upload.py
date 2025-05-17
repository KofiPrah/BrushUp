#!/usr/bin/env python3
"""
Django S3 Upload Test

This script tests uploading an artwork image through Django to S3.
It verifies that:
1. The image is uploaded to S3
2. The image URL is correctly generated
3. The image is accessible at the URL
"""
import os
import sys
import logging
import requests
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'artcritique.settings')
import django
django.setup()

# Now we can import Django models
from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from critique.models import ArtWork, Profile

# Set up logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_environment():
    """Check if S3 is enabled and required environment variables are set"""
    if not settings.USE_S3:
        print("❌ S3 storage is not enabled in settings (USE_S3 is not True)")
        print("This test requires S3 storage to be enabled.")
        print("Please make sure the USE_S3 environment variable is set to True")
        return False
    
    required_vars = ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'AWS_STORAGE_BUCKET_NAME']
    missing = []
    
    for var in required_vars:
        if not os.environ.get(var):
            missing.append(var)
    
    if missing:
        print(f"❌ Missing required environment variables: {', '.join(missing)}")
        print("Please set these variables before running this test.")
        return False
    
    print("✅ Environment configuration verified")
    return True

def create_test_image(width=500, height=400, text="Test Artwork"):
    """Create a test image with text and timestamp"""
    # Create a blank image with a colored background
    image = Image.new('RGB', (width, height), color=(73, 109, 137))
    
    # Get a drawing context
    draw = ImageDraw.Draw(image)
    
    # Add text
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    draw.text((10, 10), f"{text}", fill=(255, 255, 255))
    draw.text((10, 50), f"Created: {timestamp}", fill=(255, 255, 255))
    
    # Add some shapes for visual interest
    draw.rectangle([(50, 150), (450, 350)], outline=(255, 255, 255), width=2)
    
    # Convert to bytes
    img_byte_arr = BytesIO()
    image.save(img_byte_arr, format='JPEG')
    img_byte_arr.seek(0)
    
    return img_byte_arr.getvalue()

def get_or_create_test_user():
    """Get or create a test user for the artwork"""
    username = "testuser"
    email = "testuser@example.com"
    
    try:
        user = User.objects.get(username=username)
        print(f"✅ Using existing test user: {username}")
    except User.DoesNotExist:
        user = User.objects.create_user(
            username=username,
            email=email,
            password="testpassword"
        )
        # Create a profile for the user
        Profile.objects.create(user=user)
        print(f"✅ Created new test user: {username}")
    
    return user

def create_test_artwork(user):
    """Create a test artwork with an image"""
    # Create test image
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
    return artwork

def verify_image_url(url):
    """Verify the image URL is accessible"""
    try:
        response = requests.head(url, timeout=5)
        
        if response.status_code == 200:
            print(f"✅ Image is accessible at URL: {url}")
            return True
        else:
            print(f"❌ Image is not accessible. Status code: {response.status_code}")
            print(f"URL: {url}")
            return False
    
    except Exception as e:
        print(f"❌ Error checking image URL: {e}")
        print(f"URL: {url}")
        return False

def main():
    """Main test function"""
    print("\n========== Django S3 Upload Test ==========\n")
    
    # Check environment
    if not check_environment():
        return 1
    
    # Print S3 configuration
    print(f"\nS3 Configuration:")
    print(f"  Storage backend: {settings.DEFAULT_FILE_STORAGE}")
    print(f"  Media URL: {settings.MEDIA_URL}")
    print(f"  S3 Bucket: {settings.AWS_STORAGE_BUCKET_NAME}")
    print(f"  S3 Region: {settings.AWS_S3_REGION_NAME}")
    
    # Get or create test user
    user = get_or_create_test_user()
    
    # Create test artwork
    print("\nCreating test artwork with image...")
    artwork = create_test_artwork(user)
    
    # Print image information
    print("\nImage Information:")
    print(f"  Image field: {artwork.image}")
    print(f"  Image URL: {artwork.image.url}")
    
    # Verify image URL
    print("\nVerifying image URL...")
    verified = verify_image_url(artwork.image.url)
    
    if verified:
        print("\n✅ TEST PASSED: Image was successfully uploaded to S3 and is accessible.")
    else:
        print("\n❌ TEST FAILED: Image was not successfully uploaded or is not accessible.")
    
    return 0 if verified else 1

if __name__ == "__main__":
    sys.exit(main())