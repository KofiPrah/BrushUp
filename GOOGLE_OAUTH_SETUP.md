# Google OAuth Setup for Art Critique

This document explains how to configure Google OAuth for the Art Critique application.

## Overview

Google OAuth allows users to sign in to the application using their Google accounts, providing a seamless login experience without requiring a separate account creation process.

## Current Configuration

The application is set up to use Google OAuth with the following configuration:

- Client ID and Secret are stored in environment variables:
  - `GOOGLE_OAUTH_CLIENT_ID`
  - `GOOGLE_OAUTH_CLIENT_SECRET`

- Requested scopes:
  - `profile` - To get basic profile information
  - `email` - To get the user's email address

- Auto signup enabled - New users will be automatically created based on their Google profile

## Required Redirect URIs

For Google OAuth to work correctly, you must add these redirect URIs to your Google Cloud Console project:

1. For local/development environment:
   - `https://workspace.kprah4.repl.co/accounts/google/login/callback/`

2. For production (if applicable):
   - `https://your-production-domain.com/accounts/google/login/callback/`

## Verifying Google OAuth Setup

1. Navigate to the login page at `/accounts/login/`
2. Click on the "Login with Google" button
3. You should be redirected to Google's login page
4. After successful authentication, you should be redirected back to the application

## Common Issues

1. **"Missing required parameter: client_id" or "Error 400: invalid_request"**:
   - Check that the `GOOGLE_OAUTH_CLIENT_ID` and `GOOGLE_OAUTH_CLIENT_SECRET` environment variables are set correctly
   - Ensure that the OAuth Client ID is properly configured in Google Cloud Console
   - Verify that the redirect URIs are correctly set in Google Cloud Console

2. **"Error: redirect_uri_mismatch"**:
   - This means the redirect URI used by the application doesn't match any URIs configured in Google Cloud Console
   - Add the correct redirect URI to the authorized redirect URIs list in your Google OAuth client settings

3. **"Error: invalid_client"**:
   - This typically means the client ID or secret is incorrect
   - Check that you've copied the correct values from Google Cloud Console

## Google Cloud Console Setup Instructions

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Navigate to "APIs & Services" > "Credentials"
4. Click "Create Credentials" > "OAuth client ID"
5. Select "Web application" as the application type
6. Add the necessary redirect URIs (as mentioned above)
7. Copy the generated Client ID and Client Secret
8. Set these values as environment variables in your Replit environment

## Testing the Configuration

To verify that the Google OAuth integration is working correctly:

1. Make sure you're logged out of the application
2. Go to the login page
3. Click "Login with Google"
4. Complete the Google authentication flow
5. You should be redirected back to the application and logged in

Once logged in, you can test additional functionality like uploading artwork images, which requires authentication.