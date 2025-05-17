# Image Upload API Documentation

This document provides information on how to upload images to the Art Critique platform using the API. Our system has been configured to store images in AWS S3 for improved performance, scalability, and reliability.

## Configuration

The application has been configured with the following settings for image uploads:

- Images are stored in AWS S3 using django-storages
- Public-read ACL is used for direct frontend access
- URL signing is disabled for easier access
- Both the API and S3 bucket have CORS configured for cross-origin requests
- All uploads are automatically redirected to S3

## Uploading Images

### Endpoint

`POST /api/artworks/`

### Authentication

Authentication is required for image uploads. Include your authentication token or session cookie in the request.

### Content Type

Use `multipart/form-data` for image uploads.

### Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| title | string | Yes | Title of the artwork |
| description | string | Yes | Description of the artwork |
| image | file | No | Image file to upload |
| image_url | string | No | Legacy parameter: URL to an existing image |
| medium | string | No | Medium used (e.g., "Oil painting", "Digital art") |
| dimensions | string | No | Dimensions of the artwork (e.g., "24x36 inches") |
| tags | string | No | Comma-separated tags |

### Example Request

Using cURL:

```bash
curl -X POST \
  -H "X-CSRFToken: your_csrf_token" \
  -H "Cookie: csrftoken=your_csrf_token; sessionid=your_session_id" \
  -F "title=My Awesome Artwork" \
  -F "description=This is a beautiful landscape painting" \
  -F "medium=Oil on canvas" \
  -F "dimensions=24x36 inches" \
  -F "tags=landscape,nature,mountains" \
  -F "image=@/path/to/your/image.jpg" \
  https://your-domain.com/api/artworks/
```

Using JavaScript Fetch API:

```javascript
const formData = new FormData();
formData.append('title', 'My Awesome Artwork');
formData.append('description', 'This is a beautiful landscape painting');
formData.append('medium', 'Oil on canvas');
formData.append('dimensions', '24x36 inches');
formData.append('tags', 'landscape,nature,mountains');
formData.append('image', imageFile); // imageFile is a File object from a file input

fetch('https://your-domain.com/api/artworks/', {
  method: 'POST',
  headers: {
    'X-CSRFToken': csrfToken, // Get from cookie
  },
  credentials: 'include', // Needed for cookies
  body: formData
})
.then(response => response.json())
.then(data => console.log(data))
.catch(error => console.error('Error:', error));
```

### Response

A successful upload will return a 201 Created response with the artwork data, including the S3 URL of the uploaded image:

```json
{
  "id": 123,
  "title": "My Awesome Artwork",
  "description": "This is a beautiful landscape painting",
  "image": "/path/to/image.jpg",  // S3 relative path
  "image_url": "",
  "image_display_url": "https://your-bucket.s3.amazonaws.com/media/artworks/image.jpg",
  "created_at": "2025-05-15T10:30:00Z",
  "updated_at": "2025-05-15T10:30:00Z",
  "author": {
    "id": 1,
    "username": "artist1",
    "email": "artist1@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "profile": {
      "id": 1,
      "bio": "Professional artist",
      "location": "New York"
    }
  },
  "medium": "Oil on canvas",
  "dimensions": "24x36 inches",
  "tags": "landscape,nature,mountains",
  "likes_count": 0,
  "reviews_count": 0,
  "is_liked": false
}
```

## Displaying Images

To display the uploaded image in your frontend, use the `image_display_url` field from the response. This field provides the complete, directly accessible URL to the image stored in S3.

Example usage in HTML:

```html
<img src="{{ artwork.image_display_url }}" alt="{{ artwork.title }}" />
```

## End-to-End Flow

1. User uploads an image through the API
2. The image is automatically sent to AWS S3
3. The S3 URL is saved in the ArtWork model
4. The API returns the URL in the response
5. The frontend uses this URL to display the image

## Troubleshooting

If you encounter issues with image uploads:

1. Verify your authentication is correct
2. Ensure your form data is properly formatted
3. Check that the image file is valid and not too large
4. Confirm the S3 bucket is properly configured with the correct CORS settings
5. Verify your AWS credentials and permissions

## Notes on S3 Configuration

For optimal performance and security:

- The S3 bucket is configured for public read access for simplicity
- CORS is configured to allow requests from our domain
- We use direct S3 URLs without query parameters for easier caching
- Cache-Control headers are set to improve performance
- The bucket should have a lifecycle policy to manage storage costs