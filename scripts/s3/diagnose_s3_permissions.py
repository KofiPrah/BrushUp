"""
Diagnostic tool for S3 bucket permissions
"""
import os
import django
import boto3
import json
from botocore.exceptions import ClientError

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'artcritique.settings')
django.setup()

from django.conf import settings

def print_header(text):
    """Print formatted header text"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)

def check_s3_configuration():
    """Check Django S3 settings"""
    print_header("Django S3 Configuration")
    
    # Check if S3 is enabled
    if not settings.USE_S3:
        print("❌ S3 storage is not enabled. Set USE_S3=True to enable.")
        return False
        
    # Check AWS credentials
    required_settings = [
        'AWS_ACCESS_KEY_ID', 
        'AWS_SECRET_ACCESS_KEY', 
        'AWS_STORAGE_BUCKET_NAME',
        'AWS_DEFAULT_ACL'
    ]
    
    for setting_name in required_settings:
        value = getattr(settings, setting_name, None)
        if value:
            # Mask sensitive values
            if setting_name in ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY']:
                display_value = value[:4] + '****' + value[-4:] if len(value) > 8 else '****'
            else:
                display_value = value
            print(f"✓ {setting_name}: {display_value}")
        else:
            print(f"❌ Missing {setting_name}")
            
    # Check storage backend
    storage = getattr(settings, 'DEFAULT_FILE_STORAGE', None)
    print(f"✓ Storage backend: {storage}")
    
    # Check ACL settings
    acl = getattr(settings, 'AWS_DEFAULT_ACL', None)
    if acl == 'public-read':
        print("✓ Default ACL is public-read (good for public files)")
    else:
        print(f"⚠️ Default ACL is {acl} (may not allow public access)")
        
    return True

def check_s3_bucket_settings():
    """Check S3 bucket configuration using boto3"""
    print_header("S3 Bucket Configuration")
    
    # Initialize boto3 client
    try:
        s3 = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME or 'us-east-1'
        )
        
        bucket_name = settings.AWS_STORAGE_BUCKET_NAME
        print(f"✓ Connected to S3 service")
        print(f"✓ Target bucket: {bucket_name}")
        
        # Check if bucket exists
        try:
            s3.head_bucket(Bucket=bucket_name)
            print(f"✓ Bucket exists and is accessible")
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            if error_code == '404':
                print(f"❌ Bucket does not exist: {bucket_name}")
            elif error_code == '403':
                print(f"❌ Permission denied to access bucket: {bucket_name}")
            else:
                print(f"❌ Error accessing bucket: {error_code}")
            return False
            
        # Check bucket public access settings
        try:
            public_access = s3.get_public_access_block(Bucket=bucket_name)
            block_settings = public_access.get('PublicAccessBlockConfiguration', {})
            
            if block_settings.get('BlockPublicAcls', False):
                print("❌ BlockPublicAcls is enabled - This blocks public ACLs")
            else:
                print("✓ BlockPublicAcls is disabled - ACLs can be public")
                
            if block_settings.get('IgnorePublicAcls', False):
                print("❌ IgnorePublicAcls is enabled - Public ACLs are ignored")
            else:
                print("✓ IgnorePublicAcls is disabled - Public ACLs are honored")
                
            if block_settings.get('BlockPublicPolicy', False):
                print("❌ BlockPublicPolicy is enabled - Public policies are blocked")
            else:
                print("✓ BlockPublicPolicy is disabled - Public policies are allowed")
                
            if block_settings.get('RestrictPublicBuckets', False):
                print("❌ RestrictPublicBuckets is enabled - Public access is restricted")
            else:
                print("✓ RestrictPublicBuckets is disabled - Public access is allowed")
                
        except ClientError as e:
            print(f"⚠️ Could not check public access settings: {e}")
        
        # Check CORS configuration
        try:
            cors = s3.get_bucket_cors(Bucket=bucket_name)
            print("✓ CORS configuration exists")
            
            # Print CORS rules
            if 'CORSRules' in cors:
                for rule in cors['CORSRules']:
                    origins = rule.get('AllowedOrigins', [])
                    methods = rule.get('AllowedMethods', [])
                    
                    origin_str = ', '.join(origins) if origins else 'None'
                    methods_str = ', '.join(methods) if methods else 'None'
                    
                    print(f"  - Origins: {origin_str}")
                    print(f"  - Methods: {methods_str}")
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchCORSConfiguration':
                print("⚠️ No CORS configuration found")
            else:
                print(f"⚠️ Error checking CORS: {e}")
        
        # Check bucket policy
        try:
            policy = s3.get_bucket_policy(Bucket=bucket_name)
            if 'Policy' in policy:
                print("✓ Bucket policy exists")
                
                # Parse and check if policy allows public read
                policy_json = json.loads(policy['Policy'])
                has_public_read = False
                
                for statement in policy_json.get('Statement', []):
                    if (statement.get('Effect') == 'Allow' and 
                        statement.get('Principal', {}) == '*' and
                        's3:GetObject' in statement.get('Action', [])):
                        has_public_read = True
                
                if has_public_read:
                    print("✓ Bucket policy allows public read access")
                else:
                    print("⚠️ Bucket policy may not allow public read access")
                
            else:
                print("⚠️ No bucket policy found")
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchBucketPolicy':
                print("⚠️ No bucket policy found")
            else:
                print(f"⚠️ Error checking bucket policy: {e}")
        
        # Check object ACLs on a test object
        try:
            # List some objects to check
            objects = s3.list_objects_v2(Bucket=bucket_name, MaxKeys=5)
            
            if 'Contents' in objects and objects['Contents']:
                sample_key = objects['Contents'][0]['Key']
                print(f"\nChecking ACL for sample object: {sample_key}")
                
                try:
                    acl = s3.get_object_acl(Bucket=bucket_name, Key=sample_key)
                    
                    # Check for public-read grant
                    has_public_read = False
                    for grant in acl.get('Grants', []):
                        grantee = grant.get('Grantee', {})
                        uri = grantee.get('URI', '')
                        permission = grant.get('Permission', '')
                        
                        if 'http://acs.amazonaws.com/groups/global/AllUsers' in uri and permission == 'READ':
                            has_public_read = True
                    
                    if has_public_read:
                        print("✓ Object has public-read permission")
                    else:
                        print("❌ Object does not have public-read permission")
                        
                except ClientError as e:
                    print(f"⚠️ Could not check object ACL: {e}")
            else:
                print("⚠️ No objects found in bucket to check ACLs")
                
        except ClientError as e:
            print(f"⚠️ Error listing objects: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error connecting to S3: {e}")
        return False

def suggest_fixes():
    """Provide suggestions to fix S3 permission issues"""
    print_header("Suggested Fixes for S3 Permissions")
    
    print("""
1. Disable S3 Block Public Access settings:
   - Go to your S3 bucket in AWS console
   - Click on "Permissions" tab
   - Find "Block public access" and click "Edit"
   - Uncheck all four options to allow public access
   - Click "Save changes"

2. Add a bucket policy to allow public read access:
   - Go to "Bucket Policy" under the "Permissions" tab
   - Add a policy like:
   
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Sid": "PublicReadGetObject",
         "Effect": "Allow",
         "Principal": "*",
         "Action": "s3:GetObject",
         "Resource": "arn:aws:s3:::YOUR-BUCKET-NAME/*"
       }
     ]
   }
   
   (Replace YOUR-BUCKET-NAME with your actual bucket name)

3. Set proper CORS configuration:
   - Go to "CORS configuration" under the "Permissions" tab
   - Add a configuration like:
   
   [
     {
       "AllowedOrigins": ["*"],
       "AllowedMethods": ["GET"],
       "AllowedHeaders": ["*"],
       "ExposeHeaders": [],
       "MaxAgeSeconds": 3000
     }
   ]

4. Re-upload files and ensure they have the correct ACL:
   - When uploading files, explicitly set ACL to "public-read"
   - For existing files, you may need to update their ACL
    """)

def main():
    print("Diagnosing S3 Permission Issues\n")
    
    # Check Django configuration
    django_config_ok = check_s3_configuration()
    
    # If Django config is okay, check S3 bucket settings
    if django_config_ok:
        s3_bucket_ok = check_s3_bucket_settings()
    
    # Suggest fixes
    suggest_fixes()
    
    print("\nDiagnosis complete. See above for details and suggested fixes.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error running diagnostic: {e}")
        import traceback
        traceback.print_exc()