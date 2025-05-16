import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { getValidImageUrl, handleImageError } from '../utils/imageUtils';
import PlaceholderImage from '../components/PlaceholderImage';
import { artworkAPI } from '../services/api';

const ArtworkList = () => {
  const [artworks, setArtworks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    search: '',
    sortBy: 'newest'
  });
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);

  const fetchArtworks = async () => {
    try {
      setLoading(true);
      
      const params = {
        page: page,
        search: filters.search || undefined
      };
      
      // Map frontend sorting options to backend ordering parameters
      switch (filters.sortBy) {
        case 'newest':
          params.ordering = '-created_at';
          break;
        case 'oldest':
          params.ordering = 'created_at';
          break;
        case 'most_liked':
          params.ordering = '-likes_count';
          break;
        case 'most_critiqued':
          params.ordering = '-critiques_count';
          break;
        default:
          params.ordering = '-created_at';
      }
      
      const response = await artworkAPI.getArtworks(params);
      
      const { results, next } = response.data;
      
      // Update artworks state (append on pagination, replace on filter change)
      setArtworks(page === 1 ? results : [...artworks, ...results]);
      
      // Determine if there are more pages to load
      setHasMore(!!next);
      setError(null);
    } catch (err) {
      console.error('Error fetching artworks:', err);
      setError('Failed to load artworks. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  // Fetch artworks when filters change (reset to page 1)
  useEffect(() => {
    setPage(1);
    fetchArtworks();
  }, [filters]);
  
  // Fetch artworks when page changes (pagination)
  useEffect(() => {
    if (page > 1) {
      fetchArtworks();
    }
  }, [page]);

  const handleSearchChange = (e) => {
    setFilters({
      ...filters,
      search: e.target.value
    });
  };

  const handleSortChange = (e) => {
    setFilters({
      ...filters,
      sortBy: e.target.value
    });
  };

  const loadMoreArtworks = () => {
    if (hasMore && !loading) {
      setPage(prevPage => prevPage + 1);
    }
  };

  if (loading && artworks.length === 0) {
    return (
      <div className="container mt-5 text-center">
        <div className="spinner-border" role="status">
          <span className="visually-hidden">Loading...</span>
        </div>
        <p className="mt-3">Loading artworks...</p>
      </div>
    );
  }

  if (error && artworks.length === 0) {
    return (
      <div className="container mt-5">
        <div className="alert alert-danger" role="alert">
          Error loading artworks: {error}
        </div>
      </div>
    );
  }

  return (
    <div className="container mt-4">
      <h1 className="mb-4">Artwork Gallery</h1>
      
      {/* Search and Filter Controls */}
      <div className="row mb-4">
        <div className="col-md-6">
          <div className="input-group">
            <input
              type="text"
              className="form-control"
              placeholder="Search artworks..."
              value={filters.search}
              onChange={handleSearchChange}
            />
            <button className="btn btn-primary" type="button">Search</button>
          </div>
        </div>
        <div className="col-md-6">
          <div className="d-flex justify-content-end align-items-center">
            <label className="me-2">Sort by:</label>
            <select 
              className="form-select w-auto" 
              value={filters.sortBy}
              onChange={handleSortChange}
            >
              <option value="newest">Newest</option>
              <option value="oldest">Oldest</option>
              <option value="most_liked">Most Liked</option>
              <option value="most_critiqued">Most Critiqued</option>
            </select>
          </div>
        </div>
      </div>
      
      {/* Artwork Gallery */}
      <div className="row">
        {artworks.length === 0 ? (
          <div className="col-12 text-center my-5">
            <p className="lead">No artworks found matching your criteria.</p>
          </div>
        ) : (
          <>
            {artworks.map(artwork => (
              <div className="col-md-4 mb-4" key={artwork.id}>
                <div className="card h-100">
                  {artwork.image_display_url ? (
                    <div className="card-img-container" style={{ height: '200px', position: 'relative' }}>
                      <img 
                        src={getValidImageUrl(artwork.image_display_url)} 
                        className="card-img-top" 
                        alt={artwork.title} 
                        style={{ height: '200px', objectFit: 'cover', width: '100%' }}
                        onError={handleImageError}
                      />
                    </div>
                  ) : (
                    <PlaceholderImage 
                      alt={`${artwork.title} (image unavailable)`}
                      className="card-img-top"
                      style={{ height: '200px' }}
                      aspectRatio="16:9"
                    />
                  )}
                  <div className="card-body">
                    <h5 className="card-title">{artwork.title}</h5>
                    <h6 className="card-subtitle mb-2 text-muted">
                      by {artwork.author.username}
                    </h6>
                    <p className="card-text">
                      {artwork.description?.length > 100
                        ? `${artwork.description.substring(0, 100)}...`
                        : artwork.description}
                    </p>
                  </div>
                  <div className="card-footer d-flex justify-content-between align-items-center">
                    <small className="text-muted">
                      <span className="me-2">
                        <i className="bi bi-heart-fill text-danger me-1"></i> 
                        {artwork.likes_count}
                      </span>
                      <span>
                        <i className="bi bi-chat-text-fill me-1"></i> 
                        {artwork.critiques_count}
                      </span>
                    </small>
                    <Link to={`/artworks/${artwork.id}`} className="btn btn-sm btn-outline-primary">
                      View Details
                    </Link>
                  </div>
                </div>
              </div>
            ))}
            
            {/* Loading indicator and Load More button */}
            <div className="col-12 text-center my-4">
              {loading && (
                <div className="mb-3">
                  <div className="spinner-border spinner-border-sm" role="status">
                    <span className="visually-hidden">Loading...</span>
                  </div>
                  <span className="ms-2">Loading more artworks...</span>
                </div>
              )}
              
              {hasMore && !loading && (
                <button 
                  className="btn btn-primary" 
                  onClick={loadMoreArtworks}
                >
                  Load More Artworks
                </button>
              )}
              
              {!hasMore && artworks.length > 0 && (
                <p className="text-muted">No more artworks to load.</p>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default ArtworkList;