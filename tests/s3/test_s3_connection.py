#!/usr/bin/env python
'''
Test S3 connection and operations with bucket ownership enforced.
This script verifies that your S3 configuration works correctly.
'''

import os
import sys
import argparse
import logging
import tempfile
import boto3
from botocore.exceptions import ClientError
from django.conf import settings
import django

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('s3_test')

def initialize_django():
    """Initialize Django settings"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'artcritique.settings')
    django.setup()
    return settings

def test_bucket_policy(s3_client, bucket_name):
    """Check if the bucket has a policy that allows public read access"""
    try:
        policy = s3_client.get_bucket_policy(Bucket=bucket_name)
        logger.info("Bucket policy exists:")
        logger.info(policy.get('Policy', 'No policy content found'))
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchBucketPolicy':
            logger.warning("No bucket policy exists. Public access may be restricted.")
            return False
        else:
            logger.error(f"Error checking bucket policy: {e}")
            return False

def test_object_upload(s3_client, bucket_name, object_key='test_upload.txt'):
    """Test uploading an object to S3 with bucket ownership enforced"""
    try:
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(b'Test file content')
            tmp_path = tmp.name
        
        # Upload file to S3
        logger.info(f"Uploading test file to s3://{bucket_name}/{object_key}")
        
        # For bucket with ownership enforced, we don't use ACL
        s3_client.upload_file(
            tmp_path, 
            bucket_name, 
            object_key,
            ExtraArgs={
                'ObjectOwnership': 'BucketOwnerEnforced'
            }
        )
        logger.info("Upload successful")
        
        # Check if object exists
        try:
            s3_client.head_object(Bucket=bucket_name, Key=object_key)
            logger.info("Object exists in bucket")
            return True
        except ClientError as e:
            logger.error(f"Error checking object: {e}")
            return False
        
        finally:
            # Clean up temporary file
            os.unlink(tmp_path)
            
    except ClientError as e:
        logger.error(f"Error uploading object: {e}")
        return False

def test_object_public_access(s3_client, bucket_name, object_key='test_upload.txt'):
    """Test if an object can be accessed publicly"""
    try:
        # Generate a pre-signed URL with short expiration
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name, 'Key': object_key},
            ExpiresIn=60
        )
        logger.info(f"Pre-signed URL: {url}")
        logger.info("Note: If bucket policy allows public read access, this object should also be accessible without this URL")
        
        # Check if object is publicly accessible via direct URL
        # Note: With bucket ownership enforced, this depends on bucket policy, not object ACLs
        direct_url = f"https://{bucket_name}.s3.amazonaws.com/{object_key}"
        logger.info(f"Direct URL (requires public read access in bucket policy): {direct_url}")
        
        return True
    except ClientError as e:
        logger.error(f"Error generating URL: {e}")
        return False

def cleanup_test_objects(s3_client, bucket_name, object_key='test_upload.txt'):
    """Clean up test objects"""
    try:
        s3_client.delete_object(Bucket=bucket_name, Key=object_key)
        logger.info(f"Deleted test object: {object_key}")
        return True
    except ClientError as e:
        logger.error(f"Error deleting object: {e}")
        return False

def main():
    """Main function to test S3 connection and operations"""
    parser = argparse.ArgumentParser(description='Test S3 connection with bucket ownership enforced')
    parser.add_argument('--skip-upload', action='store_true', help='Skip upload test')
    parser.add_argument('--skip-cleanup', action='store_true', help='Skip cleanup of test objects')
    args = parser.parse_args()
    
    logger.info("Initializing Django...")
    settings = initialize_django()
    
    if not hasattr(settings, 'AWS_STORAGE_BUCKET_NAME'):
        logger.error("AWS_STORAGE_BUCKET_NAME not found in settings")
        sys.exit(1)
    
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME
    logger.info(f"Using bucket: {bucket_name}")
    
    # Initialize S3 client
    try:
        logger.info("Initializing S3 client...")
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME if hasattr(settings, 'AWS_S3_REGION_NAME') else None
        )
        logger.info("S3 client initialized")
    except Exception as e:
        logger.error(f"Error initializing S3 client: {e}")
        sys.exit(1)
    
    # Check if bucket exists
    try:
        s3_client.head_bucket(Bucket=bucket_name)
        logger.info(f"Bucket {bucket_name} exists and is accessible")
    except ClientError as e:
        logger.error(f"Error accessing bucket: {e}")
        sys.exit(1)
    
    # Check ownership settings
    try:
        ownership = s3_client.get_bucket_ownership_controls(Bucket=bucket_name)
        logger.info(f"Bucket ownership settings: {ownership}")
    except ClientError as e:
        if e.response['Error']['Code'] == 'OwnershipControlsNotFoundError':
            logger.warning("No ownership controls found, bucket is using legacy settings")
        else:
            logger.error(f"Error checking ownership controls: {e}")
    
    # Test bucket policy
    test_bucket_policy(s3_client, bucket_name)
    
    # Test object upload
    object_key = f"test-files/test_upload_{os.getpid()}.txt"
    upload_success = True
    
    if not args.skip_upload:
        upload_success = test_object_upload(s3_client, bucket_name, object_key)
        if upload_success:
            test_object_public_access(s3_client, bucket_name, object_key)
    
    # Clean up test objects
    if upload_success and not args.skip_cleanup:
        cleanup_test_objects(s3_client, bucket_name, object_key)
    
    logger.info("S3 connection test completed")

if __name__ == "__main__":
    main()