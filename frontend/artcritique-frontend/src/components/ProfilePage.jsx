import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { Plus, Folder, FolderOpen, Edit3, Trash2, Eye, EyeOff, Globe, Lock, Users } from 'lucide-react';

const ProfilePage = () => {
  const { username } = useParams();
  const [user, setUser] = useState(null);
  const [folders, setFolders] = useState([]);
  const [unorganizedArtworks, setUnorganizedArtworks] = useState([]);
  const [isOwnProfile, setIsOwnProfile] = useState(false);
  const [showCreateFolder, setShowCreateFolder] = useState(false);
  const [editingFolder, setEditingFolder] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchProfileData();
  }, [username]);

  const fetchProfileData = async () => {
    try {
      setLoading(true);
      
      // Get current user info to check if this is their profile
      const currentUserResponse = await fetch('/api/auth/user/', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      let currentUser = null;
      if (currentUserResponse.ok) {
        currentUser = await currentUserResponse.json();
      }

      // Fetch profile user data
      const userResponse = await fetch(`/api/users/?username=${username}`);
      if (!userResponse.ok) throw new Error('User not found');
      
      const userData = await userResponse.json();
      const profileUser = userData.results[0];
      setUser(profileUser);
      
      const ownProfile = currentUser && currentUser.username === username;
      setIsOwnProfile(ownProfile);

      // Fetch folders based on permissions
      let foldersUrl = '/api/folders/';
      if (ownProfile) {
        foldersUrl = '/api/folders/my_folders/';
      } else {
        foldersUrl = `/api/folders/?owner=${profileUser.id}`;
      }

      const foldersResponse = await fetch(foldersUrl, {
        headers: currentUser ? {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        } : {}
      });

      if (foldersResponse.ok) {
        const foldersData = await foldersResponse.json();
        setFolders(foldersData.folders || foldersData.results || []);
      }

      // Fetch unorganized artworks (not in any folder)
      const artworksResponse = await fetch(`/api/artworks/?author=${profileUser.id}&folder__isnull=true`, {
        headers: currentUser ? {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        } : {}
      });

      if (artworksResponse.ok) {
        const artworksData = await artworksResponse.json();
        setUnorganizedArtworks(artworksData.results || []);
      }

    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const createFolder = async (folderData) => {
    try {
      const response = await fetch('/api/folders/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(folderData)
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.name?.[0] || 'Failed to create folder');
      }

      await fetchProfileData();
      setShowCreateFolder(false);
    } catch (err) {
      alert(err.message);
    }
  };

  const updateFolder = async (folderId, folderData) => {
    try {
      const response = await fetch(`/api/folders/${folderId}/`, {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(folderData)
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.name?.[0] || 'Failed to update folder');
      }

      await fetchProfileData();
      setEditingFolder(null);
    } catch (err) {
      alert(err.message);
    }
  };

  const deleteFolder = async (folderId) => {
    if (!confirm('Are you sure you want to delete this folder? Artworks will not be deleted, just moved out of the folder.')) {
      return;
    }

    try {
      const response = await fetch(`/api/folders/${folderId}/`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to delete folder');
      }

      await fetchProfileData();
    } catch (err) {
      alert(err.message);
    }
  };

  const getVisibilityIcon = (visibility) => {
    switch (visibility) {
      case 'public': return <Globe className="w-4 h-4 text-green-600" />;
      case 'private': return <Lock className="w-4 h-4 text-red-600" />;
      case 'unlisted': return <EyeOff className="w-4 h-4 text-yellow-600" />;
      default: return <Eye className="w-4 h-4" />;
    }
  };

  const getVisibilityLabel = (visibility) => {
    switch (visibility) {
      case 'public': return 'Public';
      case 'private': return 'Private';
      case 'unlisted': return 'Unlisted';
      default: return 'Unknown';
    }
  };

  if (loading) {
    return (
      <div className="container mt-4">
        <div className="d-flex justify-content-center">
          <div className="spinner-border" role="status">
            <span className="visually-hidden">Loading...</span>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mt-4">
        <div className="alert alert-danger" role="alert">
          Error: {error}
        </div>
      </div>
    );
  }

  return (
    <div className="container mt-4">
      {/* Profile Header */}
      <div className="row mb-4">
        <div className="col-12">
          <div className="d-flex align-items-center justify-content-between">
            <div className="d-flex align-items-center">
              <img
                src={user?.profile?.profile_picture_display_url || '/default-avatar.png'}
                alt={user?.username}
                className="rounded-circle me-3"
                style={{ width: '80px', height: '80px', objectFit: 'cover' }}
              />
              <div>
                <h2 className="mb-1">{user?.username}</h2>
                <p className="text-muted mb-0">{user?.profile?.bio || 'No bio available'}</p>
                <small className="text-muted">
                  Karma: {user?.profile?.karma || 0} • 
                  Member since {new Date(user?.date_joined).toLocaleDateString()}
                </small>
              </div>
            </div>
            
            {isOwnProfile && (
              <button
                className="btn btn-primary"
                onClick={() => setShowCreateFolder(true)}
              >
                <Plus className="w-4 h-4 me-2" />
                Create Folder
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Folders Section */}
      <div className="row">
        <div className="col-12">
          <h3 className="mb-3">
            {isOwnProfile ? 'My Portfolio' : `${user?.username}'s Portfolio`}
          </h3>

          {/* Folders */}
          {folders.map((folder) => (
            <FolderCard
              key={folder.id}
              folder={folder}
              isOwnProfile={isOwnProfile}
              onEdit={setEditingFolder}
              onDelete={deleteFolder}
            />
          ))}

          {/* Unorganized Artworks */}
          {unorganizedArtworks.length > 0 && (
            <div className="card mb-4">
              <div className="card-header d-flex align-items-center">
                <FolderOpen className="w-5 h-5 me-2 text-muted" />
                <span>Unorganized Artworks</span>
                <span className="badge bg-secondary ms-2">{unorganizedArtworks.length}</span>
              </div>
              <div className="card-body">
                <div className="row">
                  {unorganizedArtworks.map((artwork) => (
                    <div key={artwork.id} className="col-md-3 col-sm-4 col-6 mb-3">
                      <ArtworkCard artwork={artwork} />
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {folders.length === 0 && unorganizedArtworks.length === 0 && (
            <div className="text-center py-5">
              <Folder className="w-16 h-16 text-muted mx-auto mb-3" />
              <h5 className="text-muted">
                {isOwnProfile ? 'No portfolio created yet' : 'No public artworks'}
              </h5>
              <p className="text-muted">
                {isOwnProfile 
                  ? 'Create your first folder to organize your artwork collection.'
                  : 'This artist hasn\'t shared any public artwork yet.'
                }
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Create/Edit Folder Modal */}
      <FolderModal
        show={showCreateFolder || editingFolder}
        folder={editingFolder}
        onSave={editingFolder ? updateFolder : createFolder}
        onClose={() => {
          setShowCreateFolder(false);
          setEditingFolder(null);
        }}
      />
    </div>
  );
};

const FolderCard = ({ folder, isOwnProfile, onEdit, onDelete }) => {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="card mb-4">
      <div className="card-header d-flex align-items-center justify-content-between">
        <div className="d-flex align-items-center">
          <button
            className="btn btn-link p-0 me-2"
            onClick={() => setExpanded(!expanded)}
          >
            {expanded ? (
              <FolderOpen className="w-5 h-5 text-primary" />
            ) : (
              <Folder className="w-5 h-5 text-primary" />
            )}
          </button>
          <div>
            <h6 className="mb-0">{folder.name}</h6>
            <small className="text-muted d-flex align-items-center">
              {getVisibilityIcon(folder.is_public)}
              <span className="ms-1 me-2">{getVisibilityLabel(folder.is_public)}</span>
              <span className="badge bg-secondary">{folder.artwork_count} artworks</span>
            </small>
          </div>
        </div>

        {isOwnProfile && (
          <div className="btn-group" role="group">
            <button
              className="btn btn-outline-secondary btn-sm"
              onClick={() => onEdit(folder)}
            >
              <Edit3 className="w-4 h-4" />
            </button>
            <button
              className="btn btn-outline-danger btn-sm"
              onClick={() => onDelete(folder.id)}
            >
              <Trash2 className="w-4 h-4" />
            </button>
          </div>
        )}
      </div>

      {expanded && (
        <div className="card-body">
          {folder.description && (
            <p className="text-muted mb-3">{folder.description}</p>
          )}
          
          {folder.artworks && folder.artworks.length > 0 ? (
            <div className="row">
              {folder.artworks.map((artwork) => (
                <div key={artwork.id} className="col-md-3 col-sm-4 col-6 mb-3">
                  <ArtworkCard artwork={artwork} />
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-3">
              <p className="text-muted mb-0">No artworks in this folder yet.</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

const ArtworkCard = ({ artwork }) => {
  return (
    <div className="card h-100">
      <img
        src={artwork.image_display_url || '/placeholder-image.png'}
        alt={artwork.title}
        className="card-img-top"
        style={{ height: '200px', objectFit: 'cover' }}
      />
      <div className="card-body p-2">
        <h6 className="card-title mb-1" style={{ fontSize: '0.9rem' }}>
          {artwork.title}
        </h6>
        <small className="text-muted">
          {artwork.likes_count} likes • {artwork.medium}
        </small>
      </div>
    </div>
  );
};

const FolderModal = ({ show, folder, onSave, onClose }) => {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [visibility, setVisibility] = useState('public');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (folder) {
      setName(folder.name || '');
      setDescription(folder.description || '');
      setVisibility(folder.is_public || 'public');
    } else {
      setName('');
      setDescription('');
      setVisibility('public');
    }
  }, [folder]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const folderData = {
        name,
        description,
        is_public: visibility
      };

      if (folder) {
        await onSave(folder.id, folderData);
      } else {
        await onSave(folderData);
      }
    } finally {
      setLoading(false);
    }
  };

  if (!show) return null;

  return (
    <div className="modal show d-block" style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}>
      <div className="modal-dialog">
        <div className="modal-content">
          <div className="modal-header">
            <h5 className="modal-title">
              {folder ? 'Edit Folder' : 'Create New Folder'}
            </h5>
            <button
              type="button"
              className="btn-close"
              onClick={onClose}
              disabled={loading}
            />
          </div>
          
          <form onSubmit={handleSubmit}>
            <div className="modal-body">
              <div className="mb-3">
                <label htmlFor="folderName" className="form-label">
                  Folder Name *
                </label>
                <input
                  type="text"
                  className="form-control"
                  id="folderName"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  required
                  maxLength={100}
                />
              </div>

              <div className="mb-3">
                <label htmlFor="folderDescription" className="form-label">
                  Description
                </label>
                <textarea
                  className="form-control"
                  id="folderDescription"
                  rows="3"
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  maxLength={500}
                />
              </div>

              <div className="mb-3">
                <label htmlFor="folderVisibility" className="form-label">
                  Visibility
                </label>
                <select
                  className="form-select"
                  id="folderVisibility"
                  value={visibility}
                  onChange={(e) => setVisibility(e.target.value)}
                >
                  <option value="public">
                    🌍 Public - Everyone can see this folder
                  </option>
                  <option value="unlisted">
                    👁️ Unlisted - Only people with the link can see this
                  </option>
                  <option value="private">
                    🔒 Private - Only you can see this folder
                  </option>
                </select>
              </div>
            </div>

            <div className="modal-footer">
              <button
                type="button"
                className="btn btn-secondary"
                onClick={onClose}
                disabled={loading}
              >
                Cancel
              </button>
              <button
                type="submit"
                className="btn btn-primary"
                disabled={loading || !name.trim()}
              >
                {loading ? (
                  <>
                    <span className="spinner-border spinner-border-sm me-2" />
                    {folder ? 'Updating...' : 'Creating...'}
                  </>
                ) : (
                  folder ? 'Update Folder' : 'Create Folder'
                )}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default ProfilePage;