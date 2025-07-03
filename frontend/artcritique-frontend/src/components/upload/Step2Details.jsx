import React from 'react';

const Step2Details = ({ title, description, onTitleChange, onDescriptionChange, fieldErrors }) => {
  return (
    <div className="text-center">
      <div className="mb-4">
        <i className="bi bi-pencil-square display-4 text-primary mb-3"></i>
        <h2 className="h4 mb-2">Tell Us About Your Creation</h2>
        <p className="text-muted">Give your artwork a title and share its story</p>
      </div>

      <div className="text-start">
        {/* Title field */}
        <div className="mb-4">
          <label htmlFor="title" className="form-label fw-bold">
            <i className="bi bi-tag me-2"></i>
            What's this piece called? *
          </label>
          <input
            type="text"
            className={`form-control form-control-lg ${fieldErrors.title ? 'is-invalid' : ''}`}
            id="title"
            value={title}
            onChange={(e) => onTitleChange(e.target.value)}
            placeholder="Enter a compelling title for your artwork"
            maxLength={200}
          />
          {fieldErrors.title && (
            <div className="invalid-feedback">{fieldErrors.title}</div>
          )}
          <div className="form-text">
            {title.length}/200 characters
          </div>
        </div>

        {/* Description field */}
        <div className="mb-4">
          <label htmlFor="description" className="form-label fw-bold">
            <i className="bi bi-journal-text me-2"></i>
            Tell us the story behind it
          </label>
          <p className="text-muted small mb-2">
            Share your inspiration, technique, or what makes this piece special
          </p>
          <textarea
            className={`form-control ${fieldErrors.description ? 'is-invalid' : ''}`}
            id="description"
            rows="5"
            value={description}
            onChange={(e) => onDescriptionChange(e.target.value)}
            placeholder="What inspired this piece? What techniques did you use? What story does it tell?"
            maxLength={1000}
          ></textarea>
          {fieldErrors.description && (
            <div className="invalid-feedback">{fieldErrors.description}</div>
          )}
          <div className="form-text">
            {description.length}/1000 characters
            {!description && (
              <span className="text-muted ms-2">
                • Optional, but recommended for better engagement
              </span>
            )}
          </div>
        </div>

        {/* Tips card */}
        <div className="card bg-light border-0 mt-4">
          <div className="card-body">
            <h6 className="card-title">
              <i className="bi bi-lightbulb text-warning me-2"></i>
              Tips for great descriptions
            </h6>
            <ul className="mb-0 small text-muted">
              <li>Share your creative process or inspiration</li>
              <li>Mention any unique techniques you used</li>
              <li>Describe the mood or feeling you wanted to convey</li>
              <li>Include any interesting backstory or challenges faced</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Step2Details;