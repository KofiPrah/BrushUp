# Popularity-Based Filtering Implementation Guide

## Overview

The Brush Up application now supports comprehensive popularity-based filtering and sorting for artworks on both the Gallery Page and Profile Page. This feature allows users to discover the most engaging content based on community interaction.

## Popularity Score Calculation

The popularity score is calculated using the following formula:
```
popularity_score = (critiques_count × 2) + likes_count + reactions_count
```

This weighted approach prioritizes:
- **Critiques (2x weight)**: Detailed feedback is most valuable
- **Likes (1x weight)**: Basic appreciation
- **Reactions (1x weight)**: Specific feedback on critiques

## Available Sorting Options

### Django Template Gallery (/artworks/)
- 📅 **Newest First** (`-created_at`)
- 📅 **Oldest First** (`created_at`)
- 🔥 **Most Popular** (`-popularity_score`)
- ❤️ **Most Liked** (`-likes_count`)
- 💬 **Most Critiques** (`-critiques_count`)
- 🔤 **Title A-Z** (`title`)
- 🔤 **Title Z-A** (`-title`)

### API Endpoints

#### Gallery API
```
GET /api/artworks/?ordering=-popularity_score
GET /api/artworks/?ordering=-likes_count
GET /api/artworks/?ordering=-critiques_count
```

#### Profile/My Artworks API
```
GET /api/profiles/{user_id}/artworks/?ordering=-popularity_score
```

## Implementation Details

### Backend Annotations
Both views use Django's `annotate()` method to calculate:
- `critiques_count`: Number of critiques per artwork
- `likes_count`: Number of likes per artwork  
- `popularity_score`: Weighted calculation of engagement

### Example Queries

#### Most Popular Artworks
```python
# Django ORM
ArtWork.objects.annotate(
    critiques_count=Count('critique', distinct=True),
    likes_count=Count('likes', distinct=True),
    popularity_score=Count('critique', distinct=True) * 2 + 
                   Count('likes', distinct=True) + 
                   Count('critique__reaction', distinct=True)
).order_by('-popularity_score')
```

#### API Usage Examples
```bash
# Get most popular artworks
curl "https://your-app.replit.app/api/artworks/?ordering=-popularity_score"

# Get most liked artworks with pagination
curl "https://your-app.replit.app/api/artworks/?ordering=-likes_count&page=1&page_size=12"

# Combined search and popularity filtering
curl "https://your-app.replit.app/api/artworks/?search=landscape&ordering=-popularity_score"

# Filter by artist and sort by critiques
curl "https://your-app.replit.app/api/artworks/?author__username=artist_name&ordering=-critiques_count"
```

## Frontend Integration

### React Gallery Component
The React frontend supports these parameters:
```javascript
// Sort by popularity
const response = await api.get('/api/artworks/', {
  params: { ordering: '-popularity_score' }
});

// Combined filtering
const response = await api.get('/api/artworks/', {
  params: { 
    ordering: '-popularity_score',
    search: 'portrait',
    author__username: 'artist_name'
  }
});
```

### Django Template Forms
The template includes a select dropdown that automatically submits:
```html
<select name="ordering" onchange="this.form.submit()">
  <option value="-popularity_score">🔥 Most Popular</option>
  <option value="-likes_count">❤️ Most Liked</option>
  <option value="-critiques_count">💬 Most Critiques</option>
</select>
```

## Performance Considerations

- Annotations are computed at query time
- Use `distinct=True` to avoid duplicate counts from JOINs
- Consider database indexing on `created_at`, `likes` relationship, and `critique` relationship for large datasets
- Pagination is implemented to handle large result sets efficiently

## Testing Examples

### High Popularity Artwork
An artwork with:
- 5 critiques = 10 points
- 8 likes = 8 points  
- 12 critique reactions = 12 points
- **Total popularity score: 30**

### Medium Popularity Artwork
An artwork with:
- 2 critiques = 4 points
- 5 likes = 5 points
- 3 critique reactions = 3 points
- **Total popularity score: 12**

This ensures that artworks with meaningful engagement (critiques and discussions) rank higher than those with just likes.