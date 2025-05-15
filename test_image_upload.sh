#!/bin/bash
# Script to test image uploads to the Art Critique API with AWS S3 storage
# Usage: ./test_image_upload.sh

# Configuration
API_URL="https://localhost:5000"
USERNAME="admin"
PASSWORD="password123"
TEST_IMAGE="test_image.jpg"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}=== Art Critique S3 Upload Test ===${NC}"
echo "This script tests the image upload functionality and S3 integration."

# Check if test image exists
if [ ! -f "$TEST_IMAGE" ]; then
    echo -e "${YELLOW}Test image not found. Creating a sample test image...${NC}"
    echo "This is a test file that would normally be a valid image" > "$TEST_IMAGE"
    echo -e "${GREEN}Created test file: $TEST_IMAGE${NC}"
fi

# Step 1: Get CSRF token
echo -e "\n${YELLOW}Step 1: Getting CSRF token...${NC}"
CSRF_RESPONSE=$(curl -s -k "$API_URL/api/auth/csrf/" -c cookies.txt)
CSRF_TOKEN=$(echo $CSRF_RESPONSE | grep -o '"csrfToken":"[^"]*' | cut -d'"' -f4)

if [ -z "$CSRF_TOKEN" ]; then
    echo -e "${RED}Failed to get CSRF token. API might be down.${NC}"
    exit 1
fi

echo -e "${GREEN}Got CSRF token: $CSRF_TOKEN${NC}"

# Step 2: Login
echo -e "\n${YELLOW}Step 2: Logging in as $USERNAME...${NC}"
LOGIN_RESPONSE=$(curl -s -k -X POST "$API_URL/api/auth/login/" \
    -H "Content-Type: application/json" \
    -H "X-CSRFToken: $CSRF_TOKEN" \
    -H "Referer: $API_URL/" \
    -b cookies.txt -c cookies.txt \
    -d "{\"username\":\"$USERNAME\",\"password\":\"$PASSWORD\"}")

if [[ $LOGIN_RESPONSE == *"error"* ]]; then
    echo -e "${RED}Login failed. Response: $LOGIN_RESPONSE${NC}"
    exit 1
fi

echo -e "${GREEN}Login successful!${NC}"

# Step 3: Upload image
echo -e "\n${YELLOW}Step 3: Uploading test image...${NC}"
echo "Preparing multipart form data with test image and artwork details..."

UPLOAD_RESPONSE=$(curl -s -k -X POST "$API_URL/api/artworks/" \
    -H "X-CSRFToken: $CSRF_TOKEN" \
    -H "Referer: $API_URL/" \
    -b cookies.txt \
    -F "title=S3 Test Artwork" \
    -F "description=Testing S3 image upload functionality" \
    -F "medium=Digital" \
    -F "dimensions=200x200" \
    -F "tags=test,s3,upload" \
    -F "image=@$TEST_IMAGE")

# Check for success
if [[ $UPLOAD_RESPONSE == *"id"* ]]; then
    echo -e "${GREEN}Upload successful!${NC}"
    
    # Extract image URL
    IMAGE_URL=$(echo $UPLOAD_RESPONSE | grep -o '"image_display_url":"[^"]*' | cut -d'"' -f4)
    
    if [ -z "$IMAGE_URL" ]; then
        echo -e "${YELLOW}No image URL found in response.${NC}"
    else
        echo -e "${GREEN}Image URL: $IMAGE_URL${NC}"
        
        # Check if it's an S3 URL
        if [[ $IMAGE_URL == *"s3.amazonaws.com"* ]]; then
            echo -e "${GREEN}✓ Confirmed: Image is stored in S3${NC}"
        else
            echo -e "${YELLOW}Image is not stored in S3. This is expected if USE_S3=False${NC}"
            echo "Current URL format indicates local storage."
        fi
    fi
    
    echo -e "\n${YELLOW}Response Details:${NC}"
    echo "$UPLOAD_RESPONSE" | python3 -m json.tool || echo "$UPLOAD_RESPONSE"
else
    echo -e "${RED}Upload failed. Response:${NC}"
    echo "$UPLOAD_RESPONSE"
    exit 1
fi

echo -e "\n${GREEN}=== Test Complete ===${NC}"
echo -e "${YELLOW}Note:${NC} If USE_S3=False, images are stored locally instead of S3."
echo "To enable S3 storage, set the following environment variables:"
echo "  USE_S3=True"
echo "  AWS_ACCESS_KEY_ID=your_access_key"
echo "  AWS_SECRET_ACCESS_KEY=your_secret_key"
echo "  AWS_STORAGE_BUCKET_NAME=your_bucket_name"
echo "  AWS_S3_REGION_NAME=your_region"