#!/usr/bin/env python3
"""
Fix S3 Media Folder Permissions

This script updates the S3 bucket policy to allow public access to the media folder
where Django-uploaded images are stored.
"""
import os
import sys
import json
import boto3
import logging
from botocore.exceptions import ClientError

# Set up logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def update_bucket_policy():
    """Update the bucket policy to allow public read access to media files"""
    # Get AWS credentials from environment
    aws_access_key = os.environ.get('AWS_ACCESS_KEY_ID')
    aws_secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
    bucket_name = os.environ.get('AWS_STORAGE_BUCKET_NAME')
    
    if not (aws_access_key and aws_secret_key and bucket_name):
        logger.error("Missing required AWS credentials in environment variables")
        return False
    
    logger.info(f"Updating policy for bucket: {bucket_name}")
    
    # Create S3 client
    s3_client = boto3.client('s3',
                            aws_access_key_id=aws_access_key,
                            aws_secret_access_key=aws_secret_key)
    
    # Create policy document to allow public read access to media files
    policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "PublicReadForMediaObjects",
                "Effect": "Allow",
                "Principal": "*",
                "Action": "s3:GetObject",
                "Resource": [
                    f"arn:aws:s3:::{bucket_name}/media/*",
                    f"arn:aws:s3:::{bucket_name}/direct_uploads/*"
                ]
            }
        ]
    }
    
    try:
        # Apply the policy to the bucket
        s3_client.put_bucket_policy(
            Bucket=bucket_name,
            Policy=json.dumps(policy)
        )
        logger.info("Successfully updated bucket policy")
        return True
    except ClientError as e:
        logger.error(f"Error updating bucket policy: {e}")
        return False

def test_s3_access():
    """Test access to S3 media files"""
    # Test URLs - update these with actual paths to test
    test_urls = [
        "https://brushup-media.s3.amazonaws.com/media/artworks/test_artwork_EhkFSNr.jpg",
        "https://brushup-media.s3.amazonaws.com/direct_uploads/test_image_20250517015003.jpg"
    ]
    
    import requests
    
    logger.info("Testing access to S3 files:")
    for url in test_urls:
        try:
            response = requests.head(url, timeout=5)
            status = "✅ ACCESSIBLE" if response.status_code == 200 else f"❌ NOT ACCESSIBLE (Status: {response.status_code})"
            logger.info(f"{status} - {url}")
        except Exception as e:
            logger.error(f"❌ ERROR testing {url}: {e}")

def main():
    """Main function to fix S3 permissions and test access"""
    logger.info("Starting S3 permission fix...")
    
    # Update bucket policy
    success = update_bucket_policy()
    
    if success:
        logger.info("✅ Bucket policy updated successfully")
        # Test access after updating policy
        logger.info("Testing access after policy update...")
        test_s3_access()
    else:
        logger.error("❌ Failed to update bucket policy")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())