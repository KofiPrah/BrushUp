# Frontend Folder Management UI Guide

## Overview
This guide demonstrates how to integrate the complete folder management UI components into your React application, providing artists with professional portfolio organization tools.

## Component Architecture

### 1. ProfilePage Component
**Location:** `frontend/artcritique-frontend/src/components/ProfilePage.jsx`

**Features:**
- 📁 **Folder Management** - Create, edit, delete portfolio folders
- 🎨 **Artwork Organization** - View artworks grouped by folders
- 🔒 **Privacy Controls** - Manage folder visibility (Public/Private/Unlisted)
- 👥 **User Permissions** - Different views for own vs. others' profiles
- 📱 **Responsive Design** - Works on all device sizes

**Usage:**
```jsx
import ProfilePage from './components/ProfilePage';

// In your Router
<Route path="/profile/:username" element={<ProfilePage />} />

// The component automatically:
// 1. Detects if viewing own profile vs others
// 2. Fetches appropriate folders based on permissions
// 3. Groups artworks by folders with expand/collapse
// 4. Shows folder management controls for owners
```

### 2. ArtworkForm Component
**Location:** `frontend/artcritique-frontend/src/components/ArtworkForm.jsx`

**Features:**
- 📂 **Folder Selection** - Dropdown of user's folders during upload/edit
- ➕ **Quick Folder Creation** - Create new folders without leaving the form
- 🖼️ **Image Upload** - File validation and preview
- 🏷️ **Metadata Entry** - Title, description, medium, dimensions, tags
- ✅ **Validation** - Client-side form validation with error handling

**Usage:**
```jsx
import ArtworkForm from './components/ArtworkForm';

// For creating new artwork
<Route path="/upload" element={<ArtworkForm mode="create" />} />

// For editing existing artwork
<Route path="/artwork/:id/edit" element={<ArtworkForm mode="edit" />} />

// Features automatically included:
// - Fetches user's folders for dropdown
// - Validates folder ownership
// - Allows creating folders on-the-fly
// - Handles image upload with preview
```

### 3. FolderGallery Component
**Location:** `frontend/artcritique-frontend/src/components/FolderGallery.jsx`

**Features:**
- 📋 **Multiple Views** - Folder view vs. grid view toggle
- 🔍 **Search & Filter** - Search across folders and artworks
- 👁️ **Privacy Respect** - Shows only accessible content
- 🗂️ **Folder Expansion** - Click to expand/collapse folder contents
- 🏷️ **Visual Indicators** - Folder privacy icons and artwork counts

**Usage:**
```jsx
import FolderGallery from './components/FolderGallery';

// For user's own profile (shows private folders)
<FolderGallery 
  userId={currentUser.id} 
  username={currentUser.username} 
  showPrivate={true} 
/>

// For viewing others' profiles (public only)
<FolderGallery 
  userId={profileUser.id} 
  username={profileUser.username} 
  showPrivate={false} 
/>

// For main gallery page (all public content)
<FolderGallery />
```

## Integration Examples

### Complete Profile Page Integration
```jsx
// App.jsx or main router file
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import ProfilePage from './components/ProfilePage';
import ArtworkForm from './components/ArtworkForm';
import FolderGallery from './components/FolderGallery';

function App() {
  return (
    <Router>
      <Routes>
        {/* Profile pages with folder management */}
        <Route path="/profile/:username" element={<ProfilePage />} />
        
        {/* Artwork upload/edit with folder selection */}
        <Route path="/upload" element={<ArtworkForm mode="create" />} />
        <Route path="/artwork/:id/edit" element={<ArtworkForm mode="edit" />} />
        
        {/* Gallery with folder organization */}
        <Route path="/gallery" element={<FolderGallery />} />
        
        {/* Individual folder view */}
        <Route path="/profile/:username/folder/:slug" element={<FolderDetailPage />} />
      </Routes>
    </Router>
  );
}
```

### Navigation Menu Integration
```jsx
// Navigation.jsx
import { Link } from 'react-router-dom';
import { User, Upload, Grid, Folder } from 'lucide-react';

const Navigation = ({ currentUser }) => {
  return (
    <nav className="navbar navbar-expand-lg navbar-dark bg-dark">
      <div className="container">
        <Link className="navbar-brand" to="/">Art Critique</Link>
        
        <div className="navbar-nav ms-auto">
          {currentUser ? (
            <>
              <Link className="nav-link" to="/gallery">
                <Grid className="w-4 h-4 me-1" />
                Gallery
              </Link>
              <Link className="nav-link" to="/upload">
                <Upload className="w-4 h-4 me-1" />
                Upload
              </Link>
              <Link className="nav-link" to={`/profile/${currentUser.username}`}>
                <User className="w-4 h-4 me-1" />
                My Portfolio
              </Link>
            </>
          ) : (
            <Link className="nav-link" to="/login">Login</Link>
          )}
        </div>
      </div>
    </nav>
  );
};
```

## User Workflow Examples

### 1. Artist Creating Portfolio
```javascript
// Step-by-step user journey

// 1. Artist visits their profile
// URL: /profile/artist123
// - Sees "Create Folder" button
// - Views any existing folders and unorganized artworks

// 2. Creates themed folders
// - Clicks "Create Folder"
// - Fills form: name="Landscape Series", visibility="public"
// - Repeats for other themes: "Portraits", "Abstract Work"

// 3. Uploads artwork with folder assignment
// URL: /upload
// - Selects image, fills metadata
// - Chooses folder from dropdown: "Landscape Series"
// - Can create new folder if needed without leaving form

// 4. Organizes existing artwork
// - Returns to profile to see organized portfolio
// - Can move artworks between folders via edit form
// - Folders show artwork counts and descriptions
```

### 2. Visitor Browsing Art
```javascript
// Visitor experience

// 1. Discovers artist profile
// URL: /profile/artist123
// - Sees public folders only
// - Can expand folders to view contents
// - No edit controls visible

// 2. Explores gallery
// URL: /gallery
// - Views all public artworks
// - Can toggle between folder view and grid view
// - Search works across all content
// - Folder badges show artwork organization

// 3. Folder-specific browsing
// URL: /profile/artist123/folder/landscape-series
// - Deep-dive into specific collection
// - See artist's curation and theming
```

## Advanced Features

### Folder Privacy System
```jsx
// Three visibility levels with automatic enforcement

// PUBLIC - Everyone can see
{
  is_public: "public",
  icon: <Globe className="text-green-600" />,
  description: "Visible to everyone"
}

// UNLISTED - Only people with direct link
{
  is_public: "unlisted", 
  icon: <EyeOff className="text-yellow-600" />,
  description: "Hidden from public listings"
}

// PRIVATE - Only folder owner
{
  is_public: "private",
  icon: <Lock className="text-red-600" />,
  description: "Only visible to you"
}
```

### Search and Filtering
```jsx
// Multi-faceted search functionality

const searchFeatures = {
  // Search across multiple fields
  targets: ['folder.name', 'folder.description', 'artwork.title', 'artwork.tags'],
  
  // Visibility filtering (for own profile)
  filters: ['all', 'public', 'unlisted', 'private'],
  
  // View mode switching
  modes: ['folders', 'grid'],
  
  // Real-time results
  debounced: true
};
```

### Responsive Design
```jsx
// Bootstrap responsive classes for different screens

const responsiveLayout = {
  // Folder cards: full width on mobile, adaptive on larger screens
  folders: "col-12",
  
  // Artwork grid: responsive breakpoints
  artworks: {
    mobile: "col-6",      // 2 per row
    tablet: "col-sm-4",   // 3 per row  
    desktop: "col-md-3",  // 4 per row
    large: "col-xl-2"     // 6 per row
  },
  
  // Navigation: collapsible on mobile
  nav: "navbar-expand-lg"
};
```

## Error Handling

### Graceful Fallbacks
```jsx
// Network error handling
const errorStates = {
  loading: <LoadingSpinner />,
  networkError: <RetryButton onRetry={fetchData} />,
  unauthorized: <LoginPrompt />,
  notFound: <EmptyState message="No artworks found" />,
  folderEmpty: <EmptyFolderMessage />
};

// Form validation
const validation = {
  folderName: "Required, max 100 characters",
  artworkTitle: "Required, max 200 characters", 
  imageFile: "JPG/PNG/GIF, max 5MB",
  folderOwnership: "Can only assign to your own folders"
};
```

This comprehensive folder management system transforms your art platform into a professional portfolio showcase, giving artists powerful organization tools while maintaining clean, intuitive user experiences for all visitors!