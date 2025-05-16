# Setting Up AWS S3 Storage

This guide provides step-by-step instructions on how to set up AWS S3 storage for the Art Critique application.

## Prerequisites

1. An AWS account
2. S3 bucket created in your AWS account
3. IAM user with appropriate S3 permissions

## Step 1: Create an S3 Bucket

1. Log in to the AWS Management Console
2. Navigate to S3 service
3. Click "Create bucket"
4. Name your bucket (e.g., "art-critique-media")
5. Select a region close to your users
6. Configure options:
   - Enable versioning (recommended for production)
   - Set appropriate public access settings
   - Enable server-side encryption if needed
7. Click "Create bucket"

## Step 2: Create an IAM User with S3 Access

1. Navigate to IAM service
2. Click "Users" and then "Add user"
3. Provide a username (e.g., "art-critique-s3-user")
4. Select "Programmatic access" for access type
5. Click "Next: Permissions"
6. Choose "Attach existing policies directly"
7. Search for and select "AmazonS3FullAccess" (or create a custom policy with limited permissions)
8. Complete the user creation process
9. **Save the Access Key ID and Secret Access Key** - you'll need these for the application

## Step 3: Configure CORS for the S3 Bucket

1. Navigate to your S3 bucket
2. Click the "Permissions" tab
3. Find and click "CORS configuration"
4. Add a CORS configuration like:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<CORSConfiguration xmlns="http://s3.amazonaws.com/doc/2006-03-01/">
    <CORSRule>
        <AllowedOrigin>*</AllowedOrigin>
        <AllowedMethod>GET</AllowedMethod>
        <AllowedMethod>POST</AllowedMethod>
        <AllowedMethod>PUT</AllowedMethod>
        <MaxAgeSeconds>3000</MaxAgeSeconds>
        <AllowedHeader>*</AllowedHeader>
    </CORSRule>
</CORSConfiguration>
```

For production, replace `*` with your actual domain.

## Step 4: Configure Environment Variables

Set the following environment variables in your deployment environment:

```
USE_S3=True
AWS_ACCESS_KEY_ID=your_access_key_id
AWS_SECRET_ACCESS_KEY=your_secret_access_key
AWS_STORAGE_BUCKET_NAME=your_bucket_name
AWS_S3_REGION_NAME=your_bucket_region
```

For local development, you can create a `.env` file with these variables.

## Step 5: Test the Configuration

1. Restart your Django application
2. Try uploading a file through the admin interface or API
3. Verify the file is stored in your S3 bucket
4. Check that the file can be accessed via its URL

## Troubleshooting

### Common Issues:

1. **Access Denied Errors**:
   - Check your IAM permissions
   - Verify bucket policy and public access settings
   - Ensure the access keys are correct

2. **CORS Issues**:
   - Verify your CORS configuration is properly set
   - Check the request headers in the browser console

3. **Bucket Not Found**:
   - Double-check the bucket name and region
   - Ensure the bucket exists in the specified region

4. **Missing Files**:
   - Check the `upload_to` path in your models
   - Look for the file in the S3 console

## Security Best Practices

1. Use IAM roles for EC2/ECS instead of access keys when possible
2. Create a custom IAM policy with the minimum required permissions
3. Set a restrictive bucket policy
4. Enable S3 bucket versioning and logging
5. Consider using server-side encryption for sensitive data
6. Regularly rotate your AWS access keys