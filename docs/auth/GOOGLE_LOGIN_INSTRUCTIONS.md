# Google Login Setup for Art Critique

To enable Google login for the Art Critique application, you need to set up a Google OAuth client.

## Step-by-Step Instructions

1. **Create a Google Cloud project**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select an existing one

2. **Configure the OAuth consent screen**
   - Navigate to "APIs & Services" > "OAuth consent screen"
   - Select "External" user type
   - Fill in the required information (app name, support email, etc.)
   - Add scopes for email and profile information

3. **Create OAuth credentials**
   - Navigate to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Select "Web application" as the application type
   - Add your application's domain to "Authorized JavaScript origins"
   - Add your application's callback URL to "Authorized redirect URIs":
     ```
     https://your-domain.repl.co/accounts/google/login/callback/
     ```

4. **Set environment variables in your Replit project**
   - Go to your Replit project
   - Click on the "Secrets" tool (padlock icon)
   - Add the following secrets:
     - `GOOGLE_OAUTH_CLIENT_ID` = Your Google client ID
     - `GOOGLE_OAUTH_CLIENT_SECRET` = Your Google client secret

5. **Restart your application**
   - The Google login button will now work!

## Troubleshooting

If you encounter issues:
- Verify that your redirect URI is correctly set in Google Cloud Console
- Check that your domain is properly configured
- Make sure you've added the correct environment variables
- Restart your application after making changes

For detailed setup information, see the full [Google OAuth Setup Guide](GOOGLE_OAUTH_SETUP.md).