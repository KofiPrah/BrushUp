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

### July 03, 2025 - Multi-Step Upload Wizard Implementation ✓
- **Transformed upload experience**: Replaced single-form upload with sophisticated 6-step wizard using progressive disclosure
- **Step 1 - Image Upload**: Drag-and-drop interface with instant preview, file validation, and visual feedback
- **Step 2 - Details**: Enhanced title and description inputs with character counters and helpful prompts
- **Step 3 - Medium & Dimensions**: Interactive medium selection with common options and custom input capability
- **Step 4 - Tags & Organization**: Smart tag suggestions, folder selection, and portfolio organization tools
- **Step 5 - Critique Settings**: Toggle for seeking feedback with focus area selection for targeted critiques
- **Step 6 - Review & Submit**: Comprehensive summary with final validation before upload
- **Enhanced UX**: Progress indicator, smooth animations, step validation, and engaging copy throughout
- **API Integration**: Seamlessly integrates with existing `/api/artworks/` endpoint and folder management
- **Responsive Design**: Optimized for all device sizes with Bootstrap 5 components and custom styling
- **Error Handling**: Comprehensive validation, file type checking, size limits, and user-friendly error messages
- **Template Architecture**: Built using Django templates with vanilla JavaScript for maximum compatibility

### July 01, 2025 - Enhanced Focus Mode Implementation ✓
- **Fixed template syntax error**: Removed duplicate {% block content %} tags that were causing Django template errors
- **Resolved artwork disappearing issue**: Removed duplicate image block in main-content section that caused visual conflicts
- **Implemented seamless Focus Mode experience**: Updated layout to use min-height instead of fixed height for better flow preservation
- **Enhanced actions bar layout**: Redesigned cramped button positioning with modern pill-shaped bar featuring proper spacing and visual hierarchy
- **Restored custom heart button**: Implemented custom ♥ button with glassmorphism styling and pink hover effects
- **Added bounce animation**: Smooth actions bar entrance with bounceIn animation after 2-second delay
- **Improved button interactions**: Enhanced hover states with scale transforms and better touch targets for mobile
- **Added scroll-triggered reveals**: Implemented smooth transitions with Intersection Observer API for progressive content disclosure
- **Enhanced user interactions**: Added fullscreen toggle button and improved favorite functionality with visual feedback
- **Improved accessibility**: Added proper focus states, keyboard navigation support, and screen reader friendly elements
- **Optimized performance**: Reduced layout shifts and improved animation performance with CSS transforms

### July 01, 2025 - Artwork Detail Page Visual Enhancement Implementation ✓
- **Enhanced artwork prominence**: Improved shadows, borders, and visual hierarchy to make artworks more prominent
- **Upgraded metadata section**: Better spacing and refined layout structure for artwork information
- **Implemented enhanced action buttons**: Improved dropdown styling and button interactions
- **Added color-coded rating system**: Visual progress indicators with icons for critique rating sections
- **Enhanced version history layout**: Added version-history-card class and improved spacing
- **Implemented enhanced critique sorting controls**: Comprehensive sorting with icons, filtering by ratings, and compact view toggle
- **Added visual progress indicators**: Color-coded rating bars with different visual states (excellent, good, average, poor)
- **Created sophisticated critique controls**: Gradient backgrounds, enhanced dropdowns with icons, and real-time filtering
- **Added smooth animations**: Critique sorting with staggered animations and visual feedback
- **Integrated toast notifications**: User feedback for all sorting and filtering actions

### July 01, 2025 - Visual Refinement Polish Implementation ✓
- **Artwork Info Sidebar Enhancement**: Added subtle vertical rule border and improved metadata spacing with `.mb-1` classes
- **Call-to-Action Area**: Implemented unified CTA container with soft background and responsive full-width buttons on mobile
- **Version History Sticky Sidebar**: Added sticky positioning for version history on large screens (top: 80px)
- **Enhanced Version Thumbnails**: Implemented hover states with purple outline and transform effects
- **Critique Card Polish**: Added consistent box shadows (0 1px 3px rgba(0,0,0,0.15)) and improved hover states
- **Reaction Button Enhancement**: Improved spacing with gap-3, enhanced hover feedback with scale and glow effects
- **Rating Section Styling**: Added subtle dividers and improved label typography with uppercase styling
- **Visual Consistency**: Applied consistent shadows across all cards and components for professional appearance
- **Tooltip Integration**: Added Bootstrap tooltip initialization for improved user experience on interactive elements

### July 01, 2025 - Pro-Grade Final Polish Implementation ✓
- **Enhanced Filter Bar**: Added subtle background (rgba(255,255,255,0.02)) with border radius and filter icon integration
- **Critique Card Left Border Accent**: Implemented dynamic left border (4px solid primary) on hover for visual pull
- **Highly Rated Critique Highlighting**: Automatic green left border and gradient background for critiques with 8+ average rating
- **Refined Reaction Count Styling**: Reduced contrast on reaction badges for better visual balance
- **Enhanced Add Critique Button**: Gradient background with hover state flip to outline style with plus-circle icon
- **Artwork Meta Section Labels**: Added uppercase styling for section headers with proper spacing and typography
- **Automatic Rating Detection**: JavaScript function to identify and highlight high-scoring critiques automatically
- **Professional Visual Hierarchy**: Complete implementation of pro-grade design patterns and interactions

### July 01, 2025 - Achievement Badges Frontend Display Implementation ✓
- **Added achievement badges section**: Created comprehensive badges display on user profile pages
- **Improved visual design**: Enhanced badge cards with proper spacing, shadows, and color-coded progress bars
- **Public badge viewing**: Updated API permissions to allow viewing badges on any user's profile
- **Progress tracking**: Display shows both earned badges and progress toward next achievements
- **Responsive layout**: Badges display optimally on different screen sizes with proper gap spacing
- **Category organization**: Badges sorted by progress percentage with visual hierarchy improvements

### June 28, 2025 - OAuth Password Management System Implementation ✓
- **Fixed import issues**: Added missing CommentForm and ReplyForm to forms.py to resolve 500 errors
- **Implemented OAuth password management**: Created comprehensive password management system for Google OAuth users
- **Fixed authentication backend error**: Resolved ValueError when setting passwords by specifying explicit backend
- **Enhanced form visibility**: Fixed missing form fields in password management interface
- **Applied dark theme styling**: Ensured all password management forms follow consistent dark background theme
- **Integrated security features**: Users can now set, change, or remove passwords while maintaining OAuth functionality
- **Fixed version deletion 405 error**: Updated API endpoint to handle DELETE requests for artwork version removal
- **Implemented dynamic version renumbering**: Versions are now automatically renumbered sequentially after deletion to maintain v1, v2, v3 ordering

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