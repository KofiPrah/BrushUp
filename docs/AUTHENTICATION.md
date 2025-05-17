# Authentication System Documentation

## Overview
The Art Critique platform uses Django Allauth for authentication, providing a robust and secure system for user management with features including:

- User registration/signup
- Login/logout functionality
- Password recovery
- Email verification
- Profile management
- Social authentication (configured but providers need to be set up)

## Implementation Details

### 1. Package Integration
Django Allauth is fully integrated with the following components:

- **INSTALLED_APPS**: Added required Allauth apps: `allauth`, `allauth.account`, `allauth.socialaccount`
- **Authentication Backends**: Configured to support both standard Django authentication and Allauth's email authentication
- **URL Configuration**: Added Allauth URLs under the `/accounts/` prefix
- **Database Setup**: Created a Site model for proper domain configuration
- **Templates**: Created custom templates with Bootstrap styling for all authentication pages
- **Custom Context Processor**: Added `site_info` context processor for site-related template data

### 2. User Experience Features

- **Navigation**: Added login/signup links in the navigation bar
- **User Menu**: Added dropdown menu for authenticated users with profile access
- **Profile Management**: Created views and forms for viewing and editing user profiles
- **Authentication Test**: Added a test page at `/auth-test/` to verify authentication status

### 3. Admin Integration

- **Enhanced User Admin**: Extended Django's UserAdmin to include Profile as an inline
- **Profile Model**: Connected to User model with one-to-one relationship
- **Admin Filtering**: Added advanced filters and search capabilities for user management

### 4. Security Considerations

- **SSL Support**: Configured flexible SSL security settings
- **CSRF Protection**: Maintained Django's CSRF protection for forms
- **Password Policies**: Using Django's built-in password validation
- **Session Management**: Configured session settings for security and usability

## Usage

### User Registration
New users can register at `/accounts/signup/`. The following fields are required:
- Username
- Email
- Password (with confirmation)

### Profile Management
After registration, users can manage their profile at `/profile/` and edit details at `/profile/edit/`.

### Authentication Testing
Visit `/auth-test/` to see your current authentication status and test the system.

## Social Authentication

Social authentication is configured with Google OAuth2 integration. Users can sign in with their Google accounts from both the login and signup pages.

### Configured Providers

1. **Google OAuth2**: Fully integrated - users can sign in with Google accounts
   - Requires setting up Google API credentials (see GOOGLE_OAUTH_SETUP.md)
   - Environment variables: GOOGLE_CLIENT_ID and GOOGLE_SECRET_KEY

### Adding Social Authentication Providers

To add additional providers:

1. Add the provider to INSTALLED_APPS (e.g., 'allauth.socialaccount.providers.github')
2. Configure the provider in SOCIALACCOUNT_PROVIDERS in settings.py
3. Set up credentials via the Django admin interface at `/admin/socialaccount/socialapp/`

## Future Enhancements

Potential future authentication enhancements include:
- Two-factor authentication
- OAuth2 support for API access
- Enhanced password policies
- Social login implementation (GitHub, Google, etc.)