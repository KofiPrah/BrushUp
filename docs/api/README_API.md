# Art Critique API Guide

This guide explains how to use the Art Critique API with authentication.

## Authentication

The Art Critique API uses token-based authentication for secure API access. This guide shows how to authenticate and use protected endpoints.

### Login and Get CSRF Token

Before making any POST, PUT, PATCH or DELETE requests, you need to get a CSRF token:

```bash
# Get CSRF token
curl -k https://localhost:5000/api/auth/csrf/ -c cookies.txt
```

This will save cookies to a file and return a CSRF token:

```json
{"csrfToken": "your-csrf-token"}
```

### Login

Use the CSRF token to log in:

```bash
curl -k https://localhost:5000/api/auth/login/ \
  -X POST \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: your-csrf-token" \
  -b cookies.txt -c cookies.txt \
  -d '{"username": "your-username", "password": "your-password"}'
```

Successful login returns user info:

```json
{
  "user": {
    "id": 2,
    "username": "testuser",
    "email": "test@example.com",
    "profile": null,
    "auth_info": {
      "is_authenticated": true,
      "is_staff": false,
      "is_superuser": false,
      "date_joined": "2025-05-15T04:55:53.335671Z",
      "last_login": null
    }
  }
}
```

### Check Authentication Status

Verify your authentication status:

```bash
curl -k https://localhost:5000/api/auth/session/ -b cookies.txt
```

Returns:

```json
{
  "authenticated": true,
  "user": {
    "id": 2,
    "username": "testuser",
    "email": "test@example.com",
    "profile": null,
    "auth_info": {
      "is_authenticated": true,
      "is_staff": false,
      "is_superuser": false,
      "date_joined": "2025-05-15T04:55:53.335671Z",
      "last_login": null
    }
  }
}
```

## Example API Calls

### Get Artworks

```bash
curl -k https://localhost:5000/api/artworks/ -b cookies.txt
```

### Create a New Artwork

```bash
curl -k https://localhost:5000/api/artworks/ \
  -X POST \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: your-csrf-token" \
  -b cookies.txt \
  -d '{
    "title": "New Artwork",
    "description": "A beautiful landscape painting",
    "medium": "Oil on canvas",
    "dimensions": "24x36 inches",
    "tags": "landscape,nature,mountains"
  }'
```

### Update an Artwork

```bash
curl -k https://localhost:5000/api/artworks/1/ \
  -X PUT \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: your-csrf-token" \
  -b cookies.txt \
  -d '{
    "title": "Updated Title",
    "description": "Updated description",
    "medium": "Updated medium",
    "dimensions": "Updated dimensions",
    "tags": "updated,tags"
  }'
```

### Delete an Artwork

```bash
curl -k https://localhost:5000/api/artworks/1/ \
  -X DELETE \
  -H "X-CSRFToken: your-csrf-token" \
  -b cookies.txt
```

### Like an Artwork

```bash
curl -k https://localhost:5000/api/artworks/1/like/ \
  -X POST \
  -H "X-CSRFToken: your-csrf-token" \
  -b cookies.txt
```

### Create a Review

```bash
curl -k https://localhost:5000/api/reviews/ \
  -X POST \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: your-csrf-token" \
  -b cookies.txt \
  -d '{
    "artwork": 1,
    "content": "This is a great artwork!",
    "rating": 5
  }'
```

### Log Out

```bash
curl -k https://localhost:5000/api/auth/logout/ \
  -X POST \
  -H "X-CSRFToken: your-csrf-token" \
  -b cookies.txt
```

## JavaScript Example

If you're using JavaScript to make API calls, here's an example using the fetch API:

```javascript
// Function to get CSRF token
async function getCSRFToken() {
  const response = await fetch('/api/auth/csrf/', {
    method: 'GET',
    credentials: 'include'  // Important for cookies
  });
  const data = await response.json();
  return data.csrfToken;
}

// Login function
async function login(username, password) {
  const csrfToken = await getCSRFToken();
  
  const response = await fetch('/api/auth/login/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': csrfToken
    },
    credentials: 'include',
    body: JSON.stringify({ username, password })
  });
  
  return response.json();
}

// Create artwork function
async function createArtwork(artworkData) {
  const csrfToken = await getCSRFToken();
  
  const response = await fetch('/api/artworks/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': csrfToken
    },
    credentials: 'include',
    body: JSON.stringify(artworkData)
  });
  
  return response.json();
}

// Example usage
login('testuser', 'password123')
  .then(data => {
    console.log('Logged in:', data);
    
    // Create a new artwork
    return createArtwork({
      title: 'JavaScript Created Artwork',
      description: 'Created via JavaScript API call',
      medium: 'Digital',
      tags: 'javascript,api,example'
    });
  })
  .then(artwork => {
    console.log('Created artwork:', artwork);
  })
  .catch(error => {
    console.error('Error:', error);
  });
```

## Notes on CSRF Protection

- CSRF protection is required for all non-GET requests
- Always include the X-CSRFToken header for POST, PUT, PATCH, and DELETE requests
- The CSRF token is tied to your session, so you need to include cookies in your requests

For more detailed API documentation, see [API_DOCS.md](API_DOCS.md).