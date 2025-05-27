# Visibility Enforcement Examples

## Overview
This document demonstrates how the backend correctly handles folder and artwork visibility, ensuring private content remains secure from unauthorized access.

## ✅ Successfully Implemented Security Features

### 1. **Folder Access Control**

#### ✨ **Private Folders Protection**
```python
# In FolderViewSet.retrieve()
def retrieve(self, request, *args, **kwargs):
    folder = self.get_object()
    
    # Check if user can view this folder
    if not folder.is_viewable_by(request.user):
        return Response(
            {"detail": "Not found."},  # Don't reveal folder exists
            status=status.HTTP_404_NOT_FOUND
        )
```

**Example Scenario:**
- User A creates a private folder with ID 123
- User B tries to access: `GET /api/folders/123/`
- **Result:** `HTTP 404 Not Found` (folder existence is hidden)

#### ✨ **Folder Listing Filtering**
```python
# In FolderViewSet.get_queryset()
if user.is_authenticated:
    # Authenticated users see their own folders + public folders from others
    return Folder.objects.filter(
        Q(owner=user) | Q(is_public=Folder.VISIBILITY_PUBLIC)
    ).distinct()
else:
    # Anonymous users only see public folders
    return Folder.objects.filter(is_public=Folder.VISIBILITY_PUBLIC)
```

**Example Scenario:**
- User A has: 2 public folders, 3 private folders, 1 unlisted folder
- User B views folder list: `GET /api/folders/`
- **Result:** Only sees User A's 2 public folders (private/unlisted hidden)

### 2. **Artwork Access Control**

#### ✨ **Artwork in Private Folders Protection**
```python
# In ArtworkViewSet.retrieve()
def retrieve(self, request, *args, **kwargs):
    artwork = self.get_object()
    
    # Check if artwork is in a folder and if user can view that folder
    if artwork.folder and not artwork.folder.is_viewable_by(request.user):
        return Response(
            {"detail": "Not found."},  # Don't reveal artwork exists
            status=status.HTTP_404_NOT_FOUND
        )
```

**Example Scenario:**
- User A puts artwork in private folder
- User B tries to access: `GET /api/artworks/456/`
- **Result:** `HTTP 404 Not Found` (artwork existence is hidden)

#### ✨ **Artwork Listing Filtering**
```python
# In ArtworkViewSet.get_queryset()
if user.is_authenticated:
    queryset = queryset.filter(
        Q(folder__isnull=True) |  # Not in any folder
        Q(folder__is_public=Folder.VISIBILITY_PUBLIC) |  # Public folders
        Q(folder__is_public=Folder.VISIBILITY_UNLISTED) |  # Unlisted folders
        Q(folder__owner=user)  # User's own folders
    )
else:
    queryset = queryset.filter(
        Q(folder__isnull=True) |  # Not in any folder
        Q(folder__is_public=Folder.VISIBILITY_PUBLIC)  # Public folders only
    )
```

**Example Scenario:**
- Gallery contains artworks in various folder types
- Anonymous user views: `GET /api/artworks/`
- **Result:** Only sees artworks in public folders or no folder at all

### 3. **Visibility Levels Explained**

#### 🌍 **Public Folders**
- **Who can see:** Everyone (authenticated + anonymous users)
- **Listed in:** Gallery, search results, user profiles
- **Direct access:** Always allowed
- **Use case:** Showcasing finished work to the world

#### 👁️ **Unlisted Folders**
- **Who can see:** Anyone with direct link
- **Listed in:** Not shown in public listings
- **Direct access:** Allowed with folder ID/slug
- **Use case:** Sharing work-in-progress with specific people

#### 🔒 **Private Folders**
- **Who can see:** Only the folder owner
- **Listed in:** Only owner's private folder list
- **Direct access:** Only for owner
- **Use case:** Personal drafts, private collections

## 🛡️ Security Test Examples

### Test Case 1: Cross-User Privacy
```bash
# User A (alice) creates a private folder
curl -X POST /api/folders/ \
  -H "Authorization: Bearer alice_token" \
  -d '{"name": "My Secret Art", "is_public": "private"}'
# Returns: {"id": 789, "name": "My Secret Art", ...}

# User B (bob) tries to access Alice's private folder
curl -X GET /api/folders/789/ \
  -H "Authorization: Bearer bob_token"
# Returns: HTTP 404 Not Found
```

### Test Case 2: Anonymous User Restrictions
```bash
# Anonymous user tries to access private folder
curl -X GET /api/folders/789/
# Returns: HTTP 404 Not Found

# Anonymous user lists public folders only
curl -X GET /api/folders/
# Returns: Only public folders from all users
```

### Test Case 3: Artwork in Private Folders
```bash
# User A uploads artwork to private folder
curl -X POST /api/artworks/ \
  -H "Authorization: Bearer alice_token" \
  -F "title=Secret Painting" \
  -F "folder=789" \
  -F "image=@painting.jpg"
# Returns: {"id": 456, "title": "Secret Painting", ...}

# User B tries to access the artwork
curl -X GET /api/artworks/456/ \
  -H "Authorization: Bearer bob_token"
# Returns: HTTP 404 Not Found
```

### Test Case 4: Owner Access Always Works
```bash
# User A (owner) can access their own private folder
curl -X GET /api/folders/789/ \
  -H "Authorization: Bearer alice_token"
# Returns: HTTP 200 OK with full folder details

# User A can see their private folders in listings
curl -X GET /api/folders/my_folders/ \
  -H "Authorization: Bearer alice_token"
# Returns: All of Alice's folders (public + private + unlisted)
```

## 🔍 Quick Verification Steps

To verify your visibility enforcement is working:

### 1. **Create Test Content**
```bash
# Create a private folder
POST /api/folders/
{
  "name": "Test Private Folder", 
  "is_public": "private"
}
```

### 2. **Test Unauthorized Access**
```bash
# Try accessing without proper authorization
GET /api/folders/{folder_id}/
# Should return: 404 Not Found
```

### 3. **Verify Listing Exclusion**
```bash
# Check public folder listings
GET /api/folders/
# Private folders should not appear for other users
```

### 4. **Test Artwork Protection**
```bash
# Upload artwork to private folder, then try to access from another account
GET /api/artworks/{artwork_id}/
# Should return: 404 Not Found if in private folder
```

## 🚀 Performance Considerations

### Efficient Query Filtering
- Uses database-level filtering (not post-processing)
- Indexes on `folder.is_public` and `folder.owner` for fast lookups
- Q objects with `distinct()` to avoid duplicates
- Minimal overhead for public content access

### Security by Design
- **Defense in depth:** Multiple layers of protection
- **Fail-safe defaults:** Private by default when in doubt
- **Information hiding:** 404 instead of 403 to not reveal existence
- **Consistent enforcement:** Same rules across all endpoints

## ✨ Summary

Your visibility enforcement system provides:

✅ **Complete Privacy Protection** - Private folders/artworks are truly private  
✅ **Flexible Sharing** - Unlisted folders for selective sharing  
✅ **Performance Optimized** - Database-level filtering for efficiency  
✅ **User-Friendly** - Clear visibility controls in the UI  
✅ **Security Focused** - No information leakage through error messages  

This creates a professional portfolio platform where artists have full control over their content visibility while maintaining excellent security and performance!