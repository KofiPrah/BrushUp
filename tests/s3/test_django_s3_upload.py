"""
Script to test end-to-end S3 image upload through Django
"""
import os
import sys
import django
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'artcritique.settings')
django.setup()

# Now we can import Django models
from critique.models import ArtWork, Profile

def test_upload():
    """Test uploading an image through Django to S3"""
    print("=== Testing End-to-End S3 Image Upload via Django ===")
    
    # Check if S3 is enabled
    from django.conf import settings
    if not settings.USE_S3:
        print("❌ S3 storage is not enabled in settings (USE_S3 is not True)")
        return False
    
    print(f"✓ S3 storage is enabled")
    print(f"✓ Using bucket: {settings.AWS_STORAGE_BUCKET_NAME}")
    print(f"✓ S3 domain: {settings.AWS_S3_CUSTOM_DOMAIN}")
    
    # Get or create test user
    User = get_user_model()
    username = "test_s3_user"
    
    try:
        user = User.objects.get(username=username)
        print(f"✓ Found test user: {username}")
    except User.DoesNotExist:
        user = User.objects.create_user(
            username=username,
            email="test_s3@example.com",
            password="testpassword123"
        )
        print(f"✓ Created test user: {username}")
        
        # Create profile for user if it doesn't exist automatically
        if not hasattr(user, 'profile'):
            Profile.objects.create(user=user)
            print(f"✓ Created profile for test user")
    
    # Create a test image file
    print("Creating test image file...")
    test_image_path = "test_s3_image.jpg"
    
    # If test image doesn't exist, create a simple one
    if not os.path.exists(test_image_path):
        # Create a minimal valid JPEG file
        with open(test_image_path, 'wb') as f:
            # JPEG SOI marker
            f.write(bytes.fromhex('FFD8'))
            # JPEG APP0 marker
            f.write(bytes.fromhex('FFE0'))
            # Length of APP0 segment
            f.write(bytes.fromhex('0010'))
            # JFIF identifier
            f.write(b'JFIF\x00')
            # Version
            f.write(bytes.fromhex('0101'))
            # Units, X density, Y density
            f.write(bytes.fromhex('0001 0001 0001'))
            # Thumbnail width and height (0x0)
            f.write(bytes.fromhex('0000'))
            # JPEG EOI marker
            f.write(bytes.fromhex('FFD9'))
    
    # Read the test image
    with open(test_image_path, 'rb') as f:
        image_content = f.read()
    
    # Create an artwork with the test image
    print("Uploading test image to Django model (which will use S3 storage)...")
    
    test_artwork_title = "S3 Test Artwork"
    
    # First check if a test artwork already exists
    existing_artwork = ArtWork.objects.filter(title=test_artwork_title, author=user).first()
    if existing_artwork:
        print(f"Found existing test artwork: {existing_artwork.id}")
        artwork = existing_artwork
    else:
        # Create a new artwork with the test image
        artwork = ArtWork.objects.create(
            title=test_artwork_title,
            description="This is a test artwork to verify S3 integration",
            author=user,
            medium="Digital",
            dimensions="800x600",
            tags="test,s3,integration",
            image=SimpleUploadedFile(
                name="test_s3_image.jpg",
                content=image_content,
                content_type="image/jpeg"
            )
        )
        print(f"✓ Created new test artwork: {artwork.id}")
    
    # Verify the image URL
    if artwork.image and hasattr(artwork.image, 'url'):
        print(f"✓ Image URL: {artwork.image.url}")
        
        # Check if the URL points to S3
        s3_domain = settings.AWS_S3_CUSTOM_DOMAIN
        if s3_domain in artwork.image.url:
            print(f"✓ SUCCESS: Image is stored in S3 bucket! URL contains '{s3_domain}'")
            return True
        else:
            print(f"❌ Image URL does not point to S3 bucket (expected '{s3_domain}' in URL)")
            return False
    else:
        print("❌ Artwork has no image or image URL")
        return False

if __name__ == "__main__":
    try:
        success = test_upload()
        
        if success:
            print("\n✅ End-to-end S3 integration test PASSED!")
            print("  Your Django application is successfully storing images in S3.")
        else:
            print("\n❌ End-to-end S3 integration test FAILED.")
            print("  Please check the error messages above.")
            
    except Exception as e:
        print(f"\n❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()