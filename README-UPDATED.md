# Brush Up - Art Critique Platform

## Overview
Brush Up (formerly Art Critique) is a web application for art professionals to create, share, and collaborate on digital creative works.

## Features
- User authentication via Google OAuth
- Artwork uploads with S3 storage integration
- Critique system with reactions (Helpful/Inspiring/Detailed)
- Karma point system for community contributions
- Comprehensive artwork gallery with search and filter features

## Running the Application

To run the application in Replit, simply use the provided start script:

```
./start_http_server.sh
```

This script:
1. Ensures the CritiqueSerializer has the required methods
2. Starts the application in HTTP mode (without SSL)
3. Works properly in Replit's environment

## Technical Notes

- The application is configured to run in HTTP mode in Replit, as Replit handles HTTPS termination
- Using the start script ensures compatibility with Replit's environment
- If you need to redeploy, use Replit's deployment feature

## Troubleshooting

If you encounter issues:

1. Make sure the application is running in HTTP mode on port 5000
2. Verify that the CritiqueSerializer has the get_reactions_count method
3. Check for any database connection issues in the logs