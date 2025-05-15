# Art Critique Authentication System

This document provides a complete overview of the authentication system implemented in the Art Critique application.

## Authentication Architecture

The authentication system in Art Critique uses a hybrid approach:

1. **Django's Built-in Authentication**: 
   - Uses Django's session-based authentication
   - Handles user registration, login, password reset, etc.

2. **Django AllAuth**: 
   - Provides social authentication (Google OAuth2)
   - Manages email verification
   - Handles account management

3. **REST API Authentication Layer**:
   - Session-based authentication for frontend applications
   - CSRF protection for secure form submissions
   - User profile and session management endpoints

## Authentication Flows

### Traditional Login

1. User visits `/accounts/login/`
2. User submits credentials
3. Django authenticates and creates a session
4. Frontend can verify authentication via `/api/auth/session/`

### Social Authentication (Google)

1. User clicks "Login with Google"
2. User is redirected to Google for authentication
3. Upon successful authentication, user is redirected back
4. Django AllAuth creates/authenticates the user
5. Frontend can verify authentication via `/api/auth/session/`

### API-Based Authentication (for SPAs)

1. Frontend gets CSRF token from `/api/auth/csrf/`
2. Frontend submits login form to `/accounts/login/` with CSRF token
3. Django creates session cookie
4. Frontend verifies authentication via `/api/auth/session/`
5. Frontend gets user profile via `/api/auth/user/`
6. Logout via `/api/auth/logout/`

## Setup and Configuration

### Environment Modes

The application can run in two modes:

1. **Development Mode (HTTPS)**:
   - Uses self-signed certificates
   - Handles SSL/TLS directly in the application
   - Environment variable: `SSL_ENABLED=true`

2. **Production Mode (HTTP Behind SSL Termination)**:
   - No SSL certificates needed at application level
   - SSL/TLS handled by infrastructure (e.g., Replit's load balancer)
   - Environment variable: `SSL_ENABLED=false`

### Starting the Server

Use the flexible server script to run in either mode:

```bash
# Development mode (HTTPS)
SSL_ENABLED=true ./run_flexible_server.sh

# Production mode (HTTP)
SSL_ENABLED=false ./run_flexible_server.sh
```

### Testing Authentication Endpoints

Use the provided test script:

```bash
# Development mode (HTTPS)
./test_auth_api.py

# Production mode (HTTP)
./test_auth_api.py --no-ssl
```

## API Endpoints

See `API_AUTHENTICATION.md` for detailed documentation of all authentication endpoints.

## Deployment Notes

See `REPLIT_DEPLOYMENT_GUIDE.md` for information about deploying the application on Replit.

## Security Considerations

1. **CSRF Protection**:
   - All state-changing operations require CSRF tokens
   - Frontend applications should get tokens via `/api/auth/csrf/`

2. **Session Security**:
   - Sessions are HTTP-only cookies
   - Session timeout configured in Django settings

3. **Password Security**:
   - Django's password hashing (PBKDF2 with SHA256)
   - Password strength validation

4. **OAuth Security**:
   - Valid redirect URIs configured in Google OAuth settings
   - State parameter used to prevent CSRF in OAuth flow

## Troubleshooting

### SSL/TLS Issues

If encountering SSL issues:
1. Verify the server is running in the correct mode
2. Check if certificates exist (for development mode)
3. Use `--no-ssl` flag for testing in production mode

### Authentication Issues

1. Validate that session cookies are being set correctly
2. Check CSRF token is included in requests
3. Verify redirect URLs for social authentication