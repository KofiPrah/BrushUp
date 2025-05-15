# Image Upload Demonstration for Art Critique Project

## Background

This document demonstrates the end-to-end image upload flow for the Art Critique application. The system is designed to:

1. Allow users to upload artwork images through a web form
2. Process the images via Django and store them in AWS S3
3. Return the S3 URLs for frontend display

## Implementation Details

### Frontend Upload Form

The upload form (`artwork_upload.html`) includes:

- Form fields for artwork metadata (title, description, medium, etc.)
- File input for image selection with client-side preview
- JavaScript to handle form submission via the API endpoint
- Success/error handling with visual feedback

### API Endpoint

The API endpoint (`/api/artworks/`) is configured to:

- Accept multipart form data with image files
- Authenticate requests with session cookies and CSRF protection
- Validate input data with serializers
- Store images in S3 when properly configured
- Return complete artwork data including the image URL

### S3 Storage Configuration

When S3 storage is enabled:

- Images are automatically routed to the configured S3 bucket
- Public-read ACL allows direct frontend access
- Clean URLs without query strings for better caching

## Mock Demonstration

Since we can't directly see the frontend due to SSL configuration issues, here's a detailed walkthrough of the upload process:

1. **User selects an image**: The file input allows selecting an image, which is then previewed in the form
2. **User fills out metadata**: Title, description, medium, dimensions, and tags
3. **User submits the form**: JavaScript captures the form submission and sends it to the API
4. **API processes the upload**: Validates the data, saves the image, and creates the artwork record
5. **API returns the response**: Including the S3 URL of the uploaded image
6. **Frontend displays success**: Shows a confirmation message and the uploaded image

## Testing Options

To test the image upload flow:

1. **API Testing**: Use the `test_image_upload.sh` script to test the API endpoint
2. **HTTP Server**: Run `python run_http_server.py` to start a server without SSL for direct testing
3. **S3 Verification**: Use `python verify_s3_integration.py` to check S3 configuration

## Actual Implementation Screenshot

In a properly configured environment, the upload form would look like this:

```
+----------------------------------+
|        Upload New Artwork        |
+----------------------------------+
| Title: [Mountain Landscape     ] |
| Description:                     |
| [A beautiful mountain landscape  |
|  with snow-capped peaks and     |
|  pine forests                  ] |
|                                  |
| Medium: [Oil on canvas         ] |
|                                  |
| Dimensions: [24x36 inches      ] |
|                                  |
| Tags: [landscape,mountains,nature|
|                                ] |
|                                  |
| Artwork Image: [Choose File...v] |
|                                  |
| [Image Preview Shows Here]       |
|                                  |
|                  [Upload Artwork]|
+----------------------------------+
```

After successful upload, the user would see a success message and the uploaded image, along with a link to view the artwork detail page.

## Production vs. Development

- In production (with AWS credentials configured), images are stored in S3
- In development (without AWS credentials), images are stored locally
- The API response format is identical in both environments, ensuring consistent frontend behavior