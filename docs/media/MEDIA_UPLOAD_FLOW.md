# Media Upload Flow with AWS S3

This document explains the end-to-end flow of media uploads in the Art Critique application, particularly focusing on how images are stored in AWS S3 and accessed by the frontend.

## Configuration Overview

The application is configured to seamlessly handle image uploads and store them in AWS S3:

1. The Django application uses django-storages with boto3 to interact with AWS S3
2. Images are stored with public-read access for direct frontend access
3. URL signing is disabled to provide clean, cacheable URLs
4. Both the API and S3 bucket are configured with appropriate CORS settings
5. The system maintains backward compatibility with the legacy URL-based storage

## End-to-End Flow

### 1. User Submits Artwork with Image

The user submits a new artwork through the API, including an image file:

```http
POST /api/artworks/
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW

------WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="title"

Mountain Landscape
------WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="description"

A beautiful mountain landscape painting
------WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="medium"

Oil on canvas
------WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="dimensions"

24x36 inches
------WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="tags"

landscape,mountains,nature
------WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="image"; filename="mountain_landscape.jpg"
Content-Type: image/jpeg

[Binary image data]
------WebKitFormBoundary7MA4YWxkTrZu0gW--
```

### 2. Django API Processes the Upload

When the API receives the request:

1. The MultiPartParser processes the form data and file
2. The ArtWorkSerializer validates the data
3. Django's ImageField handles the file upload
4. The create method sets the authenticated user as the author

```python
# In ArtWorkSerializer
def create(self, validated_data):
    """Create a new artwork with the current user as author."""
    user = self.context['request'].user
    artwork = ArtWork.objects.create(author=user, **validated_data)
    return artwork
```

### 3. Django-Storages Routes the File to S3

The django-storages library, configured as the default storage backend, automatically:

1. Generates a unique key for the file based on the upload_to path ('artworks/')
2. Uploads the file to the configured S3 bucket
3. Sets the appropriate content type and access control
4. Stores the relative path in the model's ImageField

The S3 storage configuration in settings.py enables this behavior:

```python
# When USE_S3 is True
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
AWS_DEFAULT_ACL = 'public-read'
AWS_QUERYSTRING_AUTH = False
```

### 4. API Returns the S3 URL

The API response includes the uploaded image's URL:

```json
{
  "id": 123,
  "title": "Mountain Landscape",
  "description": "A beautiful mountain landscape painting",
  "image": "artworks/mountain_landscape.jpg",
  "image_url": "",
  "image_display_url": "https://your-bucket.s3.amazonaws.com/media/artworks/mountain_landscape.jpg",
  "created_at": "2025-05-15T12:30:45Z",
  "updated_at": "2025-05-15T12:30:45Z",
  "author": {
    "id": 1,
    "username": "artist1",
    "email": "artist1@example.com",
    "first_name": "John",
    "last_name": "Doe"
  },
  "medium": "Oil on canvas",
  "dimensions": "24x36 inches",
  "tags": "landscape,mountains,nature",
  "likes_count": 0,
  "reviews_count": 0,
  "is_liked": false
}
```

The `image_display_url` field provides the full URL to the image in S3, which is the key for frontend access.

### 5. Frontend Displays the Image

The frontend can directly use the `image_display_url` to display the image:

```html
<img src="https://your-bucket.s3.amazonaws.com/media/artworks/mountain_landscape.jpg" 
     alt="Mountain Landscape" 
     class="artwork-image" />
```

Because the image is stored with public-read access, no additional authentication is required to view it.

## Verification

To verify that uploads are working correctly:

1. **Check Storage Backend**: Confirm `DEFAULT_FILE_STORAGE` is set to S3Boto3Storage when `USE_S3=True`
2. **Test Upload Flow**: Upload an image through the API and check that it's stored in S3
3. **Verify URL Format**: Ensure the returned URL points to the S3 bucket and is accessible
4. **Check Public Access**: Verify the image can be accessed directly without authentication

## Common Issues and Solutions

1. **CORS Errors**:
   - Ensure the S3 bucket has proper CORS configuration
   - Example CORS settings for the S3 bucket:
     ```xml
     <CORSConfiguration>
       <CORSRule>
         <AllowedOrigin>*</AllowedOrigin>
         <AllowedMethod>GET</AllowedMethod>
         <MaxAgeSeconds>3000</MaxAgeSeconds>
         <AllowedHeader>*</AllowedHeader>
       </CORSRule>
     </CORSConfiguration>
     ```

2. **Access Denied Errors**:
   - Verify AWS_DEFAULT_ACL is set to 'public-read'
   - Check bucket policy allows public read access
   - Confirm AWS credentials have appropriate permissions

3. **URL Generation Issues**:
   - If URLs have complex query strings, check AWS_QUERYSTRING_AUTH setting
   - For clean URLs, set AWS_QUERYSTRING_AUTH = False

## Local Development vs. Production

For development without AWS credentials:

1. The system detects that S3 is not available (USE_S3=False)
2. Image uploads are automatically stored locally in the MEDIA_ROOT directory
3. URLs reference the local media path

In production with AWS credentials:

1. Set the required environment variables:
   ```
   USE_S3=True
   AWS_ACCESS_KEY_ID=your_access_key
   AWS_SECRET_ACCESS_KEY=your_secret_key
   AWS_STORAGE_BUCKET_NAME=your_bucket_name
   AWS_S3_REGION_NAME=your_region
   ```
2. Image uploads are automatically stored in S3
3. URLs reference the S3 paths

## Conclusion

This implementation ensures that:

1. Image uploads are seamlessly handled through the API
2. Files are stored in S3 when properly configured
3. URLs returned by the API point directly to accessible images
4. The frontend can display images without additional authentication
5. The system works gracefully in both development and production environments