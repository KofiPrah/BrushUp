#!/usr/bin/env python3
"""
Update S3 Bucket Policy

This script updates the S3 bucket policy to allow public read access to media files
while maintaining bucket ownership enforcement.
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

def get_current_policy(s3_client, bucket_name):
    """Get the current bucket policy if it exists"""
    try:
        response = s3_client.get_bucket_policy(Bucket=bucket_name)
        logger.info("Current bucket policy exists.")
        return json.loads(response['Policy'])
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchBucketPolicy':
            logger.info("No existing bucket policy found.")
            return None
        else:
            logger.error(f"Error getting bucket policy: {e}")
            raise

def create_public_read_policy(bucket_name):
    """Create a bucket policy that allows public read access to media files"""
    policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "PublicReadForMediaObjects",
                "Effect": "Allow",
                "Principal": "*",
                "Action": ["s3:GetObject"],
                "Resource": [
                    f"arn:aws:s3:::{bucket_name}/media/*",
                    f"arn:aws:s3:::{bucket_name}/direct_uploads/*"
                ]
            }
        ]
    }
    return policy

def update_bucket_policy(s3_client, bucket_name, policy):
    """Update the bucket policy"""
    try:
        s3_client.put_bucket_policy(
            Bucket=bucket_name,
            Policy=json.dumps(policy)
        )
        logger.info("Bucket policy updated successfully.")
        return True
    except ClientError as e:
        logger.error(f"Error updating bucket policy: {e}")
        return False

def verify_bucket_ownership_settings(s3_client, bucket_name):
    """Verify and fix bucket ownership settings"""
    try:
        # Get current ownership controls
        response = s3_client.get_bucket_ownership_controls(Bucket=bucket_name)
        current_rule = response['OwnershipControls']['Rules'][0]['ObjectOwnership']
        logger.info(f"Current bucket ownership setting: {current_rule}")
        
        # If not already set to BucketOwnerEnforced, update it
        if current_rule != 'BucketOwnerEnforced':
            logger.info(f"Updating bucket ownership from {current_rule} to BucketOwnerEnforced")
            s3_client.put_bucket_ownership_controls(
                Bucket=bucket_name,
                OwnershipControls={
                    'Rules': [
                        {
                            'ObjectOwnership': 'BucketOwnerEnforced'
                        }
                    ]
                }
            )
            logger.info("Bucket ownership updated to BucketOwnerEnforced")
        else:
            logger.info("Bucket ownership already set to BucketOwnerEnforced - no change needed")
        
        return True
    except ClientError as e:
        if 'OwnershipControlsNotFoundError' in str(e):
            # If ownership controls are not set, set them to BucketOwnerEnforced
            logger.info("No ownership controls found. Setting to BucketOwnerEnforced")
            try:
                s3_client.put_bucket_ownership_controls(
                    Bucket=bucket_name,
                    OwnershipControls={
                        'Rules': [
                            {
                                'ObjectOwnership': 'BucketOwnerEnforced'
                            }
                        ]
                    }
                )
                logger.info("Bucket ownership set to BucketOwnerEnforced")
                return True
            except ClientError as inner_e:
                logger.error(f"Error setting bucket ownership: {inner_e}")
                return False
        else:
            logger.error(f"Error checking bucket ownership: {e}")
            return False

def verify_public_access_settings(s3_client, bucket_name):
    """Verify and fix public access block settings"""
    try:
        # Get current public access block settings
        response = s3_client.get_public_access_block(Bucket=bucket_name)
        current_settings = response['PublicAccessBlockConfiguration']
        logger.info(f"Current public access block settings: {current_settings}")
        
        # If "Block all public access" is enabled, disable it or modify as needed
        if (current_settings['BlockPublicAcls'] and
            current_settings['IgnorePublicAcls'] and
            current_settings['BlockPublicPolicy'] and
            current_settings['RestrictPublicBuckets']):
            
            logger.info("Public access is completely blocked. Updating settings to allow public read through bucket policy")
            s3_client.put_public_access_block(
                Bucket=bucket_name,
                PublicAccessBlockConfiguration={
                    'BlockPublicAcls': True,
                    'IgnorePublicAcls': True,
                    'BlockPublicPolicy': False,
                    'RestrictPublicBuckets': False
                }
            )
            logger.info("Public access block settings updated to allow public read through bucket policy")
        elif current_settings['BlockPublicPolicy'] or current_settings['RestrictPublicBuckets']:
            logger.info("Public bucket policies are blocked. Updating settings")
            s3_client.put_public_access_block(
                Bucket=bucket_name,
                PublicAccessBlockConfiguration={
                    'BlockPublicAcls': current_settings['BlockPublicAcls'],
                    'IgnorePublicAcls': current_settings['IgnorePublicAcls'],
                    'BlockPublicPolicy': False,
                    'RestrictPublicBuckets': False
                }
            )
            logger.info("Public access block settings updated to allow public policies")
        else:
            logger.info("Public access settings are already configured to allow bucket policies - no change needed")
        
        return True
    except ClientError as e:
        if 'NoSuchPublicAccessBlockConfiguration' in str(e):
            # If public access block is not configured, that's actually good for us
            logger.info("No public access block configuration found - bucket can use public policies")
            return True
        else:
            logger.error(f"Error checking public access block: {e}")
            return False

def main():
    """Main function"""
    logger.info("Starting S3 bucket policy update...")
    
    # Check environment variables
    if not check_environment():
        return 1
    
    # Get bucket name from environment
    bucket_name = os.environ.get('AWS_STORAGE_BUCKET_NAME')
    logger.info(f"Working with S3 bucket: {bucket_name}")
    
    # Create S3 client
    s3_client = boto3.client('s3')
    
    # Verify bucket ownership settings
    if not verify_bucket_ownership_settings(s3_client, bucket_name):
        logger.warning("Unable to verify bucket ownership settings. Continuing anyway...")
    
    # Verify public access block settings
    if not verify_public_access_settings(s3_client, bucket_name):
        logger.warning("Unable to verify public access block settings. Continuing anyway...")
    
    # Get current policy
    current_policy = get_current_policy(s3_client, bucket_name)
    
    # Create new public read policy
    new_policy = create_public_read_policy(bucket_name)
    
    # If there's an existing policy, we might want to merge them instead of replacing
    # This is a simple case - we'll just replace the policy for now
    
    # Update bucket policy
    if update_bucket_policy(s3_client, bucket_name, new_policy):
        logger.info(f"✅ SUCCESS: S3 bucket policy for {bucket_name} has been updated to allow public read access to media files.")
        logger.info("Media files in the following paths are now publicly accessible:")
        logger.info(f"- https://{bucket_name}.s3.amazonaws.com/media/*")
        logger.info(f"- https://{bucket_name}.s3.amazonaws.com/direct_uploads/*")
        
        # Verify the policy was applied
        try:
            updated_policy = get_current_policy(s3_client, bucket_name)
            if updated_policy:
                logger.info("Updated bucket policy:")
                logger.info(json.dumps(updated_policy, indent=2))
            else:
                logger.error("Failed to retrieve updated policy. Please check the AWS console.")
        except Exception as e:
            logger.error(f"Error verifying updated policy: {e}")
        
        return 0
    else:
        logger.error(f"❌ FAILED: Could not update S3 bucket policy for {bucket_name}.")
        return 1

if __name__ == "__main__":
    sys.exit(main())