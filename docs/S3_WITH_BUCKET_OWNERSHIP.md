# S3 Configuration with Bucket Ownership Enforced

This document explains how to configure AWS S3 storage for Art Critique when bucket ownership is enforced.

## Background

AWS S3 offers several different ownership settings for buckets:

1. **Bucket Owner Preferred (Default)**: The bucket owner owns objects if they are uploaded with the `bucket-owner-full-control` canned ACL.
2. **Object Writer (Legacy)**: The object writer owns the objects they upload.
3. **Bucket Owner Enforced**: The bucket owner automatically owns and has full control over every object, regardless of who uploads it. ACLs are disabled.

Art Critique has been configured to work with Bucket Owner Enforced settings, which is the most secure option.

## Storage Configuration

The application's storage backends are configured to work with bucket ownership enforced:

- **StaticStorage**: Used for static files like CSS, JavaScript, etc.
- **PublicMediaStorage**: Used for public media files like artwork images.
- **PrivateMediaStorage**: Used for private media files.

### Key Storage Features

- No ACLs are used (since they're disabled with bucket ownership enforced)
- Bucket policies are used to control access to objects
- `ObjectOwnership` is set to `BucketOwnerEnforced` 
- Authentication query parameters are used for private files

## Bucket Policy Example

To make objects in the media folder publicly accessible, use a bucket policy like this:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadForMediaObjects",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::your-bucket-name/media/*"
        }
    ]
}
```

## Troubleshooting

### Common Issues

1. **Objects are not publicly accessible**: Check that the bucket policy includes a rule to allow public read access to objects in the media folder.

2. **Operation not allowed for bucket with ownership controls**: This error occurs if you're trying to set ACLs on objects in a bucket with ownership enforced. The application has been modified to not use ACLs.

3. **Access Denied**: If you see access denied errors, ensure that:
   - The bucket policy is correctly configured
   - The IAM user/role has permission to the bucket
   - The object path matches the pattern in the bucket policy

### Verification

You can verify your S3 configuration with:

```python
python scripts/test_s3_connection.py
```

This script will test basic read/write operations with your S3 bucket.