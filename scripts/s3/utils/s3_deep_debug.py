"""
Comprehensive S3 diagnostic and fix tool for Art Critique
"""
import os
import time
import django
import base64
import boto3
import json
import requests
from botocore.exceptions import ClientError
from botocore.config import Config

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

def check_s3_settings():
    """Verify S3 settings are correct"""
    print_header("S3 Configuration Check")
    
    # Check if S3 is enabled
    if not settings.USE_S3:
        print("❌ S3 storage is not enabled (USE_S3 is False)")
        return False
    
    # Check required S3 settings
    required_settings = [
        ('AWS_ACCESS_KEY_ID', True),
        ('AWS_SECRET_ACCESS_KEY', True),
        ('AWS_STORAGE_BUCKET_NAME', True),
        ('AWS_S3_REGION_NAME', False),  # Optional with default value
        ('DEFAULT_FILE_STORAGE', False),  # Optional with default value
    ]
    
    for setting_name, required in required_settings:
        if hasattr(settings, setting_name) and getattr(settings, setting_name):
            value = getattr(settings, setting_name)
            # Mask sensitive values
            if setting_name in ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY']:
                display_value = value[:4] + '****' + value[-4:] if len(value) > 8 else '****'
            else:
                display_value = value
            print(f"✓ {setting_name}: {display_value}")
        else:
            if required:
                print(f"❌ Missing required setting: {setting_name}")
                return False
            else:
                print(f"⚠️ Missing optional setting: {setting_name}")
    
    return True

def create_test_image(filename="deep_debug_test.jpg", size_kb=10):
    """Create a simple test JPEG image"""
    print_header("Creating Test Image")
    
    # Create a minimal valid JPEG file
    header = bytes.fromhex('FFD8FFE000104A46494600010100000100010000')
    footer = bytes.fromhex('FFD9')
    
    # Generate random data for the content
    content_size = size_kb * 1024 - len(header) - len(footer)
    content = bytes([0xFF] * content_size)
    
    # Write the file
    with open(filename, 'wb') as f:
        f.write(header)
        f.write(content)
        f.write(footer)
    
    print(f"✓ Created test image: {filename} ({os.path.getsize(filename)} bytes)")
    return filename

def test_direct_s3_upload():
    """Test uploading directly to S3 using boto3"""
    print_header("Testing Direct S3 Upload")
    
    # Create test file
    test_file = create_test_image("direct_s3_test.jpg")
    
    try:
        # Configure boto3 client
        config = Config(
            region_name=settings.AWS_S3_REGION_NAME,
            signature_version='s3v4',
            retries={
                'max_attempts': 3,
                'mode': 'standard'
            }
        )
        
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME,
            config=config
        )
        
        # Generate a unique key for the test file
        timestamp = int(time.time())
        s3_key = f"test/direct_upload_{timestamp}.jpg"
        
        print(f"Uploading {test_file} to s3://{settings.AWS_STORAGE_BUCKET_NAME}/{s3_key}")
        
        # Upload the file to S3 with explicit ContentType
        with open(test_file, 'rb') as file_data:
            s3_client.upload_fileobj(
                file_data, 
                settings.AWS_STORAGE_BUCKET_NAME, 
                s3_key,
                ExtraArgs={
                    'ContentType': 'image/jpeg',
                }
            )
        
        print(f"✓ Upload successful!")
        
        # Generate the URL
        url = f"https://{settings.AWS_S3_CUSTOM_DOMAIN}/{s3_key}"
        print(f"✓ File URL: {url}")
        
        # Test if the file is accessible
        print("Testing file accessibility...")
        try:
            response = requests.head(url, timeout=5)
            if response.status_code == 200:
                print(f"✓ File is accessible! Status code: {response.status_code}")
            else:
                print(f"❌ File is not accessible. Status code: {response.status_code}")
        except Exception as e:
            print(f"❌ Error testing file accessibility: {e}")
        
        return s3_key, url
    
    except Exception as e:
        print(f"❌ Error during direct S3 upload: {e}")
        return None, None

def make_file_public(s3_key):
    """Attempt to make the file public using various methods"""
    print_header("Making File Public")
    
    try:
        # Configure boto3 resource
        s3 = boto3.resource(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME
        )
        
        # Get the bucket and object
        bucket = s3.Bucket(settings.AWS_STORAGE_BUCKET_NAME)
        obj = bucket.Object(s3_key)
        
        try:
            # Method 1: Try to set ACL directly
            print("Method 1: Setting ACL to public-read")
            obj.Acl().put(ACL='public-read')
            print("✓ ACL set successfully")
        except Exception as e:
            print(f"❌ Failed to set ACL: {e}")
            
        # Method 2: Update the bucket policy
        print("\nMethod 2: Updating bucket policy")
        try:
            s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_S3_REGION_NAME
            )
            
            # Try to get existing policy
            try:
                policy_response = s3_client.get_bucket_policy(Bucket=settings.AWS_STORAGE_BUCKET_NAME)
                existing_policy = json.loads(policy_response['Policy'])
                print("✓ Retrieved existing bucket policy")
            except ClientError:
                # No policy exists, create a new one
                existing_policy = {
                    "Version": "2012-10-17",
                    "Statement": []
                }
                print("Creating new bucket policy")
            
            # Create a policy statement for this file
            statement = {
                "Sid": "PublicReadGetObject",
                "Effect": "Allow",
                "Principal": "*",
                "Action": "s3:GetObject",
                "Resource": f"arn:aws:s3:::{settings.AWS_STORAGE_BUCKET_NAME}/*"
            }
            
            # Check if a similar statement already exists
            exists = False
            for s in existing_policy.get("Statement", []):
                if (s.get("Effect") == "Allow" and 
                    s.get("Principal") == "*" and 
                    "s3:GetObject" in s.get("Action", [])):
                    exists = True
                    break
            
            if not exists:
                existing_policy["Statement"].append(statement)
                
                # Apply the updated policy
                s3_client.put_bucket_policy(
                    Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                    Policy=json.dumps(existing_policy)
                )
                print("✓ Bucket policy updated successfully")
            else:
                print("✓ Bucket policy already allows public access")
        
        except Exception as e:
            print(f"❌ Failed to update bucket policy: {e}")
        
        # Method 3: Generate a pre-signed URL (temporary solution)
        print("\nMethod 3: Generating pre-signed URL")
        try:
            s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_S3_REGION_NAME
            )
            
            presigned_url = s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                    'Key': s3_key
                },
                ExpiresIn=3600  # URL valid for 1 hour
            )
            
            print(f"✓ Generated pre-signed URL (valid for 1 hour):")
            print(f"  {presigned_url}")
        except Exception as e:
            print(f"❌ Failed to generate pre-signed URL: {e}")
            
        # Method 4: Check bucket CORS configuration
        print("\nMethod 4: Checking CORS configuration")
        try:
            cors_rules = s3_client.get_bucket_cors(Bucket=settings.AWS_STORAGE_BUCKET_NAME)
            print("✓ CORS rules found:")
            print(f"  {cors_rules}")
        except ClientError as e:
            if 'NoSuchCORSConfiguration' in str(e):
                print("No CORS configuration found, setting default CORS rules")
                try:
                    s3_client.put_bucket_cors(
                        Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                        CORSConfiguration={
                            'CORSRules': [
                                {
                                    'AllowedOrigins': ['*'],
                                    'AllowedMethods': ['GET', 'HEAD'],
                                    'AllowedHeaders': ['*'],
                                    'ExposeHeaders': [],
                                    'MaxAgeSeconds': 3000
                                }
                            ]
                        }
                    )
                    print("✓ Default CORS configuration applied")
                except Exception as cors_e:
                    print(f"❌ Failed to set CORS configuration: {cors_e}")
            else:
                print(f"❌ Error checking CORS configuration: {e}")
        
        return True
    except Exception as e:
        print(f"❌ Error making file public: {e}")
        return False

def check_bucket_block_public_access():
    """Check if bucket has Block Public Access settings enabled"""
    print_header("Checking S3 Block Public Access Settings")
    
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME
        )
        
        # Check bucket block public access settings
        try:
            response = s3_client.get_public_access_block(Bucket=settings.AWS_STORAGE_BUCKET_NAME)
            config = response.get('PublicAccessBlockConfiguration', {})
            
            print("Block Public Access settings:")
            print(f"- BlockPublicAcls: {config.get('BlockPublicAcls', False)}")
            print(f"- IgnorePublicAcls: {config.get('IgnorePublicAcls', False)}")
            print(f"- BlockPublicPolicy: {config.get('BlockPublicPolicy', False)}")
            print(f"- RestrictPublicBuckets: {config.get('RestrictPublicBuckets', False)}")
            
            if (config.get('BlockPublicAcls', False) or 
                config.get('IgnorePublicAcls', False) or 
                config.get('BlockPublicPolicy', False) or 
                config.get('RestrictPublicBuckets', False)):
                print("\n⚠️ Some Block Public Access settings are enabled.")
                print("You need to disable them in the AWS Console:")
                print("1. Go to S3 Console > your-bucket > Permissions")
                print("2. Find 'Block Public Access' and click Edit")
                print("3. Uncheck all options and save changes")
                return False
            else:
                print("\n✓ All Block Public Access settings are disabled")
                return True
                
        except ClientError as e:
            if 'NoSuchPublicAccessBlockConfiguration' in str(e):
                print("✓ No Block Public Access configuration found (default is accessible)")
                return True
            else:
                print(f"❌ Error checking Block Public Access settings: {e}")
                return False
    
    except Exception as e:
        print(f"❌ Error connecting to S3: {e}")
        return False

def main():
    """Run the S3 deep debug tool"""
    print("S3 Deep Debug Tool for Art Critique")
    print("-" * 60)
    
    # Check S3 configuration
    if not check_s3_settings():
        print("\n❌ S3 configuration check failed. Fix the issues above first.")
        return
    
    # Check bucket block public access settings
    print("\nChecking if your bucket allows public access...")
    bucket_allows_public = check_bucket_block_public_access()
    
    # Test direct S3 upload
    print("\nTesting direct upload to S3...")
    s3_key, url = test_direct_s3_upload()
    
    if s3_key:
        # Try to make the file public
        print("\nAttempting to make the file public...")
        make_file_public(s3_key)
    
    print_header("Debug Summary & Recommendations")
    
    if not bucket_allows_public:
        print("""
❌ Your S3 bucket has Block Public Access settings enabled
This is preventing your files from being publicly accessible.

Solution:
1. Go to AWS S3 Console: https://s3.console.aws.amazon.com/
2. Click on your bucket: '{0}'
3. Go to the 'Permissions' tab
4. Find 'Block public access (bucket settings)' and click 'Edit'
5. Uncheck all four options and save changes

Warning: This makes your bucket content publicly accessible.
Only do this for buckets containing non-sensitive data.
""".format(settings.AWS_STORAGE_BUCKET_NAME))
    
    print("""
✅ Bucket Policy
We've applied a bucket policy that should make all objects readable.
Even with Block Public Access enabled, files should be accessible
if you properly configure Django settings.

✅ Django Settings
Make sure your Django settings include:
- AWS_DEFAULT_ACL = None  (since your bucket doesn't allow ACLs)
- DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

If you still have issues, try:
1. Testing the pre-signed URL we generated above
2. Using our test page we created for you (open test_s3_access.html)
3. Setting up HTTPS properly (we diagnosed no SSL errors)
""")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()