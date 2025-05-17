"""
S3 Browser and Tester for Art Critique
Creates a simple HTML page to browse and test S3 images
"""
import os
import boto3
import json
import datetime
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'artcritique.settings')
django.setup()

from django.conf import settings

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")

def list_bucket_contents():
    """List all objects in the S3 bucket"""
    try:
        # Initialize boto3 client
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME
        )
        
        bucket_name = settings.AWS_STORAGE_BUCKET_NAME
        
        # List all objects in the bucket
        all_objects = []
        continuation_token = None
        
        while True:
            # Prepare list_objects_v2 parameters
            params = {
                'Bucket': bucket_name,
                'MaxKeys': 1000
            }
            
            if continuation_token:
                params['ContinuationToken'] = continuation_token
                
            # Get batch of objects
            response = s3_client.list_objects_v2(**params)
            
            # Process objects in this batch
            if 'Contents' in response:
                for obj in response['Contents']:
                    # Generate presigned URL for testing
                    presigned_url = s3_client.generate_presigned_url(
                        'get_object',
                        Params={
                            'Bucket': bucket_name,
                            'Key': obj['Key']
                        },
                        ExpiresIn=3600  # URL valid for 1 hour
                    )
                    
                    # Add presigned URL to object info
                    obj['PresignedUrl'] = presigned_url
                    
                    # Add direct S3 URL
                    obj['DirectUrl'] = f"https://{settings.AWS_S3_CUSTOM_DOMAIN}/{obj['Key']}"
                    
                    # Add to our list
                    all_objects.append(obj)
            
            # Check if there are more objects to fetch
            if not response.get('IsTruncated'):
                break
                
            continuation_token = response.get('NextContinuationToken')
        
        return all_objects
            
    except Exception as e:
        print(f"Error listing bucket contents: {e}")
        return []

def create_html_page(objects):
    """Create an HTML page to view and test S3 objects"""
    html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Art Critique S3 Browser</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { padding: 20px; background-color: #f8f9fa; }
        .image-container { margin-bottom: 30px; background: white; padding: 15px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        .image-preview { max-width: 300px; max-height: 200px; object-fit: contain; margin-bottom: 10px; }
        .url-box { background: #f0f0f0; padding: 8px; border-radius: 4px; margin-bottom: 5px; word-break: break-all; }
        h1 { margin-bottom: 20px; }
        .status { font-weight: bold; }
        .success { color: green; }
        .error { color: red; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Art Critique S3 Browser</h1>
        <p>This page helps you verify S3 image access. For each image, there are two URLs: a direct S3 URL and a pre-signed URL.</p>
        <div class="alert alert-info">
            <strong>Bucket:</strong> """ + settings.AWS_STORAGE_BUCKET_NAME + """<br>
            <strong>Region:</strong> """ + settings.AWS_S3_REGION_NAME + """<br>
            <strong>S3 Domain:</strong> """ + settings.AWS_S3_CUSTOM_DOMAIN + """<br>
            <strong>Total Files:</strong> """ + str(len(objects)) + """
        </div>
        
        <div id="imageContainer">
            <!-- Images will be inserted here by JavaScript -->
        </div>
    </div>
    
    <script>
        // Image objects from S3
        const s3Objects = """ + json.dumps(objects, default=json_serial) + """;
        
        // Get the container
        const container = document.getElementById('imageContainer');
        
        // Function to test if URL is accessible
        async function testImageUrl(url) {
            try {
                const response = await fetch(url, { method: 'HEAD' });
                return {
                    success: response.ok,
                    status: response.status,
                    statusText: response.statusText
                };
            } catch (error) {
                return {
                    success: false,
                    status: 'Error',
                    statusText: error.message
                };
            }
        }
        
        // Function to create an image card
        async function createImageCard(obj) {
            // Only process images
            const imageExtensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'];
            const isImage = imageExtensions.some(ext => obj.Key.toLowerCase().endsWith(ext));
            
            const card = document.createElement('div');
            card.className = 'image-container';
            
            const header = document.createElement('h4');
            header.textContent = obj.Key;
            card.appendChild(header);
            
            const size = document.createElement('p');
            size.textContent = `Size: ${(obj.Size / 1024).toFixed(2)} KB`;
            card.appendChild(size);
            
            // Direct URL section
            const directUrlTitle = document.createElement('h5');
            directUrlTitle.textContent = 'Direct S3 URL:';
            card.appendChild(directUrlTitle);
            
            const directUrlBox = document.createElement('div');
            directUrlBox.className = 'url-box';
            directUrlBox.textContent = obj.DirectUrl;
            card.appendChild(directUrlBox);
            
            // Test direct URL
            const directStatus = document.createElement('p');
            directStatus.textContent = 'Testing direct URL...';
            directStatus.className = 'status';
            card.appendChild(directStatus);
            
            // Only add image preview for image files
            if (isImage) {
                // Presigned URL section
                const presignedUrlTitle = document.createElement('h5');
                presignedUrlTitle.textContent = 'Pre-signed URL (valid for 1 hour):';
                card.appendChild(presignedUrlTitle);
                
                const presignedUrlBox = document.createElement('div');
                presignedUrlBox.className = 'url-box';
                presignedUrlBox.textContent = obj.PresignedUrl;
                card.appendChild(presignedUrlBox);
                
                // Test presigned URL and add image if successful
                const presignedStatus = document.createElement('p');
                presignedStatus.textContent = 'Testing pre-signed URL...';
                presignedStatus.className = 'status';
                card.appendChild(presignedStatus);
                
                // Image preview with presigned URL
                const imgTitle = document.createElement('h5');
                imgTitle.textContent = 'Image Preview (using pre-signed URL):';
                card.appendChild(imgTitle);
                
                const img = document.createElement('img');
                img.className = 'image-preview';
                img.alt = obj.Key;
                img.src = obj.PresignedUrl;
                card.appendChild(img);
            }
            
            // Add card to container
            container.appendChild(card);
            
            // Test direct URL
            const directResult = await testImageUrl(obj.DirectUrl);
            if (directResult.success) {
                directStatus.textContent = `✅ Direct URL works! (${directResult.status} ${directResult.statusText})`;
                directStatus.classList.add('success');
            } else {
                directStatus.textContent = `❌ Direct URL error: ${directResult.status} ${directResult.statusText}`;
                directStatus.classList.add('error');
            }
            
            // Test presigned URL for images
            if (isImage) {
                const presignedStatus = card.querySelector('p.status:nth-of-type(2)');
                const presignedResult = await testImageUrl(obj.PresignedUrl);
                if (presignedResult.success) {
                    presignedStatus.textContent = `✅ Pre-signed URL works! (${presignedResult.status} ${presignedResult.statusText})`;
                    presignedStatus.classList.add('success');
                } else {
                    presignedStatus.textContent = `❌ Pre-signed URL error: ${presignedResult.status} ${presignedResult.statusText}`;
                    presignedStatus.classList.add('error');
                }
            }
        }
        
        // Process all objects
        async function processObjects() {
            // Sort by newest first
            s3Objects.sort((a, b) => new Date(b.LastModified) - new Date(a.LastModified));
            
            // Process each object
            for (const obj of s3Objects) {
                await createImageCard(obj);
            }
        }
        
        // Start processing
        processObjects();
    </script>
</body>
</html>
    """
    
    # Save the HTML file
    with open('s3_browser.html', 'w') as f:
        f.write(html)
    
    print(f"Created S3 browser page: s3_browser.html")
    print(f"Open this file in your browser to view your S3 bucket contents")
    
def main():
    print("Creating S3 Browser for Art Critique")
    print("-" * 60)
    
    # Check if S3 is enabled
    if not settings.USE_S3:
        print("❌ S3 storage is not enabled (USE_S3 is False)")
        return
    
    # List bucket contents
    print("Fetching objects from S3 bucket...")
    objects = list_bucket_contents()
    
    if not objects:
        print("No objects found in the bucket or error occurred")
        return
    
    print(f"Found {len(objects)} objects in the bucket")
    
    # Create HTML page
    create_html_page(objects)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()