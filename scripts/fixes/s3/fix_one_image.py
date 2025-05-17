"""
Script to fix and test a single image access in S3
"""
import os
import boto3
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'artcritique.settings')
django.setup()

from django.conf import settings

def fix_specific_image(s3_key):
    """Apply bucket policy and test a specific image"""
    print(f"Attempting to fix image: {s3_key}")
    
    try:
        # Initialize boto3 clients
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME
        )
        
        # 1. Apply a public-read bucket policy to ensure all objects are readable
        bucket_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "PublicReadForGetBucketObjects",
                    "Effect": "Allow",
                    "Principal": "*",
                    "Action": "s3:GetObject",
                    "Resource": f"arn:aws:s3:::{settings.AWS_STORAGE_BUCKET_NAME}/*"
                }
            ]
        }
        
        # Convert policy to JSON
        import json
        policy_str = json.dumps(bucket_policy)
        
        # Apply policy to bucket
        s3_client.put_bucket_policy(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
            Policy=policy_str
        )
        print("✓ Applied public-read bucket policy")
        
        # 2. Generate a pre-signed URL for testing
        presigned_url = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                'Key': s3_key
            },
            ExpiresIn=3600  # URL valid for 1 hour
        )
        
        print(f"\nS3 Image Access Information:")
        print(f"S3 Key: {s3_key}")
        print(f"Direct URL: https://{settings.AWS_S3_CUSTOM_DOMAIN}/{s3_key}")
        print(f"Pre-signed URL (valid for 1 hour):")
        print(f"{presigned_url}")
        
        print("\nRecommendations:")
        print("1. Try accessing the pre-signed URL above - it should work")
        print("2. The direct URL may take a few minutes to work after applying the bucket policy")
        print("3. If direct URLs still don't work, check your AWS bucket CORS settings")
        
        return presigned_url
        
    except Exception as e:
        print(f"Error: {e}")
        return None

def main():
    # Let's fix artwork images
    
    # First, maintain our fix for the test image
    fix_specific_image("test/direct_upload_1747426651.jpg")
    
    # Now fix a specific artwork file
    fix_specific_image("media/artworks/test_new_config.jpg")
    
    # Let's also try fixing any image that might have been uploaded through the web interface
    # This covers the common pattern used by the application
    fix_specific_image("media/artworks/A170D2D5-DCEE-4E01-AE2F-B015E363AD4A.png")

if __name__ == "__main__":
    main()