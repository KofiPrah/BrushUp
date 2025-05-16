import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { artworkAPI } from '../services/api';
import { handleApiError } from '../services/errorHandler';
import { useAuth } from '../context/AuthContext';

const ArtworkUpload = () => {
  const navigate = useNavigate();
  const { isAuthenticated, user } = useAuth();
  
  // Form state
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [medium, setMedium] = useState('');
  const [dimensions, setDimensions] = useState('');
  const [tags, setTags] = useState('');
  const [image, setImage] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  
  // UI state
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [fieldErrors, setFieldErrors] = useState({});
  const [successMessage, setSuccessMessage] = useState('');
  
  // Handle file input change
  const handleImageChange = (e) => {
    const selectedFile = e.target.files[0];
    
    // Validate file type
    if (selectedFile && !selectedFile.type.match('image.*')) {
      setFieldErrors({
        ...fieldErrors,
        image: 'Please select an image file (JPEG, PNG, etc.)'
      });
      return;
    }
    
    // Create preview URL and set image state
    if (selectedFile) {
      const previewUrl = URL.createObjectURL(selectedFile);
      setImagePreview(previewUrl);
      setImage(selectedFile);
      
      // Clear any previous error
      if (fieldErrors.image) {
        const { image, ...rest } = fieldErrors;
        setFieldErrors(rest);
      }
    }
  };
  
  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validate form
    const validationErrors = {};
    if (!title.trim()) validationErrors.title = 'Title is required';
    if (!description.trim()) validationErrors.description = 'Description is required';
    if (!image) validationErrors.image = 'Please select an image for your artwork';
    
    if (Object.keys(validationErrors).length > 0) {
      setFieldErrors(validationErrors);
      return;
    }
    
    // Create FormData object
    const formData = new FormData();
    formData.append('title', title);
    formData.append('description', description);
    if (medium) formData.append('medium', medium);
    if (dimensions) formData.append('dimensions', dimensions);
    if (tags) formData.append('tags', tags);
    formData.append('image', image);
    
    // Submit the form
    try {
      setLoading(true);
      setError(null);
      setFieldErrors({});
      
      const response = await artworkAPI.uploadArtwork(formData);
      
      setSuccessMessage('Artwork uploaded successfully!');
      
      // Clear form
      setTitle('');
      setDescription('');
      setMedium('');
      setDimensions('');
      setTags('');
      setImage(null);
      setImagePreview(null);
      
      // Navigate to the new artwork's detail page after a brief delay
      setTimeout(() => {
        navigate(`/artworks/${response.data.id}`);
      }, 1500);
      
    } catch (err) {
      handleApiError(err, setError, setFieldErrors);
    } finally {
      setLoading(false);
    }
  };
  
  // Check if user is authenticated
  if (!isAuthenticated) {
    return (
      <div className="container mt-5">
        <div className="alert alert-warning">
          <h4 className="alert-heading">Authentication Required</h4>
          <p>You need to be logged in to upload artwork.</p>
          <hr />
          <button 
            className="btn btn-primary" 
            onClick={() => navigate('/login', { state: { from: '/upload' } })}
          >
            Go to Login
          </button>
        </div>
      </div>
    );
  }
  
  return (
    <div className="container mt-4 mb-5">
      <div className="row">
        <div className="col-lg-8 mx-auto">
          <div className="card shadow">
            <div className="card-header bg-primary text-white">
              <h2 className="mb-0">Upload New Artwork</h2>
            </div>
            <div className="card-body">
              {successMessage && (
                <div className="alert alert-success">{successMessage}</div>
              )}
              
              {error && (
                <div className="alert alert-danger">{error}</div>
              )}
              
              <form onSubmit={handleSubmit}>
                {/* Title field */}
                <div className="mb-3">
                  <label htmlFor="title" className="form-label">Title *</label>
                  <input
                    type="text"
                    className={`form-control ${fieldErrors.title ? 'is-invalid' : ''}`}
                    id="title"
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                    placeholder="Enter the title of your artwork"
                  />
                  {fieldErrors.title && (
                    <div className="invalid-feedback">{fieldErrors.title}</div>
                  )}
                </div>
                
                {/* Description field */}
                <div className="mb-3">
                  <label htmlFor="description" className="form-label">Description *</label>
                  <textarea
                    className={`form-control ${fieldErrors.description ? 'is-invalid' : ''}`}
                    id="description"
                    rows="4"
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    placeholder="Describe your artwork"
                  ></textarea>
                  {fieldErrors.description && (
                    <div className="invalid-feedback">{fieldErrors.description}</div>
                  )}
                </div>
                
                {/* Medium field */}
                <div className="mb-3">
                  <label htmlFor="medium" className="form-label">Medium</label>
                  <input
                    type="text"
                    className="form-control"
                    id="medium"
                    value={medium}
                    onChange={(e) => setMedium(e.target.value)}
                    placeholder="E.g., Oil painting, Digital art, Photography"
                  />
                </div>
                
                {/* Dimensions field */}
                <div className="mb-3">
                  <label htmlFor="dimensions" className="form-label">Dimensions</label>
                  <input
                    type="text"
                    className="form-control"
                    id="dimensions"
                    value={dimensions}
                    onChange={(e) => setDimensions(e.target.value)}
                    placeholder="E.g., 24x36 inches, 1920x1080 pixels"
                  />
                </div>
                
                {/* Tags field */}
                <div className="mb-3">
                  <label htmlFor="tags" className="form-label">Tags</label>
                  <input
                    type="text"
                    className="form-control"
                    id="tags"
                    value={tags}
                    onChange={(e) => setTags(e.target.value)}
                    placeholder="Enter tags separated by commas: abstract, landscape, portrait"
                  />
                  <small className="text-muted">Separate tags with commas</small>
                </div>
                
                {/* Image upload field */}
                <div className="mb-4">
                  <label htmlFor="image" className="form-label">Artwork Image *</label>
                  <input
                    type="file"
                    className={`form-control ${fieldErrors.image ? 'is-invalid' : ''}`}
                    id="image"
                    accept="image/*"
                    onChange={handleImageChange}
                  />
                  {fieldErrors.image && (
                    <div className="invalid-feedback">{fieldErrors.image}</div>
                  )}
                  
                  {/* Image preview */}
                  {imagePreview && (
                    <div className="mt-3">
                      <h6>Preview:</h6>
                      <img 
                        src={imagePreview} 
                        alt="Preview" 
                        className="img-thumbnail" 
                        style={{ maxHeight: '300px' }} 
                      />
                    </div>
                  )}
                </div>
                
                {/* Submit button */}
                <div className="d-grid gap-2">
                  <button 
                    type="submit" 
                    className="btn btn-primary btn-lg" 
                    disabled={loading}
                  >
                    {loading ? (
                      <>
                        <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                        Uploading...
                      </>
                    ) : 'Upload Artwork'}
                  </button>
                </div>
              </form>
            </div>
            <div className="card-footer text-muted">
              <small>Fields marked with * are required</small>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ArtworkUpload;