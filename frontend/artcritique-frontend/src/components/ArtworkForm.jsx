import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { Upload, Folder, Plus, Image as ImageIcon, Tag, Palette } from 'lucide-react';

const ArtworkForm = ({ mode = 'create' }) => {
  const navigate = useNavigate();
  const { id } = useParams();
  
  // Form state
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    medium: '',
    dimensions: '',
    tags: '',
    folder: '',
    image: null
  });
  
  // UI state
  const [folders, setFolders] = useState([]);
  const [loading, setLoading] = useState(false);
  const [imagePreview, setImagePreview] = useState(null);
  const [showCreateFolder, setShowCreateFolder] = useState(false);
  const [errors, setErrors] = useState({});

  useEffect(() => {
    fetchUserFolders();
    if (mode === 'edit' && id) {
      fetchArtworkData();
    }
  }, [mode, id]);

  const fetchUserFolders = async () => {
    try {
      const response = await fetch('/api/folders/my_folders/', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setFolders(data.folders || []);
      }
    } catch (error) {
      console.error('Error fetching folders:', error);
    }
  };

  const fetchArtworkData = async () => {
    try {
      const response = await fetch(`/api/artworks/${id}/`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (response.ok) {
        const artwork = await response.json();
        setFormData({
          title: artwork.title || '',
          description: artwork.description || '',
          medium: artwork.medium || '',
          dimensions: artwork.dimensions || '',
          tags: artwork.tags || '',
          folder: artwork.folder || '',
          image: null // Don't set existing image in form
        });
        if (artwork.image_display_url) {
          setImagePreview(artwork.image_display_url);
        }
      }
    } catch (error) {
      console.error('Error fetching artwork:', error);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    
    // Clear field-specific errors when user starts typing
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: null
      }));
    }
  };

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      // Validate file type
      if (!file.type.startsWith('image/')) {
        setErrors(prev => ({
          ...prev,
          image: 'Please select a valid image file'
        }));
        return;
      }

      // Validate file size (5MB limit)
      if (file.size > 5 * 1024 * 1024) {
        setErrors(prev => ({
          ...prev,
          image: 'Image size must be less than 5MB'
        }));
        return;
      }

      setFormData(prev => ({
        ...prev,
        image: file
      }));

      // Create preview
      const reader = new FileReader();
      reader.onload = () => setImagePreview(reader.result);
      reader.readAsDataURL(file);

      // Clear image errors
      setErrors(prev => ({
        ...prev,
        image: null
      }));
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

      if (response.ok) {
        const newFolder = await response.json();
        setFolders(prev => [...prev, newFolder]);
        setFormData(prev => ({
          ...prev,
          folder: newFolder.id
        }));
        setShowCreateFolder(false);
        return newFolder;
      } else {
        const error = await response.json();
        throw new Error(error.name?.[0] || 'Failed to create folder');
      }
    } catch (error) {
      alert('Error creating folder: ' + error.message);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setErrors({});

    try {
      // Prepare form data
      const submitData = new FormData();
      submitData.append('title', formData.title);
      submitData.append('description', formData.description);
      submitData.append('medium', formData.medium);
      submitData.append('dimensions', formData.dimensions);
      submitData.append('tags', formData.tags);
      
      if (formData.folder) {
        submitData.append('folder', formData.folder);
      }
      
      if (formData.image) {
        submitData.append('image', formData.image);
      }

      // Submit to API
      const url = mode === 'edit' ? `/api/artworks/${id}/` : '/api/artworks/';
      const method = mode === 'edit' ? 'PATCH' : 'POST';

      const response = await fetch(url, {
        method,
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: submitData
      });

      if (response.ok) {
        const artwork = await response.json();
        navigate(`/artwork/${artwork.id}`);
      } else {
        const errorData = await response.json();
        setErrors(errorData);
      }
    } catch (error) {
      setErrors({ 
        general: 'An error occurred while saving. Please try again.' 
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mt-4">
      <div className="row justify-content-center">
        <div className="col-lg-8">
          <div className="card">
            <div className="card-header">
              <h3 className="mb-0">
                {mode === 'edit' ? 'Edit Artwork' : 'Upload New Artwork'}
              </h3>
            </div>
            
            <div className="card-body">
              {errors.general && (
                <div className="alert alert-danger" role="alert">
                  {errors.general}
                </div>
              )}

              <form onSubmit={handleSubmit}>
                {/* Image Upload Section */}
                <div className="mb-4">
                  <label className="form-label">
                    <ImageIcon className="w-4 h-4 me-2" />
                    Artwork Image {mode === 'create' && '*'}
                  </label>
                  
                  <div className="border rounded p-4 text-center">
                    {imagePreview ? (
                      <div className="position-relative">
                        <img
                          src={imagePreview}
                          alt="Preview"
                          className="img-fluid rounded mb-3"
                          style={{ maxHeight: '300px' }}
                        />
                        <div>
                          <input
                            type="file"
                            id="imageInput"
                            accept="image/*"
                            onChange={handleImageChange}
                            className="d-none"
                          />
                          <label
                            htmlFor="imageInput"
                            className="btn btn-outline-primary"
                          >
                            Change Image
                          </label>
                        </div>
                      </div>
                    ) : (
                      <div>
                        <Upload className="w-12 h-12 text-muted mx-auto mb-3" />
                        <p className="text-muted mb-3">
                          {mode === 'edit' 
                            ? 'Upload a new image to replace the current one'
                            : 'Upload your artwork image'
                          }
                        </p>
                        <input
                          type="file"
                          id="imageInput"
                          accept="image/*"
                          onChange={handleImageChange}
                          className="d-none"
                          required={mode === 'create'}
                        />
                        <label
                          htmlFor="imageInput"
                          className="btn btn-primary"
                        >
                          <Upload className="w-4 h-4 me-2" />
                          Choose Image
                        </label>
                      </div>
                    )}
                  </div>
                  
                  {errors.image && (
                    <div className="text-danger mt-2">{errors.image}</div>
                  )}
                  <small className="form-text text-muted">
                    Supported formats: JPG, PNG, GIF. Max size: 5MB
                  </small>
                </div>

                {/* Title */}
                <div className="mb-3">
                  <label htmlFor="title" className="form-label">
                    Title *
                  </label>
                  <input
                    type="text"
                    className={`form-control ${errors.title ? 'is-invalid' : ''}`}
                    id="title"
                    name="title"
                    value={formData.title}
                    onChange={handleInputChange}
                    required
                    maxLength={200}
                  />
                  {errors.title && (
                    <div className="invalid-feedback">{errors.title[0]}</div>
                  )}
                </div>

                {/* Description */}
                <div className="mb-3">
                  <label htmlFor="description" className="form-label">
                    Description
                  </label>
                  <textarea
                    className={`form-control ${errors.description ? 'is-invalid' : ''}`}
                    id="description"
                    name="description"
                    rows="4"
                    value={formData.description}
                    onChange={handleInputChange}
                    placeholder="Tell us about your artwork..."
                  />
                  {errors.description && (
                    <div className="invalid-feedback">{errors.description[0]}</div>
                  )}
                </div>

                {/* Medium */}
                <div className="mb-3">
                  <label htmlFor="medium" className="form-label">
                    <Palette className="w-4 h-4 me-2" />
                    Medium
                  </label>
                  <input
                    type="text"
                    className={`form-control ${errors.medium ? 'is-invalid' : ''}`}
                    id="medium"
                    name="medium"
                    value={formData.medium}
                    onChange={handleInputChange}
                    placeholder="e.g., Oil on canvas, Digital art, Watercolor..."
                  />
                  {errors.medium && (
                    <div className="invalid-feedback">{errors.medium[0]}</div>
                  )}
                </div>

                {/* Dimensions */}
                <div className="mb-3">
                  <label htmlFor="dimensions" className="form-label">
                    Dimensions
                  </label>
                  <input
                    type="text"
                    className={`form-control ${errors.dimensions ? 'is-invalid' : ''}`}
                    id="dimensions"
                    name="dimensions"
                    value={formData.dimensions}
                    onChange={handleInputChange}
                    placeholder="e.g., 24x36 inches, 1920x1080 pixels..."
                  />
                  {errors.dimensions && (
                    <div className="invalid-feedback">{errors.dimensions[0]}</div>
                  )}
                </div>

                {/* Tags */}
                <div className="mb-3">
                  <label htmlFor="tags" className="form-label">
                    <Tag className="w-4 h-4 me-2" />
                    Tags
                  </label>
                  <input
                    type="text"
                    className={`form-control ${errors.tags ? 'is-invalid' : ''}`}
                    id="tags"
                    name="tags"
                    value={formData.tags}
                    onChange={handleInputChange}
                    placeholder="e.g., portrait, landscape, abstract, digital"
                  />
                  {errors.tags && (
                    <div className="invalid-feedback">{errors.tags[0]}</div>
                  )}
                  <small className="form-text text-muted">
                    Separate tags with commas
                  </small>
                </div>

                {/* Folder Selection */}
                <div className="mb-4">
                  <label htmlFor="folder" className="form-label">
                    <Folder className="w-4 h-4 me-2" />
                    Portfolio Folder
                  </label>
                  
                  <div className="d-flex gap-2">
                    <select
                      className={`form-select ${errors.folder ? 'is-invalid' : ''}`}
                      id="folder"
                      name="folder"
                      value={formData.folder}
                      onChange={handleInputChange}
                    >
                      <option value="">Select a folder (optional)</option>
                      {folders.map(folder => (
                        <option key={folder.id} value={folder.id}>
                          {folder.name} ({folder.artwork_count} artworks)
                        </option>
                      ))}
                    </select>
                    
                    <button
                      type="button"
                      className="btn btn-outline-secondary"
                      onClick={() => setShowCreateFolder(true)}
                      title="Create new folder"
                    >
                      <Plus className="w-4 h-4" />
                    </button>
                  </div>
                  
                  {errors.folder && (
                    <div className="invalid-feedback d-block">{errors.folder[0]}</div>
                  )}
                  <small className="form-text text-muted">
                    Organize your artwork into portfolio folders
                  </small>
                </div>

                {/* Submit Buttons */}
                <div className="d-flex justify-content-between">
                  <button
                    type="button"
                    className="btn btn-secondary"
                    onClick={() => navigate(-1)}
                    disabled={loading}
                  >
                    Cancel
                  </button>
                  
                  <button
                    type="submit"
                    className="btn btn-primary"
                    disabled={loading || !formData.title.trim()}
                  >
                    {loading ? (
                      <>
                        <span className="spinner-border spinner-border-sm me-2" />
                        {mode === 'edit' ? 'Updating...' : 'Uploading...'}
                      </>
                    ) : (
                      <>
                        <Upload className="w-4 h-4 me-2" />
                        {mode === 'edit' ? 'Update Artwork' : 'Upload Artwork'}
                      </>
                    )}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>

      {/* Create Folder Modal */}
      <CreateFolderModal
        show={showCreateFolder}
        onSave={createFolder}
        onClose={() => setShowCreateFolder(false)}
      />
    </div>
  );
};

const CreateFolderModal = ({ show, onSave, onClose }) => {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [visibility, setVisibility] = useState('public');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      await onSave({
        name,
        description,
        is_public: visibility
      });
      setName('');
      setDescription('');
      setVisibility('public');
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
            <h5 className="modal-title">Create New Portfolio Folder</h5>
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
                <label htmlFor="quickFolderName" className="form-label">
                  Folder Name *
                </label>
                <input
                  type="text"
                  className="form-control"
                  id="quickFolderName"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  required
                  maxLength={100}
                  placeholder="e.g., Landscape Series, Portrait Collection"
                />
              </div>

              <div className="mb-3">
                <label htmlFor="quickFolderDescription" className="form-label">
                  Description
                </label>
                <textarea
                  className="form-control"
                  id="quickFolderDescription"
                  rows="2"
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  maxLength={500}
                  placeholder="Brief description of this collection"
                />
              </div>

              <div className="mb-3">
                <label htmlFor="quickFolderVisibility" className="form-label">
                  Visibility
                </label>
                <select
                  className="form-select"
                  id="quickFolderVisibility"
                  value={visibility}
                  onChange={(e) => setVisibility(e.target.value)}
                >
                  <option value="public">🌍 Public</option>
                  <option value="unlisted">👁️ Unlisted</option>
                  <option value="private">🔒 Private</option>
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
                    Creating...
                  </>
                ) : (
                  'Create Folder'
                )}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default ArtworkForm;