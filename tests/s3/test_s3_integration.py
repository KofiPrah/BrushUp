#!/usr/bin/env python3
"""
Test script for S3 integration with the Art Critique application.
This script verifies that S3 storage is properly configured and working.
"""
import os
import sys
import boto3
import argparse
from botocore.exceptions import ClientError
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_environment_variables():
    """Check if required environment variables are set"""
    required_vars = [
        'AWS_ACCESS_KEY_ID',
        'AWS_SECRET_ACCESS_KEY', 
        'AWS_STORAGE_BUCKET_NAME',
        'USE_S3'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        return False
    
    # Check USE_S3 value
    use_s3 = os.environ.get('USE_S3', 'False').lower() == 'true'
    if not use_s3:
        logger.warning("USE_S3 is not set to True, S3 storage is disabled")
        return False
    
    logger.info("All required environment variables are set")
    return True

def check_s3_connection():
    """Check if we can connect to S3"""
    try:
        # Create S3 client
        s3 = boto3.client('s3')
        
        # Try a simple operation
        response = s3.list_buckets()
        
        # Log the bucket names
        buckets = [bucket['Name'] for bucket in response['Buckets']]
        logger.info(f"Connected to S3, available buckets: {', '.join(buckets)}")
        
        return True
    except ClientError as e:
        logger.error(f"Failed to connect to S3: {e}")
        return False

def check_target_bucket():
    """Check if the target bucket exists and is accessible"""
    bucket_name = os.environ.get('AWS_STORAGE_BUCKET_NAME')
    
    if not bucket_name:
        logger.error("AWS_STORAGE_BUCKET_NAME environment variable not set")
        return False
    
    try:
        # Create S3 client
        s3 = boto3.client('s3')
        
        # Check if bucket exists
        response = s3.head_bucket(Bucket=bucket_name)
        
        # If no exception, bucket exists and is accessible
        logger.info(f"Successfully connected to bucket: {bucket_name}")
        
        # List a few objects in the bucket
        try:
            response = s3.list_objects_v2(Bucket=bucket_name, MaxKeys=5)
            
            if 'Contents' in response:
                object_count = len(response['Contents'])
                logger.info(f"Bucket contains {object_count} objects (showing up to 5)")
                
                for obj in response['Contents']:
                    logger.info(f"  - {obj['Key']} ({obj['Size']} bytes)")
            else:
                logger.info("Bucket is empty")
        except ClientError as e:
            logger.warning(f"Could not list objects in bucket: {e}")
        
        return True
    except ClientError as e:
        logger.error(f"Failed to access bucket {bucket_name}: {e}")
        return False

def test_create_object():
    """Test creating a new object in the bucket"""
    bucket_name = os.environ.get('AWS_STORAGE_BUCKET_NAME')
    
    if not bucket_name:
        logger.error("AWS_STORAGE_BUCKET_NAME environment variable not set")
        return False
    
    test_key = 'test_integration.txt'
    test_content = 'This is a test file created by test_s3_integration.py'
    
    try:
        # Create S3 client
        s3 = boto3.client('s3')
        
        # Put object
        s3.put_object(
            Bucket=bucket_name,
            Key=test_key,
            Body=test_content,
            ContentType='text/plain'
        )
        
        logger.info(f"Successfully created test object: {test_key}")
        
        # Verify object exists
        response = s3.head_object(Bucket=bucket_name, Key=test_key)
        logger.info(f"Object verified with size: {response['ContentLength']} bytes")
        
        # Get the object
        response = s3.get_object(Bucket=bucket_name, Key=test_key)
        content = response['Body'].read().decode('utf-8')
        
        if content == test_content:
            logger.info("Object content verified")
            return True
        else:
            logger.error("Object content does not match what was uploaded")
            return False
    except ClientError as e:
        logger.error(f"Failed to create/verify test object: {e}")
        return False

def main():
    """Run S3 integration tests"""
    parser = argparse.ArgumentParser(description="Test S3 integration with Art Critique")
    parser.add_argument("--skip-upload", action="store_true", 
                        help="Skip uploading a test file to S3")
    args = parser.parse_args()
    
    logger.info("=== S3 Integration Test ===")
    
    success = True
    
    # Check environment variables
    logger.info("Checking environment variables...")
    env_check = check_environment_variables()
    success = success and env_check
    
    if not env_check:
        logger.error("Environment check failed, skipping further tests")
        return 1
    
    # Check S3 connection
    logger.info("Checking S3 connection...")
    conn_check = check_s3_connection()
    success = success and conn_check
    
    if not conn_check:
        logger.error("S3 connection check failed, skipping further tests")
        return 1
    
    # Check target bucket
    logger.info("Checking target bucket...")
    bucket_check = check_target_bucket()
    success = success and bucket_check
    
    if not bucket_check:
        logger.error("Target bucket check failed, skipping further tests")
        return 1
    
    # Test creating object
    if not args.skip_upload:
        logger.info("Testing object creation...")
        upload_check = test_create_object()
        success = success and upload_check
    
    if success:
        logger.info("\nAll S3 integration tests passed successfully!")
        return 0
    else:
        logger.error("\nSome S3 integration tests failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
