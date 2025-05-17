"""
Final S3 fix: adjust settings for image uploads
"""
import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'artcritique.settings')
django.setup()

from django.conf import settings

def check_current_settings():
    """Check and display current S3 settings"""
    print("Current S3 Settings:")
    print(f"USE_S3: {settings.USE_S3}")
    print(f"AWS_STORAGE_BUCKET_NAME: {settings.AWS_STORAGE_BUCKET_NAME}")
    print(f"AWS_S3_CUSTOM_DOMAIN: {settings.AWS_S3_CUSTOM_DOMAIN}")
    print(f"AWS_DEFAULT_ACL: {settings.AWS_DEFAULT_ACL}")
    print(f"PUBLIC_MEDIA_LOCATION: {settings.PUBLIC_MEDIA_LOCATION}")
    print(f"MEDIA_URL: {settings.MEDIA_URL}")
    print(f"DEFAULT_FILE_STORAGE: {settings.DEFAULT_FILE_STORAGE}")
    
    # Check if AWS credentials are set
    aws_access_key = getattr(settings, 'AWS_ACCESS_KEY_ID', None)
    aws_secret_key = getattr(settings, 'AWS_SECRET_ACCESS_KEY', None)
    aws_region = getattr(settings, 'AWS_S3_REGION_NAME', None)
    
    if aws_access_key and aws_secret_key:
        print(f"AWS Credentials: ✓ Present")
        print(f"AWS Region: {aws_region}")
    else:
        print("AWS Credentials: ❌ Missing")

def suggest_workaround():
    """Suggest a workaround for S3 issues"""
    print("\nRecommended Workaround Options:")
    
    print("\nOption 1: Continue using S3 with pre-signed URLs")
    print("- Modify your templates/views to use pre-signed URLs")
    print("- Add a helper function to generate pre-signed URLs:")
    print("""
    def get_presigned_url(s3_key, expiry=3600):
        import boto3
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME
        )
        return s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                'Key': s3_key
            },
            ExpiresIn=expiry
        )
    """)
    
    print("\nOption 2: Switch to local file storage temporarily")
    print("- Temporarily disable S3 storage")
    print("- Use local filesystem storage instead")
    print("- Simplifies development while resolving S3 permissions")
    print("""
    # In settings.py:
    USE_S3 = False
    
    # Configure local media storage
    MEDIA_URL = '/media/'
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
    """)
    
    print("\nOption 3: Fix AWS S3 bucket permissions in AWS Console")
    print("- Log into AWS Console")
    print("- Navigate to S3 > brushup-media > Permissions")
    print("- Ensure Block Public Access settings are OFF")
    print("- Add a bucket policy allowing public read access to all objects")
    print("- Check CORS configuration allows access from your domain")

def update_serializer_for_presigned():
    """Generate code to update serializer to use presigned URLs"""
    print("\nExample Serializer Update for Pre-signed URLs:")
    print("""
from django.conf import settings
import boto3

def get_presigned_url(s3_key, expiry=3600):
    # Generate a pre-signed URL for an S3 object
    s3_client = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_S3_REGION_NAME
    )
    return s3_client.generate_presigned_url(
        'get_object',
        Params={
            'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
            'Key': s3_key
        },
        ExpiresIn=expiry
    )

class ArtWorkSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = ArtWork
        fields = [
            'id', 'title', 'description', 'image', 'image_url',
            # other fields...
        ]
    
    def get_image_url(self, obj):
        """Return a pre-signed URL for the image"""
        if obj.image and hasattr(obj.image, 'name'):
            # Return pre-signed URL valid for 1 hour
            return get_presigned_url(obj.image.name)
        return None
""")

def main():
    print("Final S3 Fix and Recommendations\n" + "=" * 50)
    
    # Check current settings
    check_current_settings()
    
    # Suggest workarounds
    suggest_workaround()
    
    # Example code for serializer
    update_serializer_for_presigned()
    
    print("\nNext Steps:")
    print("1. Try one of the recommended options")
    print("2. Test with a new image upload")
    print("3. If still having issues, check AWS console settings")
    print("\nFor development purposes, Option 2 (local storage) may be simplest")
    print("For production, Option 1 (pre-signed URLs) or Option 3 (fix AWS console) is recommended")

if __name__ == "__main__":
    main()