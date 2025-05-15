# Google Login Instructions

## Access the Login Page

Your Google OAuth credentials have been successfully configured in the Art Critique application. To test Google login functionality, you'll need to:

1. Access the login page at: 
   - **When using HTTPS**: https://workspace.kprah4.repl.co/accounts/login/
   - **When using HTTP**: http://workspace.kprah4.repl.co/accounts/login/

2. On the login page, you'll see a red "Sign in with Google" button.

3. Click this button to initiate the Google OAuth flow.

## Troubleshooting

If you're having issues with the application not loading or SSL errors, try:

1. Accessing the HTTP version of the site directly (http://workspace.kprah4.repl.co/accounts/login/)

2. If you're getting a "redirect_uri_mismatch" error from Google, ensure your Google Cloud Console project has the following redirect URIs configured:
   - https://workspace.kprah4.repl.co/accounts/google/login/callback/
   - http://workspace.kprah4.repl.co/accounts/google/login/callback/

3. If you're getting other Google OAuth errors, check that the client ID and client secret are correctly configured.

## Verify Configuration

The following environment variables are now properly configured:
- GOOGLE_OAUTH_CLIENT_ID
- GOOGLE_OAUTH_CLIENT_SECRET

These credentials will be used by Django Allauth to authenticate users with Google.

After successfully logging in with Google, you'll be able to use the image upload functionality and other features that require authentication.