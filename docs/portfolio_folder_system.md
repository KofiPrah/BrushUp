# Portfolio Folder System Documentation

## Overview
The Portfolio Folder system allows artists to organize their artworks into themed collections, providing better portfolio management and presentation capabilities.

## Database Models

### Folder Model
```python
class Folder(models.Model):
    name = models.CharField(max_length=200)  # e.g., "Landscape Series"
    description = models.TextField(blank=True)  # Optional folder description
    owner = models.ForeignKey(User, related_name='folders')
    is_public = models.CharField(max_length=20, choices=VISIBILITY_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    cover_image = models.ImageField(upload_to='folder_covers/', blank=True, null=True)
    slug = models.SlugField(max_length=250, blank=True)  # Auto-generated URL slug
```

### Visibility Options
- **Public**: Visible to everyone in gallery and search results
- **Private**: Only visible to the folder owner
- **Unlisted**: Accessible via direct link but not in public listings

### ArtWork Model Updates
```python
class ArtWork(models.Model):
    # ... existing fields ...
    folder = models.ForeignKey(
        Folder,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='artworks'
    )
```

## Key Features

### 1. Portfolio Organization
- Artists can create multiple folders (e.g., "Abstract Works", "Portraits", "Digital Art")
- Each artwork can optionally belong to one folder
- Folders maintain unique slugs per user for clean URLs

### 2. Visibility Control
- Fine-grained privacy settings per folder
- Artists can showcase specific collections publicly while keeping others private
- Unlisted option for sharing with specific audiences

### 3. Auto-Generated Slugs
- URL-friendly slugs automatically created from folder names
- Ensures uniqueness per user with automatic numbering if needed
- Clean portfolio URLs: `/profile/username/folder/landscape-series/`

### 4. S3 Integration
- Cover images stored securely on AWS S3
- Seamless media management with existing artwork storage

## Database Schema
- **critique_folder**: Main portfolio folder table
- **critique_artwork.folder_id**: Foreign key linking artworks to folders
- Unique constraint: (owner, slug) ensures no duplicate folder slugs per user

## Migration Applied
✅ Migration `0014_add_folder_portfolio_model` successfully applied
- Created Folder model with all relationships
- Added folder_id field to ArtWork model
- Established proper foreign key constraints

## Usage Examples

### Creating a Portfolio Folder
```python
folder = Folder.objects.create(
    name="Digital Landscapes",
    description="My collection of digital landscape artworks",
    owner=user,
    is_public=Folder.VISIBILITY_PUBLIC
)
# Slug automatically generated: "digital-landscapes"
```

### Adding Artwork to Folder
```python
artwork = ArtWork.objects.create(
    title="Mountain Vista",
    description="Digital painting of mountain landscape",
    author=user,
    folder=folder  # Optional - can be None
)
```

### Querying Portfolio Contents
```python
# Get all artworks in a folder
folder_artworks = folder.artworks.all()

# Get artwork count
count = folder.artwork_count()

# Check visibility permissions
can_view = folder.is_viewable_by(current_user)
```

## Next Steps
- Create API endpoints for folder CRUD operations
- Build frontend portfolio management interface
- Add folder filtering to artwork gallery
- Implement portfolio sharing features