# AWS S3 Configuration for Art Critique

This guide explains how to configure and use AWS S3 storage for the Art Critique application on Replit.

## Setup Instructions

### Prerequisites
- AWS Account
- S3 bucket created
- IAM user with appropriate permissions
- AWS credentials (access key and secret key)

### Environment Variables
The following environment variables must be set:

- `USE_S3`: Set to `True` to enable S3 storage
- `AWS_ACCESS_KEY_ID`: Your AWS access key
- `AWS_SECRET_ACCESS_KEY`: Your AWS secret key
- `AWS_STORAGE_BUCKET_NAME`: Your S3 bucket name
- `AWS_S3_REGION_NAME`: AWS region (e.g., "us-east-1")

### Starting the Application with S3 Enabled

Use one of the provided scripts to start the application with S3 storage enabled:

```bash
# Option 1: Use the shell script
./start_with_s3.sh

# Option 2: Use the Python script
python run_app_with_s3.py
```

## S3 Bucket Configuration

Your S3 bucket needs the following configuration:

1. **Block Public Access settings**: All four settings should be unchecked
2. **Bucket Policy**: A policy allowing public read access
3. **CORS Configuration**: Appropriate CORS settings for your domain

You can run the included diagnostic tool to check your configuration:

```bash
python diagnose_s3_permissions.py
```

## Fixing S3 Permissions

If you encounter permission issues with S3, use the provided fix script:

```bash
./apply_s3_fixes.sh
```

This script will:
1. Run diagnostics to identify issues
2. Update the bucket policy to allow public access
3. Apply `public-read` ACL to all existing uploads
4. Verify the fixes with another diagnostic run

## Troubleshooting S3 Access

Common issues and solutions:

1. **403 Forbidden errors**:
   - Check bucket policy
   - Verify object ACLs
   - Check Block Public Access settings

2. **Images not displaying**:
   - Ensure objects have `public-read` ACL
   - Verify the URL format is correct
   - Check CORS configuration if loading from the frontend

3. **Upload failures**:
   - Verify AWS credentials
   - Check IAM permissions
   - Ensure bucket exists and is accessible

## Implementation Details

The Art Critique application uses the following classes for S3 storage:

- `PublicMediaStorage`: For publicly accessible media files
- `PrivateMediaStorage`: For protected files requiring authentication
- `StaticStorage`: For static assets (optional)

The storage classes ensure that:
1. Uploaded files have the correct ACL
2. URLs are properly formatted
3. File access is optimized

## Switching Between Local and S3 Storage

To switch between local and S3 storage, simply change the `USE_S3` environment variable:

- For local storage: `export USE_S3=False`
- For S3 storage: `export USE_S3=True`

Restart the application after changing this setting.

## Testing S3 Configuration

To test if your S3 configuration is working:

1. Run the diagnostics: `python diagnose_s3_permissions.py`
2. Upload a test image through the application
3. Verify the image is accessible via its URL