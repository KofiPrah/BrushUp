# Brush Up - Art Critique Platform

## Overview
Brush Up is a Django-powered web application designed for art professionals to share, critique, and engage with creative works digitally. It offers user authentication via Google OAuth, secure artwork uploads with S3 storage, a comprehensive critique system with reactions, and a karma point system to foster community contributions. The platform aims to facilitate innovative digital interactions within the art community, providing a robust environment for artistic exchange and feedback.

## User Preferences
Preferred communication style: Simple, everyday language.

## System Architecture

### Core Design Principles
The application is built on a robust Django backend with a RESTful API, complemented by Django templates and vanilla JavaScript for a responsive and dynamic frontend. Key architectural decisions include:
- **Scalable Media Storage**: Integration with AWS S3 for efficient and scalable handling of artwork uploads.
- **Secure Authentication**: Utilizing Google OAuth via Django Allauth for seamless and secure user access.
- **HTTP-Only Configuration**: Optimized for Replit's deployment environment, with SSL termination handled at the infrastructure level.
- **Progressive Disclosure**: Implementation of a multi-step upload wizard to streamline the artwork submission process, enhancing user experience.
- **Advanced Version Management**: A sophisticated system for artwork versioning, allowing history preservation, comparison, and restoration.
- **Dynamic Critique System**: Features multi-type reactions, karma points, and advanced filtering for community engagement and feedback.
- **Responsive UI/UX**: Designed with Bootstrap 5 for a consistent and adaptive user experience across various devices. Aesthetic choices include subtle shadows, consistent box shadows, enhanced action buttons, and color-coded rating systems.

### Technical Implementation Details
- **Backend Framework**: Django 5.0.2 with Django REST Framework.
- **Frontend Technologies**: Django templates, Bootstrap 5.3.6, Vanilla JavaScript (ES6+).
- **Database**: PostgreSQL 16.
- **Authentication**: Django Allauth with Google OAuth.
- **Server**: Gunicorn WSGI server.
- **Image Processing**: Pillow library for artwork manipulation.
- **Media Management**: AWS S3 integration for storage; pre-signed URLs for secure access.
- **API Design**: Comprehensive REST API endpoints for all core functionalities, using Django REST Framework serializers.
- **Deployment Strategy**: Configured for Replit Autoscale with specific Gunicorn settings for memory management and health monitoring.

### Key Features
- **Authentication**: Google OAuth, user profiles with karma tracking.
- **Artwork Management**: Multi-format file uploads, S3 storage, image processing, advanced version management with history preservation, comparison, and restoration.
- **Critique System**: Multi-type reactions (Helpful, Inspiring, Detailed), karma point system, real-time reaction counting, advanced filtering.
- **Multi-Step Upload Wizard**: A 6-step progressive disclosure wizard for image upload, details, medium/dimensions, tags/organization, critique settings, and review.
- **Enhanced Focus Mode**: Improved layout for artwork display, action bars, and interactive elements.
- **Visual Polish**: Consistent styling across the platform, including enhanced filter bars, critique card highlighting, and refined reaction count styling.
- **Achievement Badges**: Display of earned and in-progress achievement badges on user profiles.

## External Dependencies

### Python Packages
- `Django`
- `djangorestframework`
- `django-allauth`
- `django-cors-headers`
- `psycopg2-binary`
- `gunicorn`
- `boto3`
- `pillow`

### Frontend Dependencies
- `Bootstrap 5.3.6`
- `Bootstrap Icons 1.13.1`
- `Axios`

### Infrastructure Services
- `PostgreSQL 16`
- `AWS S3`
- `Replit Autoscale`