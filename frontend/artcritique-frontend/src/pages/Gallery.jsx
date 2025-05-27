import React, { useState, useEffect, useCallback } from 'react';
import { Container, Row, Col, Card, Form, InputGroup, Button, Spinner, Alert, Badge, Dropdown } from 'react-bootstrap';
import { Search, Filter, SortAlphaDown, SortAlphaUp, Heart, MessageCircle } from 'react-bootstrap-icons';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';
import '../styles/Gallery.css';

const Gallery = () => {
  const { user } = useAuth();
  const [artworks, setArtworks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filters, setFilters] = useState({
    author__username: '',
    medium: '',
    tags: '',
    created_after: '',
    created_before: '',
    min_likes: '',
    min_critiques: '',
    ordering: '-created_at'
  });
  const [showFilters, setShowFilters] = useState(false);
  const [pagination, setPagination] = useState({
    count: 0,
    next: null,
    previous: null,
    current_page: 1,
    total_pages: 1,
    has_next: false,
    has_previous: false
  });
  
  // Infinite scroll state
  const [loadingMore, setLoadingMore] = useState(false);
  const [allArtworks, setAllArtworks] = useState([]); // For infinite scroll: accumulate all loaded artworks

  // Enhanced search state
  const [debouncedSearchTerm, setDebouncedSearchTerm] = useState('');
  const [searchSuggestions, setSearchSuggestions] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [recentSearches, setRecentSearches] = useState([]);
  const [popularTags, setPopularTags] = useState([]);
  const [searchHistory, setSearchHistory] = useState([]);

  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearchTerm(searchTerm);
    }, 500);

    return () => clearTimeout(timer);
  }, [searchTerm]);

  // Fetch artworks from API
  const fetchArtworks = useCallback(async (page = 1, append = false) => {
    if (append) {
      setLoadingMore(true);
    } else {
      setLoading(true);
      setAllArtworks([]); // Reset for new search/filter
    }
    setError(null);

    try {
      const params = new URLSearchParams();
      
      // Add search term
      if (debouncedSearchTerm.trim()) {
        params.append('search', debouncedSearchTerm.trim());
      }

      // Add filters
      Object.entries(filters).forEach(([key, value]) => {
        if (value && value.toString().trim()) {
          params.append(key, value.toString().trim());
        }
      });

      // Add pagination
      params.append('page', page.toString());

      const response = await api.get(`/api/artworks/?${params.toString()}`);
      
      const newArtworks = response.data.results || [];
      
      if (append) {
        // For "Load More" - append to existing artworks
        setArtworks(prev => [...prev, ...newArtworks]);
        setAllArtworks(prev => [...prev, ...newArtworks]);
      } else {
        // For new search/filter - replace artworks
        setArtworks(newArtworks);
        setAllArtworks(newArtworks);
      }
      
      setPagination({
        count: response.data.count || 0,
        total_pages: response.data.total_pages || 1,
        next: response.data.next,
        previous: response.data.previous,
        current_page: page,
        has_next: response.data.has_next || false,
        has_previous: response.data.has_previous || false
      });
    } catch (err) {
      console.error('Error fetching artworks:', err);
      setError('Failed to load artworks. Please try again.');
    } finally {
      setLoading(false);
      setLoadingMore(false);
    }
  }, [debouncedSearchTerm, filters]);

  // Fetch artworks when search term or filters change
  useEffect(() => {
    fetchArtworks(1);
  }, [fetchArtworks]);

  // Load search enhancements on component mount
  useEffect(() => {
    loadRecentSearches();
    fetchPopularTags();
  }, []);

  // Load recent searches from localStorage
  const loadRecentSearches = () => {
    try {
      const stored = localStorage.getItem('artworkSearchHistory');
      if (stored) {
        setRecentSearches(JSON.parse(stored).slice(0, 5)); // Keep only 5 most recent
      }
    } catch (error) {
      console.error('Error loading search history:', error);
    }
  };

  // Save search to history
  const saveSearchToHistory = (searchTerm) => {
    if (!searchTerm.trim()) return;
    
    try {
      const existing = JSON.parse(localStorage.getItem('artworkSearchHistory') || '[]');
      const updated = [searchTerm, ...existing.filter(term => term !== searchTerm)].slice(0, 10);
      localStorage.setItem('artworkSearchHistory', JSON.stringify(updated));
      setRecentSearches(updated.slice(0, 5));
    } catch (error) {
      console.error('Error saving search history:', error);
    }
  };

  // Fetch popular tags from API
  const fetchPopularTags = async () => {
    try {
      const response = await api.get('/api/artworks/by_tag/');
      // Extract unique tags from artworks (this would be better with a dedicated endpoint)
      const tags = ['landscape', 'portrait', 'abstract', 'digital', 'traditional', 'nature', 'urban', 'fantasy'];
      setPopularTags(tags);
    } catch (error) {
      console.error('Error fetching popular tags:', error);
      // Fallback to common tags
      setPopularTags(['landscape', 'portrait', 'abstract', 'digital', 'traditional']);
    }
  };

  // Generate search suggestions based on input
  const generateSearchSuggestions = useCallback(async (query) => {
    if (query.length < 2) {
      setSearchSuggestions([]);
      return;
    }

    try {
      // In a real implementation, this would be a dedicated autocomplete API
      const suggestions = [];
      
      // Add matching popular tags
      const matchingTags = popularTags.filter(tag => 
        tag.toLowerCase().includes(query.toLowerCase())
      ).map(tag => ({ type: 'tag', value: tag, label: `Tag: ${tag}` }));
      
      // Add recent searches that match
      const matchingRecent = recentSearches.filter(search => 
        search.toLowerCase().includes(query.toLowerCase())
      ).map(search => ({ type: 'recent', value: search, label: `Recent: ${search}` }));

      // Combine suggestions
      suggestions.push(...matchingTags.slice(0, 3));
      suggestions.push(...matchingRecent.slice(0, 2));

      setSearchSuggestions(suggestions.slice(0, 5));
    } catch (error) {
      console.error('Error generating suggestions:', error);
    }
  }, [popularTags, recentSearches]);

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({
      ...prev,
      [key]: value
    }));
  };

  const clearFilters = () => {
    setFilters({
      author__username: '',
      medium: '',
      tags: '',
      created_after: '',
      created_before: '',
      min_likes: '',
      min_critiques: '',
      ordering: '-created_at'
    });
    setSearchTerm('');
  };

  const handlePageChange = (page) => {
    fetchArtworks(page);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  // Load more functionality for infinite scroll
  const handleLoadMore = () => {
    if (pagination.has_next && !loadingMore) {
      fetchArtworks(pagination.current_page + 1, true);
    }
  };

  // Infinite scroll detection
  useEffect(() => {
    const handleScroll = () => {
      if (
        window.innerHeight + document.documentElement.scrollTop
        >= document.documentElement.offsetHeight - 1000 // Load when 1000px from bottom
        && pagination.has_next
        && !loading
        && !loadingMore
      ) {
        handleLoadMore();
      }
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, [pagination.has_next, loading, loadingMore, pagination.current_page]);

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString();
  };

  const getTotalPages = () => {
    return pagination.total_pages || Math.ceil(pagination.count / 12);
  };

  return (
    <Container className="py-4">
      {/* Header */}
      <Row className="mb-4">
        <Col>
          <h1 className="display-6 mb-3">Artwork Gallery</h1>
          <p className="text-muted">
            Discover amazing artworks from our community of talented artists
          </p>
        </Col>
      </Row>

      {/* Search and Filter Controls */}
      <Row className="mb-4">
        <Col>
          <Card className="border-0 shadow-sm">
            <Card.Body>
              {/* Enhanced Search Bar */}
              <Row className="mb-3">
                <Col md={8}>
                  <div className="position-relative">
                    <InputGroup>
                      <InputGroup.Text>
                        <Search />
                      </InputGroup.Text>
                      <Form.Control
                        type="text"
                        placeholder="Search artworks by title, description, tags, or artist..."
                        value={searchTerm}
                        onChange={(e) => {
                          setSearchTerm(e.target.value);
                          generateSearchSuggestions(e.target.value);
                          setShowSuggestions(true);
                        }}
                        onFocus={() => {
                          if (searchTerm.length >= 2) {
                            generateSearchSuggestions(searchTerm);
                            setShowSuggestions(true);
                          }
                        }}
                        onBlur={() => {
                          setTimeout(() => setShowSuggestions(false), 200);
                        }}
                        onKeyDown={(e) => {
                          if (e.key === 'Enter' && searchTerm.trim()) {
                            saveSearchToHistory(searchTerm.trim());
                            setShowSuggestions(false);
                          }
                        }}
                      />
                      {searchTerm && (
                        <Button
                          variant="outline-secondary"
                          onClick={() => {
                            setSearchTerm('');
                            setShowSuggestions(false);
                          }}
                        >
                          Clear
                        </Button>
                      )}
                    </InputGroup>

                    {/* Search Suggestions Dropdown */}
                    {showSuggestions && searchSuggestions.length > 0 && (
                      <div className="position-absolute w-100 bg-white border rounded shadow-lg mt-1" style={{ zIndex: 1000 }}>
                        {searchSuggestions.map((suggestion, index) => (
                          <div
                            key={index}
                            className="p-2 cursor-pointer border-bottom hover-bg-light"
                            style={{ cursor: 'pointer' }}
                            onClick={() => {
                              setSearchTerm(suggestion.value);
                              saveSearchToHistory(suggestion.value);
                              setShowSuggestions(false);
                            }}
                            onMouseDown={(e) => e.preventDefault()}
                          >
                            <small className="text-muted me-2">
                              {suggestion.type === 'tag' ? '🏷️' : '🕐'}
                            </small>
                            {suggestion.label}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </Col>
                <Col md={4} className="d-flex gap-2">
                  <Button
                    variant="outline-primary"
                    onClick={() => setShowFilters(!showFilters)}
                    className="flex-fill"
                  >
                    <Filter className="me-2" />
                    Filters
                  </Button>
                  <Dropdown>
                    <Dropdown.Toggle variant="outline-secondary" id="sort-dropdown">
                      <SortAlphaDown />
                    </Dropdown.Toggle>
                    <Dropdown.Menu>
                      <Dropdown.Item onClick={() => handleFilterChange('ordering', '-created_at')}>
                        Newest First
                      </Dropdown.Item>
                      <Dropdown.Item onClick={() => handleFilterChange('ordering', 'created_at')}>
                        Oldest First
                      </Dropdown.Item>
                      <Dropdown.Item onClick={() => handleFilterChange('ordering', '-likes_count')}>
                        Most Liked
                      </Dropdown.Item>
                      <Dropdown.Item onClick={() => handleFilterChange('ordering', '-critiques_count')}>
                        Most Critiqued
                      </Dropdown.Item>
                      <Dropdown.Item onClick={() => handleFilterChange('ordering', 'title')}>
                        Title A-Z
                      </Dropdown.Item>
                    </Dropdown.Menu>
                  </Dropdown>
                </Col>
              </Row>

              {/* Quick Search Helpers */}
              {!showFilters && (popularTags.length > 0 || recentSearches.length > 0) && (
                <Row className="mb-3">
                  <Col>
                    {/* Popular Tags */}
                    {popularTags.length > 0 && (
                      <div className="mb-2">
                        <small className="text-muted me-2">Popular tags:</small>
                        {popularTags.slice(0, 6).map((tag) => (
                          <Badge
                            key={tag}
                            bg="light"
                            text="dark"
                            className="me-1 mb-1 cursor-pointer"
                            style={{ cursor: 'pointer' }}
                            onClick={() => {
                              setSearchTerm(tag);
                              saveSearchToHistory(tag);
                            }}
                          >
                            #{tag}
                          </Badge>
                        ))}
                      </div>
                    )}

                    {/* Recent Searches */}
                    {recentSearches.length > 0 && (
                      <div>
                        <small className="text-muted me-2">Recent searches:</small>
                        {recentSearches.map((search, index) => (
                          <Badge
                            key={index}
                            bg="outline-secondary"
                            className="me-1 mb-1 cursor-pointer border"
                            style={{ cursor: 'pointer' }}
                            onClick={() => setSearchTerm(search)}
                          >
                            {search}
                          </Badge>
                        ))}
                        <Button
                          variant="link"
                          size="sm"
                          className="p-0 ms-2"
                          onClick={() => {
                            localStorage.removeItem('artworkSearchHistory');
                            setRecentSearches([]);
                          }}
                        >
                          <small>Clear history</small>
                        </Button>
                      </div>
                    )}
                  </Col>
                </Row>
              )}

              {/* Advanced Filters */}
              {showFilters && (
                <Row className="border-top pt-3">
                  <Col md={6} lg={3} className="mb-3">
                    <Form.Label>Artist Username</Form.Label>
                    <Form.Control
                      type="text"
                      placeholder="Enter username"
                      value={filters.author__username}
                      onChange={(e) => handleFilterChange('author__username', e.target.value)}
                    />
                  </Col>
                  <Col md={6} lg={3} className="mb-3">
                    <Form.Label>Medium</Form.Label>
                    <Form.Control
                      type="text"
                      placeholder="e.g., Oil, Acrylic, Digital"
                      value={filters.medium}
                      onChange={(e) => handleFilterChange('medium', e.target.value)}
                    />
                  </Col>
                  <Col md={6} lg={3} className="mb-3">
                    <Form.Label>Tags</Form.Label>
                    <Form.Control
                      type="text"
                      placeholder="e.g., landscape, portrait"
                      value={filters.tags}
                      onChange={(e) => handleFilterChange('tags', e.target.value)}
                    />
                  </Col>
                  <Col md={6} lg={3} className="mb-3">
                    <Form.Label>Min. Likes</Form.Label>
                    <Form.Control
                      type="number"
                      min="0"
                      placeholder="0"
                      value={filters.min_likes}
                      onChange={(e) => handleFilterChange('min_likes', e.target.value)}
                    />
                  </Col>
                  <Col md={6} lg={3} className="mb-3">
                    <Form.Label>Min. Critiques</Form.Label>
                    <Form.Control
                      type="number"
                      min="0"
                      placeholder="0"
                      value={filters.min_critiques}
                      onChange={(e) => handleFilterChange('min_critiques', e.target.value)}
                    />
                  </Col>
                  <Col md={6} lg={3} className="mb-3">
                    <Form.Label>Created After</Form.Label>
                    <Form.Control
                      type="date"
                      value={filters.created_after}
                      onChange={(e) => handleFilterChange('created_after', e.target.value)}
                    />
                  </Col>
                  <Col md={6} lg={3} className="mb-3">
                    <Form.Label>Created Before</Form.Label>
                    <Form.Control
                      type="date"
                      value={filters.created_before}
                      onChange={(e) => handleFilterChange('created_before', e.target.value)}
                    />
                  </Col>
                  <Col lg={3} className="mb-3 d-flex align-items-end">
                    <Button
                      variant="outline-danger"
                      onClick={clearFilters}
                      className="w-100"
                    >
                      Clear All Filters
                    </Button>
                  </Col>
                </Row>
              )}

              {/* Active Filters Display */}
              {(debouncedSearchTerm || Object.values(filters).some(v => v && v !== '-created_at')) && (
                <Row className="border-top pt-3">
                  <Col>
                    <div className="d-flex flex-wrap gap-2">
                      <small className="text-muted me-2">Active filters:</small>
                      {debouncedSearchTerm && (
                        <Badge bg="primary">Search: "{debouncedSearchTerm}"</Badge>
                      )}
                      {filters.author__username && (
                        <Badge bg="secondary">Artist: {filters.author__username}</Badge>
                      )}
                      {filters.medium && (
                        <Badge bg="secondary">Medium: {filters.medium}</Badge>
                      )}
                      {filters.tags && (
                        <Badge bg="secondary">Tags: {filters.tags}</Badge>
                      )}
                      {filters.min_likes && (
                        <Badge bg="secondary">Min Likes: {filters.min_likes}</Badge>
                      )}
                      {filters.min_critiques && (
                        <Badge bg="secondary">Min Critiques: {filters.min_critiques}</Badge>
                      )}
                    </div>
                  </Col>
                </Row>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Results Count */}
      {!loading && (
        <Row className="mb-3">
          <Col>
            <p className="text-muted">
              {pagination.count === 0 
                ? 'No artworks found' 
                : `Showing ${artworks.length} of ${pagination.count} artwork${pagination.count !== 1 ? 's' : ''}`
              }
            </p>
          </Col>
        </Row>
      )}

      {/* Loading State */}
      {loading && (
        <Row className="justify-content-center py-5">
          <Col xs="auto">
            <Spinner animation="border" role="status">
              <span className="visually-hidden">Loading...</span>
            </Spinner>
          </Col>
        </Row>
      )}

      {/* Error State */}
      {error && (
        <Row className="mb-4">
          <Col>
            <Alert variant="danger" onClose={() => setError(null)} dismissible>
              {error}
            </Alert>
          </Col>
        </Row>
      )}

      {/* Artwork Grid */}
      {!loading && !error && (
        <>
          <Row>
            {artworks.length === 0 ? (
              <Col>
                <Card className="text-center py-5">
                  <Card.Body>
                    <h5>No artworks found</h5>
                    <p className="text-muted">
                      Try adjusting your search terms or filters to find what you're looking for.
                    </p>
                    <Button variant="outline-primary" onClick={clearFilters}>
                      Clear All Filters
                    </Button>
                  </Card.Body>
                </Card>
              </Col>
            ) : (
              artworks.map((artwork) => (
                <Col key={artwork.id} sm={6} md={4} lg={3} className="mb-4">
                  <Card className="h-100 shadow-sm border-0 artwork-card">
                    <div className="artwork-image-container">
                      <Card.Img
                        variant="top"
                        src={artwork.image || '/placeholder-image.jpg'}
                        alt={artwork.title}
                        className="artwork-image"
                        style={{
                          height: '200px',
                          objectFit: 'cover',
                          cursor: 'pointer'
                        }}
                        as={Link}
                        to={`/artworks/${artwork.id}`}
                      />
                      {artwork.medium && (
                        <Badge 
                          bg="dark" 
                          className="position-absolute top-0 end-0 m-2"
                        >
                          {artwork.medium}
                        </Badge>
                      )}
                    </div>
                    <Card.Body className="d-flex flex-column">
                      <Card.Title className="h6 mb-2">
                        <Link 
                          to={`/artworks/${artwork.id}`} 
                          className="text-decoration-none text-dark"
                        >
                          {artwork.title}
                        </Link>
                      </Card.Title>
                      <Card.Text className="text-muted small mb-2">
                        by <Link 
                          to={`/profile/${artwork.author_username}`}
                          className="text-decoration-none"
                        >
                          {artwork.author_username}
                        </Link>
                      </Card.Text>
                      {artwork.description && (
                        <Card.Text className="small text-muted mb-2">
                          {artwork.description.length > 80 
                            ? `${artwork.description.substring(0, 80)}...` 
                            : artwork.description
                          }
                        </Card.Text>
                      )}
                      {artwork.tags && (
                        <div className="mb-2">
                          {artwork.tags.split(',').slice(0, 3).map((tag, index) => (
                            <Badge 
                              key={index} 
                              bg="light" 
                              text="dark" 
                              className="me-1 mb-1"
                            >
                              {tag.trim()}
                            </Badge>
                          ))}
                        </div>
                      )}
                      <div className="mt-auto">
                        <div className="d-flex justify-content-between align-items-center text-muted small">
                          <div className="d-flex gap-3">
                            <span>
                              <Heart className="me-1" />
                              {artwork.likes_count || 0}
                            </span>
                            <span>
                              <MessageCircle className="me-1" />
                              {artwork.critiques_count || 0}
                            </span>
                          </div>
                          <span>{formatDate(artwork.created_at)}</span>
                        </div>
                      </div>
                    </Card.Body>
                  </Card>
                </Col>
              ))
            )}
          </Row>

          {/* Load More Button and Pagination Controls */}
          {pagination.count > 12 && (
            <Row className="mt-4">
              <Col>
                {/* Load More Button for Infinite Scroll */}
                {pagination.has_next && (
                  <div className="text-center mb-4">
                    <Button
                      variant="primary"
                      size="lg"
                      onClick={handleLoadMore}
                      disabled={loadingMore}
                      className="px-5"
                    >
                      {loadingMore ? (
                        <>
                          <Spinner
                            as="span"
                            animation="border"
                            size="sm"
                            role="status"
                            aria-hidden="true"
                            className="me-2"
                          />
                          Loading more artworks...
                        </>
                      ) : (
                        <>Load More ({pagination.count - artworks.length} remaining)</>
                      )}
                    </Button>
                  </div>
                )}

                {/* Progress Indicator */}
                {pagination.count > 0 && (
                  <div className="text-center mb-3">
                    <div className="progress" style={{ height: '4px' }}>
                      <div
                        className="progress-bar"
                        role="progressbar"
                        style={{
                          width: `${(artworks.length / pagination.count) * 100}%`
                        }}
                        aria-valuenow={artworks.length}
                        aria-valuemin="0"
                        aria-valuemax={pagination.count}
                      ></div>
                    </div>
                    <small className="text-muted">
                      Loaded {artworks.length} of {pagination.count} artworks
                    </small>
                  </div>
                )}

                {/* Traditional Pagination (Alternative Navigation) */}
                <nav aria-label="Artwork gallery pagination">
                  <div className="d-flex justify-content-center align-items-center gap-2 flex-wrap">
                    <Button
                      variant="outline-secondary"
                      size="sm"
                      disabled={!pagination.has_previous}
                      onClick={() => handlePageChange(pagination.current_page - 1)}
                    >
                      Previous
                    </Button>
                    
                    {/* Page Numbers */}
                    {getTotalPages() <= 7 ? (
                      // Show all pages if 7 or fewer
                      Array.from({ length: getTotalPages() }, (_, i) => i + 1).map(page => (
                        <Button
                          key={page}
                          variant={page === pagination.current_page ? "primary" : "outline-secondary"}
                          size="sm"
                          onClick={() => handlePageChange(page)}
                        >
                          {page}
                        </Button>
                      ))
                    ) : (
                      // Show abbreviated pagination for many pages
                      <>
                        <Button
                          variant={1 === pagination.current_page ? "primary" : "outline-secondary"}
                          size="sm"
                          onClick={() => handlePageChange(1)}
                        >
                          1
                        </Button>
                        
                        {pagination.current_page > 3 && <span className="px-2">...</span>}
                        
                        {/* Show current page and surrounding pages */}
                        {Array.from(
                          { length: 3 },
                          (_, i) => pagination.current_page - 1 + i
                        )
                          .filter(page => page > 1 && page < getTotalPages())
                          .map(page => (
                            <Button
                              key={page}
                              variant={page === pagination.current_page ? "primary" : "outline-secondary"}
                              size="sm"
                              onClick={() => handlePageChange(page)}
                            >
                              {page}
                            </Button>
                          ))}
                        
                        {pagination.current_page < getTotalPages() - 2 && <span className="px-2">...</span>}
                        
                        {getTotalPages() > 1 && (
                          <Button
                            variant={getTotalPages() === pagination.current_page ? "primary" : "outline-secondary"}
                            size="sm"
                            onClick={() => handlePageChange(getTotalPages())}
                          >
                            {getTotalPages()}
                          </Button>
                        )}
                      </>
                    )}
                    
                    <Button
                      variant="outline-secondary"
                      size="sm"
                      disabled={!pagination.has_next}
                      onClick={() => handlePageChange(pagination.current_page + 1)}
                    >
                      Next
                    </Button>
                  </div>
                  
                  <div className="text-center mt-2">
                    <small className="text-muted">
                      Page {pagination.current_page} of {getTotalPages()}
                    </small>
                  </div>
                </nav>
              </Col>
            </Row>
          )}

          {/* Loading More Indicator (for infinite scroll) */}
          {loadingMore && (
            <Row className="mt-3">
              <Col className="text-center">
                <Spinner animation="border" variant="primary" />
                <p className="mt-2 text-muted">Loading more artworks...</p>
              </Col>
            </Row>
          )}
        </>
      )}
    </Container>
  );
};

export default Gallery;