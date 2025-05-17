#!/usr/bin/env python
"""
Update the bucket policy to allow public read access to all objects.
This is an alternative to ACLs when Block Public Access settings are enabled.
"""

import os
import sys
import json
import boto3
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def update_bucket_policy():
    """Add a bucket policy that allows public read access to all objects"""
    # Check for required environment variables
    required_vars = [
        "AWS_ACCESS_KEY_ID", 
        "AWS_SECRET_ACCESS_KEY", 
        "AWS_STORAGE_BUCKET_NAME",
        "AWS_S3_REGION_NAME"
    ]
    
    for var in required_vars:
        if not os.environ.get(var):
            logger.error(f"Missing required environment variable: {var}")
            return False
    
    # Get S3 configuration from environment
    bucket_name = os.environ.get("AWS_STORAGE_BUCKET_NAME")
    region = os.environ.get("AWS_S3_REGION_NAME")
    
    logger.info(f"Updating bucket policy for: {bucket_name} in region: {region}")
    
    try:
        # Create S3 client
        s3 = boto3.client('s3', region_name=region)
        
        # Test bucket existence
        s3.head_bucket(Bucket=bucket_name)
        logger.info(f"✓ S3 bucket '{bucket_name}' exists and is accessible")
        
        # Define the bucket policy for public read access
        bucket_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "PublicReadForGetBucketObjects",
                    "Effect": "Allow",
                    "Principal": "*",
                    "Action": "s3:GetObject",
                    "Resource": f"arn:aws:s3:::{bucket_name}/*"
                }
            ]
        }
        
        # Convert the policy to JSON
        bucket_policy = json.dumps(bucket_policy)
        
        # Set the new bucket policy
        s3.put_bucket_policy(Bucket=bucket_name, Policy=bucket_policy)
        logger.info("✓ Bucket policy updated successfully")
        
        # Verify the policy was set
        response = s3.get_bucket_policy(Bucket=bucket_name)
        logger.info(f"✓ New policy: {response['Policy']}")
        
        return True
    except Exception as e:
        logger.error(f"❌ Error updating bucket policy: {e}")
        return False

def main():
    """Main function"""
    success = update_bucket_policy()
    
    if success:
        logger.info("✅ Bucket policy update SUCCESSFUL")
        return 0
    else:
        logger.error("❌ Bucket policy update FAILED")
        return 1

if __name__ == "__main__":
    sys.exit(main())