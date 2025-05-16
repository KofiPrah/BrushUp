# Art Critique API Documentation

This document outlines the available endpoints in the Art Critique API, their purpose, and usage examples.

## Base URL

All API endpoints are prefixed with `/api/`.

## Authentication

Most endpoints that modify data require authentication. The API uses token-based authentication via Django REST Framework.

## Artworks

### List Artworks

**Endpoint**: `GET /api/artworks/`

Returns a paginated list of all artworks, ordered by creation date (newest first).

**Response Example**:
```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 2,
      "title": "Urban Nightscape",
      "image": "",
      "author_name": "username",
      "created_at": "2025-05-15T04:55:54.709651Z"
    },
    {
      "id": 1,
      "title": "Sunset over the Mountains",
      "image": "",
      "author_name": "testuser",
      "created_at": "2025-05-15T04:55:54.669988Z"
    }
  ]
}
```

### Get Artwork Details

**Endpoint**: `GET /api/artworks/{id}/`

Returns detailed information about a specific artwork.

**Response Example**:
```json
{
  "id": 1,
  "title": "Sunset over the Mountains",
  "description": "A vibrant oil painting depicting a sunset over a mountain range.",
  "image": "",
  "created_at": "2025-05-15T04:55:54.669988Z",
  "updated_at": "2025-05-15T05:16:57.743740Z",
  "author": {
    "id": 2,
    "username": "testuser",
    "email": "test@example.com",
    "first_name": "",
    "last_name": "",
    "profile": null,
    "is_staff": false,
    "date_joined": "2025-05-15T04:55:53.335671Z",
    "last_login": null
  },
  "medium": "",
  "dimensions": "",
  "tags": "landscape,mountains,sunset"
}
```

### Create Artwork

**Endpoint**: `POST /api/artworks/`

Creates a new artwork. Requires authentication.

**Request Body**:
```json
{
  "title": "New Artwork",
  "description": "A description of the artwork",
  "image": "https://example.com/image.jpg",
  "medium": "Oil on canvas",
  "dimensions": "24x36 inches",
  "tags": "landscape,portrait,abstract"
}
```

**Response**: Returns the created artwork with status 201.

### Update Artwork

**Endpoint**: `PUT /api/artworks/{id}/`

Updates an existing artwork. Requires authentication and user must be the author of the artwork or an admin.

**Request Body**: Same as create, with updated fields.

**Response**: Returns the updated artwork.

### Delete Artwork

**Endpoint**: `DELETE /api/artworks/{id}/`

Deletes an existing artwork. Requires authentication and user must be the author of the artwork or an admin.

**Response**: Status 204 No Content on success.

### Like/Unlike Artwork

**Endpoint**: `POST /api/artworks/{id}/like/`

Toggles the like status for the current user on an artwork. Requires authentication.

**Response Example**:
```json
{
  "status": "liked"
}
```
or
```json
{
  "status": "unliked"
}
```

### Get Artwork Reviews

**Endpoint**: `GET /api/artworks/{id}/reviews/`

Returns all reviews for a specific artwork.

**Response Example**:
```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "artwork": 1,
      "reviewer": {
        "id": 2,
        "username": "testuser",
        "email": "test@example.com",
        "first_name": "",
        "last_name": "",
        "profile": null,
        "is_staff": false,
        "date_joined": "2025-05-15T04:55:53.335671Z",
        "last_login": null
      },
      "content": "The use of color in this piece is exceptional, creating a warm and inviting atmosphere.",
      "rating": 5,
      "created_at": "2025-05-15T04:55:54.747578Z"
    }
  ]
}
```

### Filter Artworks by Tag

**Endpoint**: `GET /api/artworks/by_tag/?tag={tag}`

Returns artworks that have the specified tag.

**Response**: Same format as List Artworks.

### Get Popular Artworks

**Endpoint**: `GET /api/artworks/popular/?limit={limit}`

Returns the most popular artworks based on the number of likes. Default limit is 10.

**Response**: Same format as List Artworks.

### Get Recent Artworks

**Endpoint**: `GET /api/artworks/recent/?limit={limit}`

Returns the most recent artworks. Default limit is 10.

**Response**: Same format as List Artworks.

### Get User's Artworks

**Endpoint**: `GET /api/artworks/user_artworks/?user_id={user_id}`

Returns all artworks created by a specific user.

**Response**: Same format as List Artworks.

## Reviews

### List Reviews

**Endpoint**: `GET /api/reviews/`

Returns a paginated list of all reviews, ordered by creation date (newest first).

### Filter Reviews by Artwork

**Endpoint**: `GET /api/reviews/?artwork={artwork_id}`

Returns all reviews for a specific artwork.

### Get Review Details

**Endpoint**: `GET /api/reviews/{id}/`

Returns detailed information about a specific review.

### Create Review

**Endpoint**: `POST /api/reviews/`

Creates a new review. Requires authentication.

**Request Body**:
```json
{
  "artwork": 1,
  "content": "This is a great piece of art!",
  "rating": 5
}
```

**Response**: Returns the created review with status 201.

### Update Review

**Endpoint**: `PUT /api/reviews/{id}/`

Updates an existing review. Requires authentication and user must be the reviewer or an admin.

**Request Body**: Same as create, with updated fields.

**Response**: Returns the updated review.

### Delete Review

**Endpoint**: `DELETE /api/reviews/{id}/`

Deletes an existing review. Requires authentication and user must be the reviewer or an admin.

**Response**: Status 204 No Content on success.

## Users

### List Users

**Endpoint**: `GET /api/users/`

Returns a paginated list of all users, ordered by join date.

### Get User Details

**Endpoint**: `GET /api/users/{id}/`

Returns detailed information about a specific user. Requires authentication.

### Get Current User

**Endpoint**: `GET /api/users/me/`

Returns detailed information about the currently authenticated user.

## Profiles

### Get Current User's Profile

**Endpoint**: `GET /api/profiles/me/`

Returns the profile of the currently authenticated user.

### Get Profile Details

**Endpoint**: `GET /api/profiles/{id}/`

Returns detailed information about a specific user's profile. Requires authentication.

### Update Profile

**Endpoint**: `PUT /api/profiles/{id}/`

Updates an existing profile. Requires authentication and user must own the profile or be an admin.

**Request Body**:
```json
{
  "bio": "I am an artist who loves to create oil paintings of landscapes.",
  "location": "New York, NY",
  "profile_picture": "https://example.com/profile.jpg",
  "website": "https://mywebsite.com",
  "birth_date": "1990-01-01"
}
```

**Response**: Returns the updated profile.

## Health Check

**Endpoint**: `GET /api/health/`

Returns information about the API status and database connection.

**Response Example**:
```json
{
  "status": "healthy",
  "api_version": "1.0.0",
  "database": {
    "status": "OK",
    "counts": {
      "artworks": 2,
      "reviews": 2,
      "users": 3
    }
  },
  "message": "Art Critique API is running"
}
```