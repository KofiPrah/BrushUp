# Google OAuth Setup Guide for Art Critique

This guide will help you set up Google OAuth authentication for the Art Critique application.

## Prerequisites

1. A Google account
2. Access to the [Google Cloud Console](https://console.cloud.google.com/)

## Step 1: Create a Google Cloud Project

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Click on the project dropdown at the top of the page
3. Click "New Project"
4. Enter a name for your project (e.g., "Art Critique")
5. Click "Create"

## Step 2: Configure OAuth Consent Screen

1. From your Google Cloud project dashboard, go to "APIs & Services" > "OAuth consent screen"
2. Select "External" user type (unless you have a Google Workspace organization)
3. Click "Create"
4. Fill in the required fields:
   - App name: "Art Critique"
   - User support email: Your email address
   - Developer contact information: Your email address
5. Click "Save and Continue"
6. On the Scopes screen, click "Add or Remove Scopes"
7. Select the following scopes:
   - `./auth/userinfo.email`
   - `./auth/userinfo.profile`
   - `openid`
8. Click "Save and Continue"
9. Add any test users if needed
10. Click "Save and Continue"
11. Review your settings and click "Back to Dashboard"

## Step 3: Create OAuth Client ID

1. From your Google Cloud project dashboard, go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth client ID"
3. Select "Web application" as the application type
4. Enter a name for your client (e.g., "Art Critique Web Client")
5. Add authorized JavaScript origins:
   - For development: `https://your-replit-dev-domain.repl.co` (replace with your Replit domain)
   - For production: Your production domain
6. Add authorized redirect URIs:
   - For development: `https://your-replit-dev-domain.repl.co/accounts/google/login/callback/` (replace with your Replit domain)
   - For production: Your production redirect URI
7. Click "Create"
8. You'll see your Client ID and Client Secret - copy these values

## Step 4: Set Environment Variables

Add the following environment variables to your Replit project:

```
GOOGLE_OAUTH_CLIENT_ID=your_client_id_here
GOOGLE_OAUTH_CLIENT_SECRET=your_client_secret_here
```

## Step 5: Verify Setup

1. Restart your application
2. Try logging in with Google
3. You should be redirected to Google's login page and then back to your application

## Troubleshooting

If you encounter issues with Google OAuth:

- Verify your redirect URIs are correctly set in the Google Cloud Console
- Ensure your environment variables are correctly set
- Check that your domain is correctly configured in the OAuth consent screen
- Confirm that your application is making requests to the correct OAuth endpoints

## Security Notes

- Never commit your Client Secret to your code repository
- Regularly review and audit OAuth access
- Consider implementing additional security measures like CSRF protection
- Follow Google's OAuth best practices