import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Folder, FolderOpen, Grid, List, Search, Filter, Globe, Lock, EyeOff, Heart, MessageSquare } from 'lucide-react';

const FolderGallery = ({ userId, username, showPrivate = false }) => {
  const [folders, setFolders] = useState([]);
  const [unorganizedArtworks, setUnorganizedArtworks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [viewMode, setViewMode] = useState('folders'); // 'folders' or 'grid'
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedVisibility, setSelectedVisibility] = useState('all');
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchFolderData();
  }, [userId, showPrivate]);

  const fetchFolderData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch folders based on permissions
      let foldersUrl = '/api/folders/';
      if (showPrivate) {
        // Current user viewing their own profile
        foldersUrl = '/api/folders/my_folders/';
      } else if (userId) {
        // Viewing someone else's profile - only public folders
        foldersUrl = `/api/folders/?owner=${userId}`;
      }

      const headers = {};
      const token = localStorage.getItem('token');
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      const foldersResponse = await fetch(foldersUrl, { headers });
      
      if (foldersResponse.ok) {
        const foldersData = await foldersResponse.json();
        const foldersList = foldersData.folders || foldersData.results || [];
        
        // Fetch full folder details with artworks
        const foldersWithArtworks = await Promise.all(
          foldersList.map(async (folder) => {
            try {
              const folderResponse = await fetch(`/api/folders/${folder.id}/`, { headers });
              if (folderResponse.ok) {
                return await folderResponse.json();
              }
              return folder;
            } catch (err) {
              console.error(`Error fetching folder ${folder.id}:`, err);
              return folder;
            }
          })
        );
        
        setFolders(foldersWithArtworks);
      }

      // Fetch unorganized artworks
      let artworksUrl = '/api/artworks/?folder__isnull=true';
      if (userId) {
        artworksUrl += `&author=${userId}`;
      }

      const artworksResponse = await fetch(artworksUrl, { headers });
      if (artworksResponse.ok) {
        const artworksData = await artworksResponse.json();
        setUnorganizedArtworks(artworksData.results || []);
      }

    } catch (err) {
      setError('Failed to load gallery content');
      console.error('Error fetching folder data:', err);
    } finally {
      setLoading(false);
    }
  };

  const filteredFolders = folders.filter(folder => {
    // Search filter
    if (searchTerm && !folder.name.toLowerCase().includes(searchTerm.toLowerCase()) &&
        !folder.description?.toLowerCase().includes(searchTerm.toLowerCase())) {
      return false;
    }

    // Visibility filter
    if (selectedVisibility !== 'all' && folder.is_public !== selectedVisibility) {
      return false;
    }

    return true;
  });

  const filteredUnorganized = unorganizedArtworks.filter(artwork => {
    if (searchTerm && !artwork.title.toLowerCase().includes(searchTerm.toLowerCase()) &&
        !artwork.description?.toLowerCase().includes(searchTerm.toLowerCase())) {
      return false;
    }
    return true;
  });

  const getAllArtworks = () => {
    const allArtworks = [];
    filteredFolders.forEach(folder => {
      if (folder.artworks) {
        allArtworks.push(...folder.artworks);
      }
    });
    allArtworks.push(...filteredUnorganized);
    return allArtworks;
  };

  const getVisibilityIcon = (visibility) => {
    switch (visibility) {
      case 'public': return <Globe className="w-4 h-4 text-green-600" />;
      case 'private': return <Lock className="w-4 h-4 text-red-600" />;
      case 'unlisted': return <EyeOff className="w-4 h-4 text-yellow-600" />;
      default: return <Globe className="w-4 h-4" />;
    }
  };

  if (loading) {
    return (
      <div className="d-flex justify-content-center py-5">
        <div className="spinner-border text-primary" role="status">
          <span className="visually-hidden">Loading gallery...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="alert alert-danger" role="alert">
        {error}
      </div>
    );
  }

  return (
    <div className="folder-gallery">
      {/* Gallery Controls */}
      <div className="row mb-4">
        <div className="col-12">
          <div className="d-flex flex-wrap align-items-center justify-content-between gap-3">
            {/* Search */}
            <div className="d-flex align-items-center gap-2 flex-grow-1" style={{ maxWidth: '400px' }}>
              <div className="input-group">
                <span className="input-group-text">
                  <Search className="w-4 h-4" />
                </span>
                <input
                  type="text"
                  className="form-control"
                  placeholder="Search artworks and folders..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
            </div>

            {/* Filters and View Controls */}
            <div className="d-flex align-items-center gap-2">
              {showPrivate && (
                <select
                  className="form-select form-select-sm"
                  value={selectedVisibility}
                  onChange={(e) => setSelectedVisibility(e.target.value)}
                  style={{ width: 'auto' }}
                >
                  <option value="all">All Folders</option>
                  <option value="public">Public</option>
                  <option value="unlisted">Unlisted</option>
                  <option value="private">Private</option>
                </select>
              )}

              <div className="btn-group" role="group">
                <button
                  className={`btn btn-sm ${viewMode === 'folders' ? 'btn-primary' : 'btn-outline-primary'}`}
                  onClick={() => setViewMode('folders')}
                  title="Folder view"
                >
                  <Folder className="w-4 h-4" />
                </button>
                <button
                  className={`btn btn-sm ${viewMode === 'grid' ? 'btn-primary' : 'btn-outline-primary'}`}
                  onClick={() => setViewMode('grid')}
                  title="Grid view"
                >
                  <Grid className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      {viewMode === 'folders' ? (
        <FolderView
          folders={filteredFolders}
          unorganizedArtworks={filteredUnorganized}
          showPrivate={showPrivate}
          username={username}
        />
      ) : (
        <GridView artworks={getAllArtworks()} />
      )}

      {/* Empty State */}
      {filteredFolders.length === 0 && filteredUnorganized.length === 0 && (
        <div className="text-center py-5">
          <Folder className="w-16 h-16 text-muted mx-auto mb-3" />
          <h5 className="text-muted">
            {searchTerm ? 'No matching content found' : 'No artworks to display'}
          </h5>
          <p className="text-muted">
            {searchTerm 
              ? 'Try adjusting your search terms or filters.'
              : showPrivate 
                ? 'Upload your first artwork to get started!'
                : 'This artist hasn\'t shared any public artwork yet.'
            }
          </p>
        </div>
      )}
    </div>
  );
};

const FolderView = ({ folders, unorganizedArtworks, showPrivate, username }) => {
  const [expandedFolders, setExpandedFolders] = useState(new Set());

  const toggleFolder = (folderId) => {
    const newExpanded = new Set(expandedFolders);
    if (newExpanded.has(folderId)) {
      newExpanded.delete(folderId);
    } else {
      newExpanded.add(folderId);
    }
    setExpandedFolders(newExpanded);
  };

  const getVisibilityIcon = (visibility) => {
    switch (visibility) {
      case 'public': return <Globe className="w-4 h-4 text-green-600" />;
      case 'private': return <Lock className="w-4 h-4 text-red-600" />;
      case 'unlisted': return <EyeOff className="w-4 h-4 text-yellow-600" />;
      default: return <Globe className="w-4 h-4" />;
    }
  };

  return (
    <div className="folder-view">
      {/* Portfolio Folders */}
      {folders.map((folder) => {
        const isExpanded = expandedFolders.has(folder.id);
        const hasArtworks = folder.artworks && folder.artworks.length > 0;

        return (
          <div key={folder.id} className="card mb-4">
            <div 
              className="card-header d-flex align-items-center justify-content-between cursor-pointer"
              onClick={() => toggleFolder(folder.id)}
              style={{ cursor: 'pointer' }}
            >
              <div className="d-flex align-items-center">
                {isExpanded ? (
                  <FolderOpen className="w-5 h-5 text-primary me-2" />
                ) : (
                  <Folder className="w-5 h-5 text-primary me-2" />
                )}
                <div>
                  <h6 className="mb-0">{folder.name}</h6>
                  <div className="d-flex align-items-center gap-2">
                    {showPrivate && getVisibilityIcon(folder.is_public)}
                    <small className="text-muted">
                      {folder.artwork_count} {folder.artwork_count === 1 ? 'artwork' : 'artworks'}
                    </small>
                    {folder.description && (
                      <small className="text-muted">• {folder.description}</small>
                    )}
                  </div>
                </div>
              </div>
              
              <Link
                to={`/profile/${username}/folder/${folder.slug}`}
                className="btn btn-sm btn-outline-primary"
                onClick={(e) => e.stopPropagation()}
              >
                View Folder
              </Link>
            </div>

            {isExpanded && (
              <div className="card-body">
                {hasArtworks ? (
                  <div className="row">
                    {folder.artworks.map((artwork) => (
                      <div key={artwork.id} className="col-xl-2 col-lg-3 col-md-4 col-sm-6 mb-3">
                        <ArtworkCard artwork={artwork} />
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-3">
                    <p className="text-muted mb-0">This folder is empty.</p>
                  </div>
                )}
              </div>
            )}
          </div>
        );
      })}

      {/* Unorganized Artworks */}
      {unorganizedArtworks.length > 0 && (
        <div className="card mb-4">
          <div className="card-header d-flex align-items-center">
            <FolderOpen className="w-5 h-5 me-2 text-muted" />
            <div>
              <h6 className="mb-0">Unorganized Artworks</h6>
              <small className="text-muted">
                {unorganizedArtworks.length} {unorganizedArtworks.length === 1 ? 'artwork' : 'artworks'} not in any folder
              </small>
            </div>
          </div>
          <div className="card-body">
            <div className="row">
              {unorganizedArtworks.map((artwork) => (
                <div key={artwork.id} className="col-xl-2 col-lg-3 col-md-4 col-sm-6 mb-3">
                  <ArtworkCard artwork={artwork} />
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

const GridView = ({ artworks }) => {
  return (
    <div className="grid-view">
      <div className="row">
        {artworks.map((artwork) => (
          <div key={artwork.id} className="col-xl-2 col-lg-3 col-md-4 col-sm-6 mb-4">
            <ArtworkCard artwork={artwork} showFolder={true} />
          </div>
        ))}
      </div>
    </div>
  );
};

const ArtworkCard = ({ artwork, showFolder = false }) => {
  return (
    <div className="card h-100 artwork-card">
      <Link to={`/artwork/${artwork.id}`} className="text-decoration-none">
        <div className="position-relative">
          <img
            src={artwork.image_display_url || '/placeholder-image.png'}
            alt={artwork.title}
            className="card-img-top"
            style={{ height: '200px', objectFit: 'cover' }}
          />
          {showFolder && artwork.folder_name && (
            <div className="position-absolute top-0 start-0 m-2">
              <span className="badge bg-primary bg-opacity-75">
                <Folder className="w-3 h-3 me-1" />
                {artwork.folder_name}
              </span>
            </div>
          )}
        </div>
      </Link>
      
      <div className="card-body p-2">
        <h6 className="card-title mb-1" style={{ fontSize: '0.9rem' }}>
          <Link to={`/artwork/${artwork.id}`} className="text-decoration-none text-dark">
            {artwork.title}
          </Link>
        </h6>
        
        <div className="d-flex align-items-center justify-content-between">
          <small className="text-muted">
            {artwork.medium}
          </small>
          <div className="d-flex align-items-center gap-2">
            <small className="text-muted d-flex align-items-center">
              <Heart className="w-3 h-3 me-1" />
              {artwork.likes_count || 0}
            </small>
            {artwork.critiques_count > 0 && (
              <small className="text-muted d-flex align-items-center">
                <MessageSquare className="w-3 h-3 me-1" />
                {artwork.critiques_count}
              </small>
            )}
          </div>
        </div>

        {artwork.tags_list && artwork.tags_list.length > 0 && (
          <div className="mt-1">
            {artwork.tags_list.slice(0, 2).map((tag, index) => (
              <span key={index} className="badge bg-light text-dark me-1" style={{ fontSize: '0.7rem' }}>
                {tag}
              </span>
            ))}
            {artwork.tags_list.length > 2 && (
              <span className="badge bg-light text-muted" style={{ fontSize: '0.7rem' }}>
                +{artwork.tags_list.length - 2}
              </span>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default FolderGallery;