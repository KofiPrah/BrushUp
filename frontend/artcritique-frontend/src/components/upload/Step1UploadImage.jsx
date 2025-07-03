import React, { useRef, useState } from 'react';

const Step1UploadImage = ({ image, imagePreview, onImageChange, fieldErrors }) => {
  const fileInputRef = useRef(null);
  const [isDragOver, setIsDragOver] = useState(false);

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragOver(false);
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      handleFileSelect(files[0]);
    }
  };

  const handleFileSelect = (selectedFile) => {
    // Validate file type
    if (selectedFile && !selectedFile.type.match('image.*')) {
      onImageChange(null, 'Please select an image file (JPEG, PNG, etc.)');
      return;
    }

    // Validate file size (20MB limit)
    if (selectedFile && selectedFile.size > 20 * 1024 * 1024) {
      onImageChange(null, 'File size must be less than 20MB');
      return;
    }

    onImageChange(selectedFile);
  };

  const handleFileInputChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      handleFileSelect(selectedFile);
    }
  };

  const handleUploadClick = () => {
    fileInputRef.current?.click();
  };

  return (
    <div className="text-center">
      <div className="mb-4">
        <i className="bi bi-brush display-4 text-primary mb-3"></i>
        <h2 className="h4 mb-2">Upload Your Masterpiece</h2>
        <p className="text-muted">Let's start by adding your artwork</p>
      </div>

      {!imagePreview ? (
        <div
          className={`upload-zone border-3 border-dashed rounded-4 p-5 mb-3 ${
            isDragOver ? 'border-primary bg-primary-subtle' : 'border-secondary'
          } ${fieldErrors.image ? 'border-danger' : ''}`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={handleUploadClick}
          style={{ cursor: 'pointer', minHeight: '300px', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}
        >
          <div>
            <i className="bi bi-cloud-upload display-1 text-muted mb-3"></i>
            <h5 className="text-muted mb-2">Drop your masterpiece here or click to select</h5>
            <p className="text-muted mb-2">Drag & drop your artwork file here</p>
            <button type="button" className="btn btn-outline-primary">
              <i className="bi bi-folder2-open me-2"></i>
              Browse Files
            </button>
            <div className="mt-3">
              <small className="text-muted">
                Supported formats: JPEG, PNG, GIF, WebP, SVG, BMP, TIFF (max 20MB)
              </small>
            </div>
          </div>
        </div>
      ) : (
        <div className="uploaded-preview">
          <div className="position-relative d-inline-block">
            <img
              src={imagePreview}
              alt="Artwork preview"
              className="img-fluid rounded-3 shadow"
              style={{ maxHeight: '400px', maxWidth: '100%' }}
            />
            <button
              type="button"
              className="btn btn-sm btn-danger position-absolute top-0 end-0 m-2"
              onClick={() => onImageChange(null)}
              title="Remove image"
            >
              <i className="bi bi-x"></i>
            </button>
          </div>
          <div className="mt-3">
            <p className="text-success mb-2">
              <i className="bi bi-check-circle me-2"></i>
              Great! Your artwork looks amazing
            </p>
            <button
              type="button"
              className="btn btn-outline-secondary btn-sm"
              onClick={handleUploadClick}
            >
              <i className="bi bi-arrow-repeat me-2"></i>
              Change Image
            </button>
          </div>
        </div>
      )}

      {fieldErrors.image && (
        <div className="alert alert-danger mt-3">
          <i className="bi bi-exclamation-triangle me-2"></i>
          {fieldErrors.image}
        </div>
      )}

      <input
        ref={fileInputRef}
        type="file"
        className="d-none"
        accept="image/*"
        onChange={handleFileInputChange}
      />
    </div>
  );
};

export default Step1UploadImage;