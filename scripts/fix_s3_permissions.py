"""
Fix permissions on S3 bucket and objects by applying public-read ACL
"""
import os
import django
import boto3
from botocore.exceptions import ClientError

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'artcritique.settings')
django.setup()

from django.conf import settings
from critique.models import ArtWork

def print_header(text):
    """Print formatted header text"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)

def update_bucket_policy():
    """Add a bucket policy that allows public read access to all objects"""
    print_header("Updating S3 Bucket Policy")
    
    try:
        # Initialize boto3 client
        s3 = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME or 'us-east-1'
        )
        
        bucket_name = settings.AWS_STORAGE_BUCKET_NAME
        
        # Create a bucket policy to allow public read access
        bucket_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "PublicReadGetObject",
                    "Effect": "Allow",
                    "Principal": "*",
                    "Action": "s3:GetObject",
                    "Resource": f"arn:aws:s3:::{bucket_name}/*"
                }
            ]
        }
        
        # Convert the policy to JSON
        import json
        policy_str = json.dumps(bucket_policy)
        
        # Apply the policy to the bucket
        s3.put_bucket_policy(Bucket=bucket_name, Policy=policy_str)
        
        print(f"✓ Successfully updated bucket policy for {bucket_name}")
        print("✓ All objects should now be publicly readable")
        
        return True
    except Exception as e:
        print(f"❌ Error updating bucket policy: {e}")
        return False

def update_object_acls():
    """Update all existing artwork image objects to have public-read ACL"""
    print_header("Updating ACLs on Existing Objects")
    
    try:
        # Initialize boto3 resource
        s3 = boto3.resource(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME or 'us-east-1'
        )
        
        bucket_name = settings.AWS_STORAGE_BUCKET_NAME
        bucket = s3.Bucket(bucket_name)
        
        # Get all artwork images from the database
        artworks = ArtWork.objects.all()
        updated_count = 0
        error_count = 0
        
        print(f"Found {len(artworks)} artworks in the database")
        
        for artwork in artworks:
            if artwork.image and hasattr(artwork.image, 'name'):
                # Extract the key from the image URL
                key = artwork.image.name
                print(f"Processing: {key}")
                
                try:
                    # Get the object and update its ACL
                    obj = bucket.Object(key)
                    obj.Acl().put(ACL='public-read')
                    
                    updated_count += 1
                    print(f"✓ Updated ACL for {key}")
                except Exception as e:
                    print(f"❌ Error updating ACL for {key}: {e}")
                    error_count += 1
        
        print(f"\nUpdated {updated_count} objects")
        if error_count > 0:
            print(f"Failed to update {error_count} objects")
            
        return updated_count > 0
    except Exception as e:
        print(f"❌ Error updating object ACLs: {e}")
        return False

def update_specific_object(key):
    """Update ACL for a specific object"""
    print_header(f"Updating ACL for Specific Object: {key}")
    
    try:
        # Initialize boto3 resource
        s3 = boto3.resource(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME or 'us-east-1'
        )
        
        bucket_name = settings.AWS_STORAGE_BUCKET_NAME
        bucket = s3.Bucket(bucket_name)
        
        # Get the object and update its ACL
        obj = bucket.Object(key)
        obj.Acl().put(ACL='public-read')
        
        print(f"✓ Successfully updated ACL for {key}")
        print(f"✓ The object should now be publicly readable")
        
        # Print the URL for this object
        url = f"https://{settings.AWS_S3_CUSTOM_DOMAIN}/{key}"
        print(f"✓ Object URL: {url}")
        
        return True
    except Exception as e:
        print(f"❌ Error updating object ACL: {e}")
        return False

def list_bucket_contents():
    """List all objects in the bucket"""
    print_header("Listing Bucket Contents")
    
    try:
        # Initialize boto3 client
        s3 = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME or 'us-east-1'
        )
        
        bucket_name = settings.AWS_STORAGE_BUCKET_NAME
        
        # List objects in the bucket
        response = s3.list_objects_v2(Bucket=bucket_name)
        
        if 'Contents' in response:
            objects = response['Contents']
            print(f"Found {len(objects)} objects in the bucket")
            
            for obj in objects[:10]:  # Show just the first 10
                key = obj['Key']
                print(f"- {key}")
                
            if len(objects) > 10:
                print(f"... and {len(objects) - 10} more")
                
            return objects
        else:
            print("No objects found in the bucket")
            return []
    except Exception as e:
        print(f"❌ Error listing bucket contents: {e}")
        return []

def main():
    print("S3 Permissions Fix Utility")
    
    # Check if S3 is enabled
    if not settings.USE_S3:
        print("❌ S3 storage is not enabled (USE_S3 is not True)")
        return
    
    # Print S3 configuration
    print(f"✓ S3 bucket: {settings.AWS_STORAGE_BUCKET_NAME}")
    print(f"✓ AWS region: {settings.AWS_S3_REGION_NAME or 'default'}")
    print(f"✓ S3 domain: {settings.AWS_S3_CUSTOM_DOMAIN}")
    
    # First update the bucket policy
    update_bucket_policy()
    
    # List some contents of the bucket
    objects = list_bucket_contents()
    
    # Update ACLs for all artwork objects
    if objects:
        update_object_acls()
    
    # If you know a specific object that's having issues, update it directly
    specific_key = "media/artworks/test_new_permissions.jpg"
    update_specific_object(specific_key)
    
    print_header("Permissions Update Complete")
    print("""
The S3 bucket and objects should now have the correct permissions.
Try accessing your images again to verify the fix worked.

If you still have issues:
1. Check your AWS console for any S3 bucket restrictions
2. Verify the bucket policy was applied correctly
3. Try refreshing your browser cache when accessing the images
    """)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()