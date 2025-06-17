# Brush Up - Art Critique Platform

## Overview

Brush Up (formerly Art Critique) is a Django-powered web application that provides a comprehensive platform for art professionals to share, critique, and engage with creative works through innovative digital interactions. The platform features user authentication via Google OAuth, artwork uploads with S3 storage integration, a critique system with reactions, and a karma point system for community contributions.

## System Architecture

### Backend Architecture
- **Framework**: Django 5.0.2 with Django REST Framework for API endpoints
- **Server**: Gunicorn WSGI server optimized for production deployment
- **Database**: PostgreSQL for primary data storage
- **Authentication**: Django Allauth with Google OAuth integration
- **API**: RESTful API with comprehensive serializers for frontend integration

### Frontend Architecture
- **Templates**: Django templates with Bootstrap 5.3.6 for responsive design
- **JavaScript**: Vanilla JavaScript with modern ES6+ features
- **Styling**: Bootstrap Icons and custom CSS for enhanced user experience
- **Interactive Elements**: Dynamic artwork galleries, critique systems, and user profiles

### HTTP-Only Configuration
The application is specifically configured to run in HTTP-only mode to ensure compatibility with Replit's load balancer and deployment environment. SSL termination is handled at the infrastructure level.

## Key Components

### Core Applications
- **artcritique/**: Main Django application with project settings and URL configuration
- **critique/**: Core functionality for artwork management, critique system, and user profiles
- **API Layer**: Comprehensive REST API endpoints for all major features

### Authentication System
- Google OAuth integration via Django Allauth
- User profiles with karma tracking
- Session management and security features

### Artwork Management
- File upload handling with support for multiple formats (JPEG, PNG, GIF, WebP, SVG, BMP, TIFF)
- S3 integration for scalable media storage
- Image processing and display optimization
- **Advanced Version Management System**:
  - Preserves image history during version creation
  - Safe version restoration with auto-backup of current state
  - Drag-and-drop version comparison interface
  - Version archiving and management tools

### Critique System
- Multi-type reactions (Helpful, Inspiring, Detailed)
- Karma point system for community engagement
- Real-time reaction counting and display
- Advanced filtering and sorting capabilities

### Storage Integration
- AWS S3 bucket (brushup-media) for media file storage
- Local media fallback for development
- Pre-signed URL generation for secure access
- Optimized image delivery and caching

## Data Flow

### User Registration and Authentication
1. Users register via Google OAuth or standard Django authentication
2. Profile creation with karma initialization
3. Session management and permission handling

### Artwork Upload Process
1. User uploads artwork through Django forms
2. Files are processed and stored in S3 bucket
3. Metadata is saved to PostgreSQL database
4. Karma points are awarded for contributions

### Critique and Interaction Flow
1. Users browse artwork gallery with advanced filtering
2. Critiques are submitted and processed through API endpoints
3. Reactions are tracked and karma is calculated
4. Real-time updates to reaction counts and user profiles

### API Data Exchange
1. Frontend makes requests to Django REST API endpoints
2. Serializers handle data transformation and validation
3. Database queries are optimized for performance
4. Responses include computed fields like reaction counts

## External Dependencies

### Python Packages
- **Django 5.0.2**: Web framework foundation
- **djangorestframework 3.16.0**: API development
- **django-allauth 65.8.0**: Authentication system
- **django-cors-headers 4.7.0**: Cross-origin request handling
- **psycopg2-binary 2.9.9**: PostgreSQL database adapter
- **gunicorn 23.0.0**: WSGI HTTP server
- **boto3**: AWS S3 integration
- **pillow**: Image processing capabilities

### Frontend Dependencies
- **Bootstrap 5.3.6**: CSS framework for responsive design
- **Bootstrap Icons 1.13.1**: Icon library
- **Axios 1.9.0**: HTTP client for API requests

### Infrastructure Services
- **PostgreSQL 16**: Primary database server
- **AWS S3**: Cloud storage for media files
- **Replit Autoscale**: Deployment platform

## Deployment Strategy

### Production Configuration
- Gunicorn server with optimized worker configuration
- Single worker process to prevent memory issues on autoscale
- 120-second timeout for startup operations
- Memory management with request limits (1000 requests per worker)

### HTTP-Only Mode
- SSL termination handled by Replit infrastructure
- Empty certificate files to satisfy workflow requirements
- Environment variables configured for HTTP operation
- Port configuration with dynamic binding (PORT environment variable)

### Health Monitoring
- Comprehensive health check endpoint at `/api/health/`
- Database connectivity testing
- Service status reporting with proper HTTP status codes

### Environment Variables
- `DJANGO_SETTINGS_MODULE`: Django configuration
- `SSL_ENABLED`: Set to 'false' for HTTP-only operation
- `HTTP_ONLY`: Flag for HTTP mode configuration
- `PORT`: Dynamic port binding for deployment

### Database Management
- PostgreSQL connection with proper connection pooling
- Migration management for schema updates
- Karma system database tables and relationships

## Recent Changes

### June 17, 2025 - Comprehensive Version History System Enhancement ✓
- **Fixed save current state API**: Resolved 400 error by adding `force_create` parameter to bypass change detection
- **Implemented version deletion**: Users can now delete versions with safety checks to prevent deleting the only version
- **Enhanced thumbnail refresh**: New version uploads immediately update thumbnails without requiring page refresh
- **Added restoration snapshots**: Version restoration now creates automatic snapshots of current state before switching
- **Critique-version associations**: Critiques are now linked to specific artwork versions, eliminating shared critique counts
- **Fixed z-index overlap**: Version history card no longer interferes with main navigation dropdown
- **Fixed deletion endpoints**: Resolved 405 error for version deletion and 404 error for critique reply deletion
- **Enhanced user feedback control**: Users can now delete their own replies regardless of engagement levels

### June 14, 2025 - Version Management System Fixes
- **Fixed critical version creation bug**: Versions now properly preserve old images instead of overwriting them
- **Improved version switching**: Changed "restore" to "set as current" - no unnecessary version creation
- **Enhanced version integrity**: All version operations now maintain proper image history
- **Cleaner user experience**: Version switching is now intuitive and doesn't create version clutter

### Technical Details
#### June 17, 2025 Updates
- Added `artwork_version` foreign key to Critique model with proper migration
- Enhanced version creation API with `force_create` parameter for saving current state
- Implemented comprehensive version deletion with artwork ownership and safety validations
- Added real-time thumbnail updates using cache-busting timestamps
- Modified restoration to create automatic snapshots before version switching
- Fixed frontend delete functionality with proper API endpoint routing
- Set version history card z-index to 1 to resolve navigation overlap

#### June 14, 2025 Updates
- Updated `create_artwork_version` API to preserve old images in versions while updating artwork with new images
- Modified `ArtworkVersionRestoreView` to simply set selected version as current without creating new versions
- Ensured version records are never modified after creation, maintaining data integrity
- Updated UI terminology from "Restore" to "Set as Current" for clarity

## Changelog

```
Changelog:
- June 17, 2025. Comprehensive version history system enhancements with deletion, snapshots, and critique associations
- June 14, 2025. Initial setup and version management system fixes
```

## User Preferences

```
Preferred communication style: Simple, everyday language.
```