"""
Script to verify the S3 connection for the Art Critique application.
This script will check if we can connect to S3 and list the contents of the bucket.
"""

import os
import boto3
from botocore.exceptions import ClientError

def verify_s3_connection():
    """Verify that we can connect to S3 and access the bucket."""
    print("=== Verifying S3 Connection ===")
    
    # Check if the environment variables are set
    required_vars = ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'AWS_STORAGE_BUCKET_NAME']
    for var in required_vars:
        if not os.environ.get(var):
            print(f"❌ ERROR: Environment variable {var} is not set")
            return False
    
    # Get the AWS credentials and bucket name
    aws_access_key = os.environ.get('AWS_ACCESS_KEY_ID')
    aws_secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
    bucket_name = os.environ.get('AWS_STORAGE_BUCKET_NAME')
    region_name = os.environ.get('AWS_S3_REGION_NAME', 'us-east-1')
    
    print(f"✓ Found all required environment variables")
    print(f"✓ Using bucket: {bucket_name} in region: {region_name}")
    
    try:
        # Create an S3 client
        s3 = boto3.client(
            's3',
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=region_name
        )
        
        # Test if we can list objects in the bucket
        print("✓ Successfully created S3 client")
        print(f"Attempting to list objects in bucket '{bucket_name}'...")
        
        response = s3.list_objects_v2(Bucket=bucket_name, MaxKeys=5)
        
        # Check if the bucket is empty or has content
        if 'Contents' in response:
            print(f"✓ Successfully listed objects. Found {len(response['Contents'])} objects in the bucket.")
            for obj in response['Contents'][:5]:  # Show up to 5 objects
                print(f"  - {obj['Key']} ({obj['Size']} bytes)")
        else:
            print("✓ Successfully connected to bucket. The bucket is empty.")
        
        # Test uploading a small test file
        print("\nTesting upload capability...")
        test_content = b"This is a test file to verify S3 upload functionality."
        test_key = "test_upload.txt"
        
        s3.put_object(
            Bucket=bucket_name,
            Key=test_key,
            Body=test_content,
            ContentType='text/plain'
        )
        
        print(f"✓ Successfully uploaded test file: {test_key}")
        
        # Generate a pre-signed URL for verification
        url = s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name, 'Key': test_key},
            ExpiresIn=3600  # URL valid for 1 hour
        )
        
        print(f"✓ Test file accessible at (temporary URL):\n{url}")
        
        return True
        
    except ClientError as e:
        print(f"❌ AWS S3 Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    if verify_s3_connection():
        print("\n✅ SUCCESS: S3 connection verified! Your application is ready to use S3 for storage.")
    else:
        print("\n❌ FAILED: Could not verify S3 connection. Please check your AWS credentials and settings.")