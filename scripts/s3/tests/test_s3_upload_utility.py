"""
S3 Upload Utility for Art Critique

This is a utility script that handles direct uploads to AWS S3 through 
your Django application, bypassing the web interface.

Usage:
    python test_s3_upload_utility.py
"""
import os
import sys
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'artcritique.settings')
django.setup()

# Import Django models
from django.contrib.auth import get_user_model
from critique.models import ArtWork, Profile
from django.core.files.uploadedfile import SimpleUploadedFile

def print_header(text):
    """Print formatted header text"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)

def create_test_image(filename, size_kb=20):
    """Create a test JPEG image file of specified size"""
    print(f"Creating test image: {filename} ({size_kb}KB)")
    
    # Create a valid minimal JPEG
    header = bytes.fromhex('FFD8FFE000104A46494600010100000100010000')
    footer = bytes.fromhex('FFD9')
    
    # Fill the content to match the requested size
    content_size = size_kb * 1024 - len(header) - len(footer)
    content = bytes([0xFF] * content_size)
    
    with open(filename, 'wb') as f:
        f.write(header)
        f.write(content)
        f.write(footer)
    
    print(f"✓ Created test image file: {filename} ({os.path.getsize(filename)} bytes)")
    return filename

def get_or_create_test_user(username, email, password):
    """Get or create a test user for uploading artwork"""
    User = get_user_model()
    
    try:
        user = User.objects.get(username=username)
        print(f"✓ Found existing test user: {username}")
    except User.DoesNotExist:
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        print(f"✓ Created new test user: {username}")
        
        # Create profile if needed
        if not hasattr(user, 'profile'):
            Profile.objects.create(user=user)
            print(f"✓ Created profile for test user")
    
    return user

def create_test_artwork(user, image_path, title, description):
    """Create a test artwork with an image that will be stored in S3"""
    print(f"Creating test artwork: {title}")
    
    # Read image file
    with open(image_path, 'rb') as f:
        image_content = f.read()
    
    # Create artwork with the image
    artwork = ArtWork.objects.create(
        title=title,
        description=description,
        author=user,
        medium="Digital",
        dimensions="800x600",
        tags="test,s3,upload",
        image=SimpleUploadedFile(
            name=os.path.basename(image_path),
            content=image_content,
            content_type="image/jpeg"
        )
    )
    
    print(f"✓ Created artwork (ID: {artwork.id})")
    return artwork

def verify_s3_storage(artwork):
    """Verify the artwork image is stored in S3"""
    print("\nVerifying S3 storage...")
    
    if not artwork.image:
        print("❌ Artwork has no image!")
        return False
    
    # Get the image URL
    image_url = artwork.image.url
    print(f"Image URL: {image_url}")
    
    # Check if it's an S3 URL
    if "s3.amazonaws.com" in image_url:
        print("✓ SUCCESS! Image is stored in S3 bucket")
        return True
    else:
        print("❌ Image does not appear to be stored in S3")
        print("  This might mean S3 storage is not properly configured")
        return False

def main():
    print_header("Art Critique - S3 Upload Utility")
    
    # Check if S3 is enabled
    from django.conf import settings
    if not settings.USE_S3:
        print("❌ S3 storage is not enabled in settings (USE_S3 is not True)")
        print("Please make sure the USE_S3 environment variable is set to True")
        return
    
    print("✓ S3 storage is enabled")
    print(f"✓ S3 bucket: {settings.AWS_STORAGE_BUCKET_NAME}")
    print(f"✓ S3 domain: {settings.AWS_S3_CUSTOM_DOMAIN}")
    
    # Create test data
    test_image = "test_s3_utility.jpg"
    create_test_image(test_image)
    
    user = get_or_create_test_user(
        username="s3_utility_user",
        email="s3utility@example.com",
        password="utility_password_123"
    )
    
    # Create an artwork with the test image
    artwork = create_test_artwork(
        user=user,
        image_path=test_image,
        title="S3 Utility Test Artwork",
        description="This artwork was created by the S3 upload utility to test S3 integration"
    )
    
    # Verify S3 storage
    success = verify_s3_storage(artwork)
    
    if success:
        print_header("S3 INTEGRATION TEST SUCCESSFUL!")
        print("""
Your Art Critique application is successfully storing images in S3.
When users upload images through the API or web interface, they will be
stored in your S3 bucket, assuming the web interface properly handles
authentication and CSRF tokens.
        """)
    else:
        print_header("S3 INTEGRATION TEST FAILED")
        print("""
There was an issue storing images in S3. Please check the following:
1. AWS credentials are correctly set up
2. S3 bucket exists and is accessible
3. USE_S3 environment variable is set to True
4. AWS_STORAGE_BUCKET_NAME is correctly set
        """)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()