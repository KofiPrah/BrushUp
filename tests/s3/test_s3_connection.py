#!/usr/bin/env python
"""
Test script to verify S3 connectivity and bucket policy settings.
This script attempts to upload a test file to S3 and verify it's accessible.
"""

import os
import sys
import boto3
import logging
import requests
from io import BytesIO
from PIL import Image, ImageDraw

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def create_test_image(size=(200, 200), color=(0, 128, 255), text="Test S3 Upload"):
    """Create a simple test image"""
    img = Image.new('RGB', size, color=color)
    draw = ImageDraw.Draw(img)
    draw.text((size[0]//4, size[1]//2), text, fill=(255, 255, 255))
    
    img_bytes = BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    
    return img_bytes

def test_s3_connection():
    """Test connection to S3 and bucket policies"""
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
    
    logger.info(f"Testing S3 connection to bucket: {bucket_name} in region: {region}")
    
    try:
        # Create S3 client
        s3 = boto3.client('s3', region_name=region)
        
        # Test bucket existence
        s3.head_bucket(Bucket=bucket_name)
        logger.info(f"✓ S3 bucket '{bucket_name}' exists and is accessible")
        
        # Test bucket policy
        try:
            policy = s3.get_bucket_policy(Bucket=bucket_name)
            logger.info(f"✓ Bucket has a policy: {policy['Policy'][:100]}...")
        except s3.exceptions.ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchBucketPolicy':
                logger.warning("⚠ Bucket does not have a policy - public access may be restricted")
            else:
                logger.error(f"❌ Error checking bucket policy: {e}")
        
        # Test file upload
        test_key = "test/s3_connection_test.jpg"
        img_data = create_test_image()
        
        logger.info(f"Uploading test image to s3://{bucket_name}/{test_key}")
        s3.upload_fileobj(
            img_data, 
            bucket_name, 
            test_key,
            ExtraArgs={
                'ContentType': 'image/jpeg',
            }
        )
        logger.info("✓ Test image upload successful")
        
        # Get the URL of the uploaded file
        url = f"https://{bucket_name}.s3.{region}.amazonaws.com/{test_key}"
        logger.info(f"Testing public access to: {url}")
        
        # Test public access to the file
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            logger.info(f"✓ File is publicly accessible (HTTP {response.status_code})")
            return True
        else:
            logger.error(f"❌ File is not publicly accessible (HTTP {response.status_code})")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error testing S3 connection: {e}")
        return False

def main():
    """Main test function"""
    success = test_s3_connection()
    
    if success:
        logger.info("✅ S3 connection test PASSED")
        return 0
    else:
        logger.error("❌ S3 connection test FAILED")
        return 1

if __name__ == "__main__":
    sys.exit(main())