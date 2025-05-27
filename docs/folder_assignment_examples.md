# Artwork-to-Folder Assignment Examples

## Overview
This document demonstrates how to assign artworks to folders using the enhanced API endpoints with proper validation.

## API Usage Examples

### 1. Create Artwork with Folder Assignment
```bash
# Create artwork and assign to folder in one request
curl -X POST "https://your-domain/api/artworks/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Mountain Landscape",
    "description": "A beautiful mountain vista",
    "medium": "Digital Painting",
    "tags": "landscape, mountains, nature",
    "folder": 5
  }'
```

**Response:**
```json
{
  "id": 25,
  "title": "Mountain Landscape",
  "description": "A beautiful mountain vista",
  "medium": "Digital Painting",
  "tags": "landscape, mountains, nature",
  "folder": 5,
  "folder_name": "Landscape Series",
  "folder_slug": "landscape-series",
  "author": {
    "id": 10,
    "username": "artist123"
  },
  "created_at": "2024-01-20T14:30:00Z"
}
```

### 2. Update Artwork to Assign to Different Folder
```bash
# Move artwork to a different folder
curl -X PATCH "https://your-domain/api/artworks/25/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "folder": 8
  }'
```

### 3. Remove Artwork from Folder
```bash
# Remove artwork from folder (set to null)
curl -X PATCH "https://your-domain/api/artworks/25/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "folder": null
  }'
```

### 4. Get Folder Details with Nested Artworks
```bash
# Retrieve folder with all its artworks
curl -X GET "https://your-domain/api/folders/5/" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
{
  "id": 5,
  "name": "Landscape Series",
  "description": "My collection of landscape paintings",
  "owner": 10,
  "owner_username": "artist123",
  "is_public": "public",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-20T14:30:00Z",
  "cover_image_url": "https://s3.amazonaws.com/...",
  "slug": "landscape-series",
  "artwork_count": 3,
  "can_edit": true,
  "can_delete": true,
  "url": "/profile/artist123/folder/landscape-series/",
  "artworks": [
    {
      "id": 25,
      "title": "Mountain Landscape",
      "image_display_url": "https://s3.amazonaws.com/...",
      "author_name": "artist123",
      "created_at": "2024-01-20T14:30:00Z",
      "medium": "Digital Painting",
      "likes_count": 12,
      "tags_list": ["landscape", "mountains", "nature"]
    },
    {
      "id": 23,
      "title": "Sunset Valley",
      "image_display_url": "https://s3.amazonaws.com/...",
      "author_name": "artist123",
      "created_at": "2024-01-18T09:15:00Z",
      "medium": "Oil Painting",
      "likes_count": 8,
      "tags_list": ["landscape", "sunset", "valley"]
    }
  ]
}
```

## Validation Examples

### ✅ Valid Operations
```javascript
// User can assign their artwork to their own folder
{
  "artwork_author": "user123",
  "folder_owner": "user123",
  "result": "✅ SUCCESS"
}
```

### ❌ Invalid Operations with Error Messages

#### 1. Assigning to Someone Else's Folder
```bash
curl -X POST "https://your-domain/api/artworks/" \
  -H "Authorization: Bearer USER_A_TOKEN" \
  -d '{"title": "My Art", "folder": 99}'  # Folder owned by User B
```

**Error Response:**
```json
{
  "folder": ["You can only assign artworks to your own folders."]
}
```

#### 2. Updating Someone Else's Artwork
```bash
curl -X PATCH "https://your-domain/api/artworks/999/" \
  -H "Authorization: Bearer USER_A_TOKEN" \
  -d '{"folder": 5}'  # Artwork owned by User B
```

**Error Response:**
```json
{
  "non_field_errors": ["You can only modify your own artworks."]
}
```

## JavaScript Frontend Integration

### Create Artwork with Folder Assignment
```javascript
async function createArtworkInFolder(artworkData, folderId) {
  try {
    const response = await fetch('/api/artworks/', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        ...artworkData,
        folder: folderId
      })
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.folder?.[0] || 'Failed to create artwork');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error creating artwork:', error.message);
    throw error;
  }
}
```

### Move Artwork Between Folders
```javascript
async function moveArtworkToFolder(artworkId, newFolderId) {
  try {
    const response = await fetch(`/api/artworks/${artworkId}/`, {
      method: 'PATCH',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        folder: newFolderId
      })
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.folder?.[0] || 'Failed to move artwork');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error moving artwork:', error.message);
    throw error;
  }
}
```

### Get Folder with All Artworks
```javascript
async function getFolderWithArtworks(folderId) {
  try {
    const response = await fetch(`/api/folders/${folderId}/`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    
    if (!response.ok) {
      throw new Error('Failed to fetch folder');
    }
    
    const folder = await response.json();
    console.log(`Folder "${folder.name}" contains ${folder.artwork_count} artworks`);
    
    return folder;
  } catch (error) {
    console.error('Error fetching folder:', error.message);
    throw error;
  }
}
```

## Security Features

1. **Ownership Validation**: Users can only assign their artworks to their own folders
2. **Update Protection**: Users can only modify their own artworks
3. **Folder Privacy**: Folder visibility settings are respected in all operations
4. **Permission Checking**: All operations verify user permissions before execution

## Common Use Cases

### Portfolio Organization
```javascript
// 1. Create themed folders
const portraitFolder = await createFolder({
  name: "Portrait Collection",
  description: "My best portrait work",
  is_public: "public"
});

// 2. Create artworks directly in folders
const artwork1 = await createArtworkInFolder({
  title: "Self Portrait",
  medium: "Oil Paint"
}, portraitFolder.id);

// 3. Move existing artworks to folders
await moveArtworkToFolder(existingArtworkId, portraitFolder.id);
```

### Bulk Operations
```javascript
// Move multiple artworks to a folder
const artworkIds = [101, 102, 103];
const results = await Promise.all(
  artworkIds.map(id => moveArtworkToFolder(id, targetFolderId))
);
```

This comprehensive system provides secure, validated artwork-to-folder assignment with full API support!