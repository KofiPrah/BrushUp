import React, { useState } from 'react';

const Step3Meta = ({ medium, dimensions, onMediumChange, onDimensionsChange }) => {
  const [showCustomMedium, setShowCustomMedium] = useState(false);
  
  const commonMediums = [
    'Oil Painting',
    'Acrylic Painting',
    'Watercolor',
    'Digital Art',
    'Photography',
    'Pencil Drawing',
    'Charcoal Drawing',
    'Ink Drawing',
    'Mixed Media',
    'Sculpture',
    'Printmaking',
    'Collage',
    'Other'
  ];

  const handleMediumSelect = (selectedMedium) => {
    if (selectedMedium === 'Other') {
      setShowCustomMedium(true);
      onMediumChange('');
    } else {
      setShowCustomMedium(false);
      onMediumChange(selectedMedium);
    }
  };

  return (
    <div className="text-center">
      <div className="mb-4">
        <i className="bi bi-palette display-4 text-primary mb-3"></i>
        <h2 className="h4 mb-2">Artwork Details</h2>
        <p className="text-muted">Help viewers understand your medium and scale</p>
      </div>

      <div className="text-start">
        {/* Medium selection */}
        <div className="mb-4">
          <label className="form-label fw-bold">
            <i className="bi bi-brush me-2"></i>
            What medium did you use?
          </label>
          
          {!showCustomMedium ? (
            <div className="row g-2 mt-2">
              {commonMediums.map((mediumOption) => (
                <div key={mediumOption} className="col-6 col-md-4 col-lg-3">
                  <button
                    type="button"
                    className={`btn w-100 ${
                      medium === mediumOption 
                        ? 'btn-primary' 
                        : 'btn-outline-secondary'
                    }`}
                    onClick={() => handleMediumSelect(mediumOption)}
                  >
                    {mediumOption}
                  </button>
                </div>
              ))}
            </div>
          ) : (
            <div className="mt-2">
              <input
                type="text"
                className="form-control"
                value={medium}
                onChange={(e) => onMediumChange(e.target.value)}
                placeholder="Enter your custom medium"
                autoFocus
              />
              <button
                type="button"
                className="btn btn-sm btn-outline-secondary mt-2"
                onClick={() => setShowCustomMedium(false)}
              >
                <i className="bi bi-arrow-left me-1"></i>
                Back to common mediums
              </button>
            </div>
          )}
          
          <div className="form-text">
            This helps viewers understand your artistic technique
          </div>
        </div>

        {/* Dimensions field */}
        <div className="mb-4">
          <label htmlFor="dimensions" className="form-label fw-bold">
            <i className="bi bi-aspect-ratio me-2"></i>
            What are the dimensions?
          </label>
          <input
            type="text"
            className="form-control"
            id="dimensions"
            value={dimensions}
            onChange={(e) => onDimensionsChange(e.target.value)}
            placeholder="e.g., 24×36 inches, 1920×1080 pixels, 8×10 cm"
          />
          <div className="form-text">
            Optional • Include units (inches, cm, pixels, etc.)
          </div>
        </div>

        {/* Info card */}
        <div className="card bg-light border-0">
          <div className="card-body">
            <h6 className="card-title">
              <i className="bi bi-info-circle text-info me-2"></i>
              Why does this matter?
            </h6>
            <p className="mb-0 small text-muted">
              Medium and dimensions help viewers appreciate the scale and technique of your work. 
              Digital artists might include pixel dimensions, while traditional artists often use inches or centimeters.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Step3Meta;