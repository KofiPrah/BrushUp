# Google OAuth2 Setup Guide for Art Critique

This guide explains how to configure Google OAuth2 authentication for the Art Critique application, allowing users to sign in using their Google accounts.

## Prerequisites

- A Google account with access to Google Cloud Console
- Your Art Critique application domain (e.g., artcritique.replit.app)

## Step 1: Create a Google Cloud Project

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Click on the project dropdown at the top of the page
3. Click "New Project"
4. Enter a name for your project (e.g., "Art Critique")
5. Click "Create"

## Step 2: Enable the Google OAuth API

1. Select your newly created project
2. From the left sidebar, navigate to "APIs & Services" > "Library"
3. Search for "Google OAuth2 API" or "Google+ API"
4. Click on the API and then click "Enable"

## Step 3: Configure the OAuth Consent Screen

1. From the left sidebar, navigate to "APIs & Services" > "OAuth consent screen"
2. Select "External" as the user type (or "Internal" if you're using Google Workspace)
3. Click "Create"
4. Fill in the required information:
   - App name: "Art Critique"
   - User support email: Your email address
   - Developer contact information: Your email address
5. Click "Save and Continue"
6. Add the following scopes:
   - email
   - profile
   - openid
7. Click "Save and Continue"
8. Add any test users if needed (for development)
9. Click "Save and Continue"
10. Review your settings and click "Back to Dashboard"

## Step 4: Create OAuth Client ID

1. From the left sidebar, navigate to "APIs & Services" > "Credentials"
2. Click "Create Credentials" and select "OAuth client ID"
3. Application type: Select "Web application"
4. Name: "Art Critique Web Client"
5. Authorized JavaScript origins: 
   - Add your domain (e.g., `https://artcritique.replit.app`)
   - For development, also add `https://localhost:8000` or your development URL
6. Authorized redirect URIs:
   - Add `https://artcritique.replit.app/accounts/google/login/callback/`
   - For development, also add `https://localhost:8000/accounts/google/login/callback/`
7. Click "Create"
8. Note the generated Client ID and Client Secret

## Step 5: Configure Art Critique with OAuth Credentials

### Option 1: Environment Variables (Recommended)

1. Set the following environment variables in your Replit environment:
   ```
   GOOGLE_CLIENT_ID=your_client_id
   GOOGLE_SECRET_KEY=your_client_secret
   ```

### Option 2: Django Admin Interface

1. Log in to your Django admin interface (`/admin/`)
2. Navigate to "Social Applications" under the "Social Accounts" section
3. Click "Add Social Application"
4. Fill in the following information:
   - Provider: Google
   - Name: Google
   - Client ID: Your OAuth client ID from Google
   - Secret key: Your OAuth client secret from Google
   - Sites: Add your site (e.g., artcritique.replit.app)
5. Click "Save"

## Step 6: Test Google Login

1. Go to your application's login page
2. Click the "Login with Google" button
3. Follow the Google OAuth flow
4. You should be redirected back to your application and logged in

## Troubleshooting

- If you see "Invalid redirect URI" errors, make sure your redirect URI is exactly as registered in the Google Cloud Console
- If you see "Error: invalid_client", double-check your client ID and secret
- If you're using HTTPS locally for development, make sure your SSL certificate is properly configured
- For cross-site request errors, ensure your Django CORS settings are properly configured

## Security Considerations

- Never commit your Client ID and Client Secret to version control
- Use environment variables or a secure secrets management system
- Regularly review authorized applications in the Google Cloud Console
- Keep your OAuth consent screen information up to date

## Additional Resources

- [Django Allauth Documentation](https://django-allauth.readthedocs.io/en/latest/providers.html#google)
- [Google OAuth2 Documentation](https://developers.google.com/identity/protocols/oauth2)