#!/usr/bin/env python3
"""
Direct S3 Upload Script

This script demonstrates how to upload an image directly to S3 without going through Django.
It's useful for testing S3 connectivity and permissions outside of the web application.
"""
import os
import sys
import boto3
import argparse
import logging
from botocore.exceptions import ClientError
from PIL import Image, ImageDraw
import io
import random
import datetime

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_environment():
    """Check if required environment variables are set"""
    required_vars = ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'AWS_STORAGE_BUCKET_NAME']
    missing = []
    
    for var in required_vars:
        if not os.environ.get(var):
            missing.append(var)
    
    if missing:
        logger.error(f"Missing required environment variables: {', '.join(missing)}")
        logger.error("Please set these variables before running this script.")
        return False
    
    logger.info("Environment variables verified.")
    return True

def create_test_image(width=500, height=400, text="Test Image"):
    """Create a simple test image with text and timestamp"""
    # Create a blank image with a colored background
    image = Image.new('RGB', (width, height), color=(73, 109, 137))
    
    # Get a drawing context
    draw = ImageDraw.Draw(image)
    
    # Add text
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    draw.text((10, 10), f"{text}", fill=(255, 255, 255))
    draw.text((10, 50), f"Created: {timestamp}", fill=(255, 255, 255))
    draw.text((10, 90), f"Random ID: {random.randint(1000, 9999)}", fill=(255, 255, 255))
    
    # Add some shapes
    draw.rectangle([(50, 150), (450, 350)], outline=(255, 255, 255), width=2)
    
    # Convert to bytes
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='JPEG')
    img_byte_arr.seek(0)
    
    return img_byte_arr

def upload_to_s3(file_obj, bucket, key, content_type='image/jpeg'):
    """Upload a file to S3"""
    try:
        s3_client = boto3.client('s3')
        
        # Upload the file
        logger.info(f"Uploading to S3 bucket '{bucket}' with key '{key}'...")
        response = s3_client.upload_fileobj(
            file_obj,
            bucket,
            key,
            ExtraArgs={
                'ContentType': content_type
            }
        )
        
        # Generate the URL
        url = f"https://{bucket}.s3.amazonaws.com/{key}"
        
        logger.info(f"Upload successful! Image URL: {url}")
        return url
    
    except ClientError as e:
        logger.error(f"Error uploading to S3: {e}")
        return None

def generate_presigned_url(bucket, key, expiration=3600):
    """Generate a presigned URL for the uploaded object"""
    try:
        s3_client = boto3.client('s3')
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': bucket,
                'Key': key
            },
            ExpiresIn=expiration
        )
        
        logger.info(f"Generated presigned URL (valid for {expiration} seconds): {url}")
        return url
    
    except ClientError as e:
        logger.error(f"Error generating presigned URL: {e}")
        return None

def check_public_access(bucket, key):
    """Check if the object is publicly accessible"""
    public_url = f"https://{bucket}.s3.amazonaws.com/{key}"
    
    try:
        import requests
        response = requests.head(public_url, timeout=5)
        
        if response.status_code == 200:
            logger.info(f"Object is publicly accessible at: {public_url}")
            return True
        else:
            logger.warning(f"Object is not publicly accessible. Status code: {response.status_code}")
            return False
    
    except Exception as e:
        logger.error(f"Error checking public access: {e}")
        return False

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Upload an image directly to S3')
    parser.add_argument('--image', help='Path to image file to upload')
    parser.add_argument('--key', help='S3 key (path) to use for the upload')
    parser.add_argument('--generate', action='store_true', help='Generate a test image instead of using a file')
    args = parser.parse_args()
    
    # Check environment variables
    if not check_environment():
        return 1
    
    # Get bucket name
    bucket = os.environ.get('AWS_STORAGE_BUCKET_NAME')
    
    # Determine the file to upload
    if args.generate:
        logger.info("Generating a test image...")
        file_obj = create_test_image(text="Direct S3 Upload Test")
        
        # Use a timestamp in the key to avoid overwriting existing files
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        key = args.key or f"direct_uploads/test_image_{timestamp}.jpg"
    
    elif args.image:
        # Use the provided image file
        try:
            logger.info(f"Reading image file: {args.image}")
            file_obj = open(args.image, 'rb')
            key = args.key or f"direct_uploads/{os.path.basename(args.image)}"
        except Exception as e:
            logger.error(f"Error opening image file: {e}")
            return 1
    
    else:
        logger.error("Either --image or --generate must be specified")
        parser.print_help()
        return 1
    
    # Upload to S3
    url = upload_to_s3(file_obj, bucket, key)
    
    if not url:
        return 1
    
    # Generate a presigned URL
    presigned_url = generate_presigned_url(bucket, key)
    
    # Check public access
    is_public = check_public_access(bucket, key)
    
    if is_public:
        logger.info("✅ SUCCESS: Image was successfully uploaded and is publicly accessible.")
    else:
        logger.warning("⚠️ WARNING: Image was uploaded but is not publicly accessible.")
        logger.info("You may need to use the presigned URL or check bucket permissions.")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())