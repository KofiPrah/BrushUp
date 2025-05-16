# Art Critique Authentication API

This document describes the authentication endpoints for the Art Critique application.

## Authentication Flow

The typical authentication flow for the API is:

1. Get a CSRF token from the `/api/auth/csrf/` endpoint
2. Login using the `/api/auth/login/` endpoint with the CSRF token
3. Check authentication status using the `/api/auth/session/` endpoint
4. Perform authenticated requests with the session cookie and CSRF token
5. Logout using the `/api/auth/logout/` endpoint

## Endpoints

### Get CSRF Token

**Endpoint:** `/api/auth/csrf/`
**Method:** GET
**Description:** Returns a CSRF token that must be used for all subsequent POST requests

**Example Request:**
```bash
curl -k https://localhost:5000/api/auth/csrf/ -c cookies.txt
```

**Example Response:**
```json
{
  "csrfToken": "abcdef123456789"
}
```

### Login

**Endpoint:** `/api/auth/login/`
**Method:** POST
**Description:** Authenticates a user and creates a session

**Request Headers:**
- Content-Type: application/json
- X-CSRFToken: (token from the csrf endpoint)

**Request Body:**
```json
{
  "username": "yourusername",
  "password": "yourpassword"
}
```

**Example Request:**
```bash
curl -k https://localhost:5000/api/auth/login/ -X POST \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: abcdef123456789" \
  -b cookies.txt -c cookies.txt \
  -d '{"username": "admin", "password": "password123"}'
```

**Example Success Response:**
```json
{
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "first_name": "",
    "last_name": "",
    "profile": {
      "id": 2,
      "bio": "",
      "location": "",
      "profile_picture": "",
      "website": "",
      "birth_date": null
    },
    "auth_info": {
      "is_authenticated": true,
      "is_staff": true,
      "is_superuser": true,
      "date_joined": "2025-05-15T04:32:28.865890Z",
      "last_login": "2025-05-15T07:54:35.982769Z"
    }
  }
}
```

**Example Error Response:**
```json
{
  "error": "Invalid credentials"
}
```

### Check Session

**Endpoint:** `/api/auth/session/`
**Method:** GET
**Description:** Checks if the current session is authenticated

**Example Request:**
```bash
curl -k https://localhost:5000/api/auth/session/ -b cookies.txt
```

**Example Authenticated Response:**
```json
{
  "id": 1,
  "username": "admin",
  "email": "admin@example.com",
  "first_name": "",
  "last_name": "",
  "profile": {
    "id": 2,
    "bio": "",
    "location": "",
    "profile_picture": "",
    "website": "",
    "birth_date": null
  },
  "auth_info": {
    "is_authenticated": true,
    "is_staff": true,
    "is_superuser": true,
    "date_joined": "2025-05-15T04:32:28.865890Z",
    "last_login": "2025-05-15T07:54:35.982769Z"
  }
}
```

**Example Unauthenticated Response:**
```json
{
  "authenticated": false,
  "detail": "Not authenticated"
}
```

### Logout

**Endpoint:** `/api/auth/logout/`
**Method:** POST
**Description:** Logs out the current user and invalidates the session

**Request Headers:**
- X-CSRFToken: (token from the csrf endpoint)
- Referer: (the domain URL, e.g., https://localhost:5000/)

**Example Request:**
```bash
curl -k https://localhost:5000/api/auth/logout/ -X POST \
  -H "Referer: https://localhost:5000/" \
  -H "X-CSRFToken: abcdef123456789" \
  -b cookies.txt -c cookies.txt
```

**Example Response:**
```json
{
  "detail": "Successfully logged out"
}
```

## User Profile

**Endpoint:** `/api/auth/user/`
**Method:** GET
**Description:** Returns the currently authenticated user's profile

**Example Request:**
```bash
curl -k https://localhost:5000/api/auth/user/ -b cookies.txt
```

**Example Response:**
```json
{
  "id": 1,
  "username": "admin",
  "email": "admin@example.com",
  "first_name": "",
  "last_name": "",
  "profile": {
    "id": 2,
    "bio": "",
    "location": "",
    "profile_picture": "",
    "website": "",
    "birth_date": null
  },
  "auth_info": {
    "is_authenticated": true,
    "is_staff": true,
    "is_superuser": true,
    "date_joined": "2025-05-15T04:32:28.865890Z",
    "last_login": "2025-05-15T07:54:35.982769Z"
  }
}
```

## Notes for Frontend Implementation

1. Store the CSRF token on the client side and include it in all POST, PUT, PATCH, and DELETE requests.
2. Use cookies for session management - the server will set the session cookie automatically.
3. For security reasons, always include the Referer header in requests that require CSRF protection.
4. Check the session status to determine if a user is logged in before displaying protected content.
5. Always handle authentication errors gracefully and redirect users to the login page when needed.