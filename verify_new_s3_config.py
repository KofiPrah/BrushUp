"""
Test script to verify new S3 configuration without ACLs
"""
import os
import django
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'artcritique.settings')
django.setup()

# Now we can import Django models
from critique.models import ArtWork, Profile
from django.conf import settings

def create_test_image(filename="test_new_config.jpg", size_kb=20):
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

def upload_new_image():
    """Upload a test image with new S3 settings"""
    print("\n=== Testing Updated S3 Configuration ===")
    
    # Check if S3 is enabled
    if not settings.USE_S3:
        print("❌ S3 storage is not enabled. Set USE_S3=True to enable.")
        return
    
    # Check ACL settings
    acl = getattr(settings, 'AWS_DEFAULT_ACL', 'Unknown')
    print(f"Current AWS_DEFAULT_ACL: {acl}")
    
    # Create test user
    User = get_user_model()
    username = "new_config_test_user"
    
    try:
        user = User.objects.get(username=username)
        print(f"✓ Found test user: {username}")
    except User.DoesNotExist:
        user = User.objects.create_user(
            username=username,
            email="new_config_test@example.com",
            password="newconfig123"
        )
        print(f"✓ Created test user: {username}")
        
        # Create profile for user if it doesn't exist
        if not hasattr(user, 'profile'):
            Profile.objects.create(user=user)
    
    # Create test image
    image_path = create_test_image()
    
    # Read image file
    with open(image_path, 'rb') as f:
        image_content = f.read()
    
    # Create artwork with this image
    print(f"Creating new artwork with image: {image_path}")
    artwork = ArtWork.objects.create(
        title="Test New S3 Config",
        description="Testing our updated S3 configuration without ACLs",
        author=user,
        medium="Digital",
        dimensions="800x600",
        tags="test,config,s3",
        image=SimpleUploadedFile(
            name="test_new_config.jpg",
            content=image_content,
            content_type="image/jpeg"
        )
    )
    
    print(f"✓ Created new artwork (ID: {artwork.id})")
    
    # Get image URL
    if artwork.image:
        image_url = artwork.image.url
        print(f"✓ Image URL: {image_url}")
        print("\nPlease check if you can access this URL in your browser.")
        print("If it works, our updated S3 configuration is successful!")
        
        # Full S3 path
        media_location = settings.PUBLIC_MEDIA_LOCATION if hasattr(settings, 'PUBLIC_MEDIA_LOCATION') else 'media'
        s3_path = f"{media_location}/artworks/test_new_config.jpg"
        print(f"\nThe image should be in your S3 bucket at:")
        print(f"  AWS → S3 → {settings.AWS_STORAGE_BUCKET_NAME} → {s3_path}")
    else:
        print("❌ No image URL available")

if __name__ == "__main__":
    upload_new_image()