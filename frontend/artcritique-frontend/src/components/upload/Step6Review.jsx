import React from 'react';

const Step6Review = ({ 
  title, 
  description, 
  medium, 
  dimensions, 
  tags, 
  folder, 
  folders, 
  seekingCritique, 
  critiqueFocus, 
  imagePreview, 
  loading 
}) => {
  const selectedFolder = folders.find(f => f.id === parseInt(folder));
  const tagsList = tags ? tags.split(',').map(tag => tag.trim()).filter(tag => tag) : [];
  const focusAreas = [
    { id: 'technique', label: 'Technique & Skills' },
    { id: 'composition', label: 'Composition & Layout' },
    { id: 'color', label: 'Color & Lighting' },
    { id: 'style', label: 'Artistic Style' },
    { id: 'concept', label: 'Concept & Storytelling' },
    { id: 'improvement', label: 'Areas for Improvement' }
  ];

  const selectedFocusAreas = focusAreas.filter(area => 
    (critiqueFocus || []).includes(area.id)
  );

  return (
    <div className="text-center">
      <div className="mb-4">
        <i className="bi bi-check-circle display-4 text-success mb-3"></i>
        <h2 className="h4 mb-2">Ready to Share Your Art?</h2>
        <p className="text-muted">Review your artwork details before uploading</p>
      </div>

      <div className="row">
        {/* Artwork Preview */}
        <div className="col-lg-6 mb-4">
          <div className="card h-100">
            <div className="card-header">
              <h6 className="mb-0">
                <i className="bi bi-image me-2"></i>
                Artwork Preview
              </h6>
            </div>
            <div className="card-body text-center">
              {imagePreview && (
                <img
                  src={imagePreview}
                  alt="Artwork preview"
                  className="img-fluid rounded-3 shadow"
                  style={{ maxHeight: '300px', maxWidth: '100%' }}
                />
              )}
            </div>
          </div>
        </div>

        {/* Details Summary */}
        <div className="col-lg-6 mb-4">
          <div className="card h-100">
            <div className="card-header">
              <h6 className="mb-0">
                <i className="bi bi-list-check me-2"></i>
                Artwork Details
              </h6>
            </div>
            <div className="card-body">
              <div className="text-start">
                {/* Title */}
                <div className="mb-3">
                  <strong className="text-muted small d-block">TITLE</strong>
                  <div className="fw-bold">{title || 'Untitled'}</div>
                </div>

                {/* Description */}
                {description && (
                  <div className="mb-3">
                    <strong className="text-muted small d-block">DESCRIPTION</strong>
                    <div className="small text-muted" style={{ maxHeight: '60px', overflow: 'hidden' }}>
                      {description.length > 100 
                        ? `${description.substring(0, 100)}...` 
                        : description
                      }
                    </div>
                  </div>
                )}

                {/* Medium */}
                {medium && (
                  <div className="mb-3">
                    <strong className="text-muted small d-block">MEDIUM</strong>
                    <div>{medium}</div>
                  </div>
                )}

                {/* Dimensions */}
                {dimensions && (
                  <div className="mb-3">
                    <strong className="text-muted small d-block">DIMENSIONS</strong>
                    <div>{dimensions}</div>
                  </div>
                )}

                {/* Folder */}
                {selectedFolder && (
                  <div className="mb-3">
                    <strong className="text-muted small d-block">FOLDER</strong>
                    <div>
                      <i className="bi bi-folder me-2"></i>
                      {selectedFolder.name}
                    </div>
                  </div>
                )}

                {/* Tags */}
                {tagsList.length > 0 && (
                  <div className="mb-3">
                    <strong className="text-muted small d-block">TAGS</strong>
                    <div className="d-flex flex-wrap gap-1">
                      {tagsList.slice(0, 5).map((tag, index) => (
                        <span key={index} className="badge bg-secondary small">
                          {tag}
                        </span>
                      ))}
                      {tagsList.length > 5 && (
                        <span className="badge bg-light text-muted small">
                          +{tagsList.length - 5} more
                        </span>
                      )}
                    </div>
                  </div>
                )}

                {/* Critique status */}
                <div className="mb-3">
                  <strong className="text-muted small d-block">SEEKING CRITIQUE</strong>
                  <div className={seekingCritique ? 'text-success' : 'text-muted'}>
                    <i className={`bi ${seekingCritique ? 'bi-check-circle' : 'bi-x-circle'} me-2`}></i>
                    {seekingCritique ? 'Yes, open to feedback' : 'No, just sharing'}
                  </div>
                  
                  {seekingCritique && selectedFocusAreas.length > 0 && (
                    <div className="mt-2">
                      <small className="text-muted d-block">Focus areas:</small>
                      <div className="small">
                        {selectedFocusAreas.map(area => area.label).join(', ')}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Upload button */}
      <div className="d-grid gap-2 col-md-6 mx-auto">
        <button 
          type="submit" 
          className="btn btn-primary btn-lg" 
          disabled={loading}
        >
          {loading ? (
            <>
              <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
              Uploading your brilliance...
            </>
          ) : (
            <>
              <i className="bi bi-cloud-upload me-2"></i>
              Upload Artwork
            </>
          )}
        </button>
      </div>

      {!loading && (
        <div className="mt-3">
          <small className="text-muted">
            <i className="bi bi-info-circle me-1"></i>
            Your artwork will be visible to the community once uploaded
          </small>
        </div>
      )}
    </div>
  );
};

export default Step6Review;