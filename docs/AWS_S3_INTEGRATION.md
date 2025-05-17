# AWS S3 Storage Integration

## Overview

This project now uses AWS S3 for storing media files such as artwork images. This integration provides several benefits:

1. **Scalable Storage**: Amazon S3 provides virtually unlimited storage capacity
2. **Improved Performance**: Content can be served via AWS's global CDN network
3. **Durability and Reliability**: AWS S3 offers 99.999999999% durability
4. **Security**: Fine-grained access controls and encryption options
5. **Cost-Effective**: Pay only for the storage you use

## Implementation Details

### Required Packages

The following packages have been installed to enable S3 integration:

- `django-storages`: Provides storage backends for Django to use various storage providers
- `boto3`: The AWS SDK for Python, required by django-storages to communicate with AWS services
- `pillow`: Required for processing images with ImageField

### Configuration

The integration is configured in `settings.py` with the following settings:

```python
# AWS S3 Configuration
USE_S3 = os.environ.get('USE_S3', 'False') == 'True'

if USE_S3:
    # AWS Settings
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_REGION_NAME = os.environ.get('AWS_S3_REGION_NAME', 'us-east-1')
    AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
    AWS_S3_OBJECT_PARAMETERS = {
        'CacheControl': 'max-age=86400',  # 1 day cache
    }
    
    # S3 Public Media Settings
    PUBLIC_MEDIA_LOCATION = 'media'
    MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{PUBLIC_MEDIA_LOCATION}/'
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    
    # S3 Private Media Settings (optional)
    PRIVATE_MEDIA_LOCATION = 'private'
    PRIVATE_FILE_STORAGE = 'artcritique.storage_backends.PrivateMediaStorage'
```

### Environment Variables

To enable S3 storage, you need to set the following environment variables:

- `USE_S3=True` - Toggle to enable/disable S3 storage
- `AWS_ACCESS_KEY_ID` - Your AWS access key
- `AWS_SECRET_ACCESS_KEY` - Your AWS secret key
- `AWS_STORAGE_BUCKET_NAME` - The name of your S3 bucket
- `AWS_S3_REGION_NAME` - The AWS region of your bucket (default: us-east-1)

### Storage Classes

Custom storage classes are defined in `artcritique/storage_backends.py`:

1. **PublicMediaStorage**: For publicly accessible media files
2. **PrivateMediaStorage**: For private files that require authentication
3. **StaticStorage**: For static files (optional, commented out by default)

### Model Changes

The `ArtWork` model has been updated to use S3 storage:

```python
# Old field (kept for backwards compatibility)
image_url = models.URLField(max_length=1000, blank=True)

# New field using S3 storage
image = models.ImageField(upload_to='artworks/', blank=True, null=True)
```

### Serializer Changes

Serializers have been updated to handle both types of image fields:

1. Added `image_display_url` method field that prioritizes the S3 image URL
2. Modified serializers to expose both fields for backward compatibility
3. Added logic to choose the appropriate image source depending on availability

## Usage

### Uploading Files

When files are uploaded to the `image` field of the `ArtWork` model, they will automatically be saved to the configured S3 bucket in the `artworks/` directory. The URL to the file will be available through the `image.url` attribute.

### Displaying Images

To display images in your templates or API responses, use the `image_display_url` field which will automatically choose the best available image source.

### Backwards Compatibility

The integration maintains compatibility with the old `image_url` field. If a record has data in both fields, the S3 image will be preferred.

## Security Considerations

1. AWS credentials are stored as environment variables, not in code
2. The `USE_S3` toggle makes it easy to disable S3 in development environments
3. Private media files use a custom storage class that doesn't expose public URLs

## Testing S3 Integration

To verify the S3 integration is working:

1. Set the required environment variables
2. Set `USE_S3=True`
3. Upload an image through the admin interface or API
4. Verify the image is being served from the S3 bucket