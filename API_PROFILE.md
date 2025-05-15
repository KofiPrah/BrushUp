# User Profile API

This document describes the User Profile endpoints for the Art Critique application.

## Profile Endpoints

### Get Current User Profile

**Endpoint:** `/api/profiles/me/`
**Method:** GET
**Authentication:** Required
**Description:** Returns the profile of the currently authenticated user

**Example Request:**
```bash
curl -k https://localhost:5000/api/profiles/me/ \
  -H "Cookie: sessionid=your_session_cookie" \
  -H "X-CSRFToken: your_csrf_token"
```

**Example Response:**
```json
{
  "id": 1,
  "username": "admin",
  "email": "admin@example.com",
  "bio": "Art enthusiast and critic",
  "location": "New York",
  "profile_picture": "https://example.com/profile.jpg",
  "website": "https://myportfolio.com",
  "birth_date": "1990-01-01"
}
```

### Update Current User Profile

**Endpoint:** `/api/profiles/me/`
**Method:** PUT or PATCH
**Authentication:** Required
**Description:** Updates the profile of the currently authenticated user. PUT requires all fields, PATCH allows partial updates.

**Request Headers:**
- Content-Type: application/json
- X-CSRFToken: (token from the csrf endpoint)

**Request Body (PUT - full update):**
```json
{
  "bio": "Professional artist and educator",
  "location": "San Francisco",
  "profile_picture": "https://example.com/new_profile.jpg",
  "website": "https://myart.com",
  "birth_date": "1990-01-01",
  "first_name": "Jane",
  "last_name": "Smith"
}
```

**Request Body (PATCH - partial update):**
```json
{
  "bio": "Professional artist and educator",
  "location": "San Francisco"
}
```

**Example Request:**
```bash
curl -k https://localhost:5000/api/profiles/me/ -X PATCH \
  -H "Content-Type: application/json" \
  -H "Cookie: sessionid=your_session_cookie" \
  -H "X-CSRFToken: your_csrf_token" \
  -d '{"bio": "Professional artist and educator", "location": "San Francisco"}'
```

**Example Success Response:**
```json
{
  "id": 1,
  "username": "admin",
  "email": "admin@example.com",
  "bio": "Professional artist and educator",
  "location": "San Francisco",
  "profile_picture": "https://example.com/profile.jpg",
  "website": "https://myportfolio.com",
  "birth_date": "1990-01-01"
}
```

**Example Error Response:**
```json
{
  "birth_date": ["Date has wrong format. Use YYYY-MM-DD format."]
}
```

### Get Profile by ID (Staff or Owner only)

**Endpoint:** `/api/profiles/{id}/`
**Method:** GET
**Authentication:** Required
**Description:** Returns a specific profile by ID. User must be staff or the owner of the profile.

**Example Request:**
```bash
curl -k https://localhost:5000/api/profiles/1/ \
  -H "Cookie: sessionid=your_session_cookie" \
  -H "X-CSRFToken: your_csrf_token"
```

**Example Response:**
Same format as "Get Current User Profile"

### List All Profiles (Staff only)

**Endpoint:** `/api/profiles/`
**Method:** GET
**Authentication:** Required
**Description:** Lists all user profiles. Only accessible to staff users.

**Example Request:**
```bash
curl -k https://localhost:5000/api/profiles/ \
  -H "Cookie: sessionid=your_session_cookie" \
  -H "X-CSRFToken: your_csrf_token"
```

**Example Response:**
```json
[
  {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "bio": "Art enthusiast and critic",
    "location": "New York",
    "profile_picture": "https://example.com/profile.jpg",
    "website": "https://myportfolio.com",
    "birth_date": "1990-01-01"
  },
  {
    "id": 2,
    "username": "artist1",
    "email": "artist1@example.com",
    "bio": "Contemporary painter",
    "location": "Los Angeles",
    "profile_picture": "https://example.com/profile2.jpg",
    "website": "https://artist1.com",
    "birth_date": "1985-05-15"
  }
]
```

## Notes for Profile Fields

- `bio` - A text description of the user (max 500 characters)
- `location` - The user's location or city (max 100 characters)
- `profile_picture` - URL to the user's profile picture
- `website` - URL to the user's personal website or portfolio
- `birth_date` - The user's birth date in YYYY-MM-DD format
- `first_name` - The user's first name (updates the User model)
- `last_name` - The user's last name (updates the User model)

## Integration with Authentication

The profile endpoints work seamlessly with the authentication flow:

1. Get a CSRF token from `/api/auth/csrf/`
2. Login using `/api/auth/login/`
3. Access profile information at `/api/profiles/me/`
4. Update profile with PUT/PATCH to `/api/profiles/me/`

## Error Handling

- 401 Unauthorized - User is not authenticated
- 403 Forbidden - User is trying to access a profile they don't own
- 400 Bad Request - Invalid data in profile update
- 404 Not Found - Profile not found