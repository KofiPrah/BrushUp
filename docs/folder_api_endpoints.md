# Folder API Endpoints Documentation

## Overview
The FolderViewSet provides comprehensive REST API endpoints for portfolio management, allowing artists to organize their artworks into themed collections.

## Base URL
All folder endpoints are available at: `/api/folders/`

## Authentication
- Most endpoints require authentication
- Only folder owners can modify their folders
- Public folders are viewable by everyone

## Available Endpoints

### 1. List Folders
**GET /api/folders/**
- Lists folders based on user permissions
- Authenticated users see their own + public folders
- Anonymous users see only public folders
- Supports search, filtering, and ordering

**Query Parameters:**
- `search`: Search in folder name and description
- `ordering`: Sort by `created_at`, `updated_at`, `name` (prefix with `-` for descending)

**Response:**
```json
{
  "count": 25,
  "next": "http://example.com/api/folders/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Landscape Series",
      "description": "My collection of landscape paintings",
      "owner_username": "artist123",
      "is_public": "public",
      "created_at": "2024-01-15T10:30:00Z",
      "slug": "landscape-series",
      "artwork_count": 12,
      "cover_image_url": "https://s3.amazonaws.com/..."
    }
  ]
}
```

### 2. Create Folder
**POST /api/folders/**
- Requires authentication
- Creates a new portfolio folder for the current user

**Request Body:**
```json
{
  "name": "Abstract Works",
  "description": "My experimental abstract paintings",
  "is_public": "public",
  "cover_image": null
}
```

**Response:** 201 Created with folder details

### 3. Get Folder Details
**GET /api/folders/{id}/**
- Returns detailed folder information
- Respects privacy settings

**Response:**
```json
{
  "id": 1,
  "name": "Landscape Series",
  "description": "My collection of landscape paintings",
  "owner": 5,
  "owner_username": "artist123",
  "is_public": "public",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-20T14:22:00Z",
  "cover_image": "https://s3.amazonaws.com/...",
  "cover_image_url": "https://s3.amazonaws.com/...",
  "slug": "landscape-series",
  "artwork_count": 12,
  "can_edit": true,
  "can_delete": true,
  "url": "/profile/artist123/folder/landscape-series/"
}
```

### 4. Update Folder
**PUT/PATCH /api/folders/{id}/**
- Requires authentication and ownership
- Updates folder information

**Request Body:**
```json
{
  "name": "Updated Landscapes",
  "description": "Updated description",
  "is_public": "private"
}
```

### 5. Delete Folder
**DELETE /api/folders/{id}/**
- Requires authentication and ownership
- Artworks in folder are not deleted, just unassigned

### 6. Get Folder Artworks
**GET /api/folders/{id}/artworks/**
- Lists all artworks in the specified folder
- Respects folder privacy settings

**Response:**
```json
{
  "folder": {
    "id": 1,
    "name": "Landscape Series",
    "slug": "landscape-series"
  },
  "artworks": [
    {
      "id": 10,
      "title": "Mountain Vista",
      "description": "Digital landscape painting",
      "image_url": "https://s3.amazonaws.com/...",
      "created_at": "2024-01-16T09:15:00Z",
      "author_name": "artist123"
    }
  ],
  "count": 12
}
```

### 7. Add Artwork to Folder
**POST /api/folders/{id}/add_artwork/**
- Requires authentication and folder ownership
- Adds an artwork (that you own) to the folder

**Request Body:**
```json
{
  "artwork_id": 25
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Artwork 'Mountain Vista' added to folder 'Landscape Series'"
}
```

### 8. Remove Artwork from Folder
**POST /api/folders/{id}/remove_artwork/**
- Requires authentication and folder ownership
- Removes artwork from folder (artwork not deleted)

**Request Body:**
```json
{
  "artwork_id": 25
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Artwork 'Mountain Vista' removed from folder 'Landscape Series'"
}
```

### 9. Get My Folders
**GET /api/folders/my_folders/**
- Requires authentication
- Returns all folders belonging to the current user

**Response:**
```json
{
  "folders": [
    {
      "id": 1,
      "name": "Landscape Series",
      "description": "My landscape collection",
      "owner_username": "artist123",
      "is_public": "public",
      "created_at": "2024-01-15T10:30:00Z",
      "slug": "landscape-series",
      "artwork_count": 12,
      "cover_image_url": "https://s3.amazonaws.com/..."
    }
  ],
  "count": 3
}
```

## Error Responses

### 403 Forbidden
```json
{
  "error": "Only the folder owner can add artworks"
}
```

### 404 Not Found
```json
{
  "error": "Artwork not found or you don't own it"
}
```

### 400 Bad Request
```json
{
  "error": "artwork_id is required"
}
```

## Security Features

1. **Ownership Validation**: Only folder owners can modify their folders
2. **Privacy Respect**: Visibility settings strictly enforced
3. **Artwork Ownership**: Can only add/remove your own artworks
4. **Permission Checking**: Comprehensive permission validation

## Integration Examples

### Creating a Portfolio Workflow
```javascript
// 1. Create folder
const folder = await fetch('/api/folders/', {
  method: 'POST',
  headers: { 'Authorization': 'Bearer token', 'Content-Type': 'application/json' },
  body: JSON.stringify({
    name: 'My Best Works',
    description: 'Curated collection of my finest pieces',
    is_public: 'public'
  })
});

// 2. Add artworks to folder
await fetch(`/api/folders/${folder.id}/add_artwork/`, {
  method: 'POST',
  headers: { 'Authorization': 'Bearer token', 'Content-Type': 'application/json' },
  body: JSON.stringify({ artwork_id: 123 })
});
```

This comprehensive API enables full portfolio management functionality for artists on your platform!