import React, { useState, useEffect } from 'react';
import { artworkAPI } from '../../services/api';

const Step4TagsFolder = ({ tags, folder, onTagsChange, onFolderChange, folders, setFolders }) => {
  const [tagInput, setTagInput] = useState('');
  const [tagsList, setTagsList] = useState([]);
  const [showCreateFolder, setShowCreateFolder] = useState(false);
  const [newFolderName, setNewFolderName] = useState('');
  const [creatingFolder, setCreatingFolder] = useState(false);

  // Common art tags suggestions
  const suggestedTags = [
    'abstract', 'landscape', 'portrait', 'still-life', 'digital', 'traditional',
    'fantasy', 'realistic', 'colorful', 'monochrome', 'experimental', 'nature',
    'urban', 'conceptual', 'surreal', 'minimalist'
  ];

  // Initialize tags list from props
  useEffect(() => {
    if (tags) {
      const parsedTags = tags.split(',').map(tag => tag.trim()).filter(tag => tag);
      setTagsList(parsedTags);
    }
  }, [tags]);

  // Update parent component when tagsList changes
  useEffect(() => {
    onTagsChange(tagsList.join(', '));
  }, [tagsList, onTagsChange]);

  const addTag = (tag) => {
    const cleanTag = tag.trim().toLowerCase();
    if (cleanTag && !tagsList.includes(cleanTag)) {
      setTagsList([...tagsList, cleanTag]);
    }
    setTagInput('');
  };

  const removeTag = (tagToRemove) => {
    setTagsList(tagsList.filter(tag => tag !== tagToRemove));
  };

  const handleTagInputKeyPress = (e) => {
    if (e.key === 'Enter' || e.key === ',') {
      e.preventDefault();
      addTag(tagInput);
    }
  };

  const handleCreateFolder = async () => {
    if (!newFolderName.trim()) return;

    setCreatingFolder(true);
    try {
      // Call API to create folder
      const response = await artworkAPI.createFolder({
        name: newFolderName.trim(),
        description: `Created during artwork upload`
      });

      // Add new folder to list
      setFolders([...folders, response.data]);
      onFolderChange(response.data.id);
      setNewFolderName('');
      setShowCreateFolder(false);
    } catch (error) {
      console.error('Error creating folder:', error);
    } finally {
      setCreatingFolder(false);
    }
  };

  return (
    <div className="text-center">
      <div className="mb-4">
        <i className="bi bi-tags display-4 text-primary mb-3"></i>
        <h2 className="h4 mb-2">Organize & Categorize</h2>
        <p className="text-muted">Add tags and choose a folder to help people find your work</p>
      </div>

      <div className="text-start">
        {/* Tags section */}
        <div className="mb-5">
          <label className="form-label fw-bold">
            <i className="bi bi-tag me-2"></i>
            Tags
          </label>
          <p className="text-muted small mb-3">
            Help people discover your artwork with descriptive tags
          </p>

          {/* Tag input */}
          <div className="mb-3">
            <input
              type="text"
              className="form-control"
              value={tagInput}
              onChange={(e) => setTagInput(e.target.value)}
              onKeyPress={handleTagInputKeyPress}
              placeholder="Type a tag and press Enter"
            />
            <div className="form-text">
              Press Enter or comma to add tags
            </div>
          </div>

          {/* Current tags */}
          {tagsList.length > 0 && (
            <div className="mb-3">
              <div className="d-flex flex-wrap gap-2">
                {tagsList.map((tag, index) => (
                  <span key={index} className="badge bg-primary d-flex align-items-center">
                    {tag}
                    <button
                      type="button"
                      className="btn-close btn-close-white ms-2"
                      style={{ fontSize: '0.65em' }}
                      onClick={() => removeTag(tag)}
                      aria-label={`Remove ${tag} tag`}
                    ></button>
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Suggested tags */}
          <div>
            <h6 className="text-muted mb-2">Popular tags:</h6>
            <div className="d-flex flex-wrap gap-2">
              {suggestedTags.map((suggestedTag) => (
                <button
                  key={suggestedTag}
                  type="button"
                  className={`btn btn-sm ${
                    tagsList.includes(suggestedTag) 
                      ? 'btn-primary' 
                      : 'btn-outline-secondary'
                  }`}
                  onClick={() => addTag(suggestedTag)}
                  disabled={tagsList.includes(suggestedTag)}
                >
                  {suggestedTag}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Folder section */}
        <div className="mb-4">
          <label className="form-label fw-bold">
            <i className="bi bi-folder me-2"></i>
            Portfolio Folder
          </label>
          <p className="text-muted small mb-3">
            Optional • Organize your artwork into folders
          </p>

          {!showCreateFolder ? (
            <div>
              <select
                className="form-select mb-2"
                value={folder || ''}
                onChange={(e) => onFolderChange(e.target.value || null)}
              >
                <option value="">No folder (keep in main gallery)</option>
                {folders.map((folderOption) => (
                  <option key={folderOption.id} value={folderOption.id}>
                    {folderOption.name}
                  </option>
                ))}
              </select>
              <button
                type="button"
                className="btn btn-outline-primary btn-sm"
                onClick={() => setShowCreateFolder(true)}
              >
                <i className="bi bi-plus-circle me-2"></i>
                Create New Folder
              </button>
            </div>
          ) : (
            <div className="card">
              <div className="card-body">
                <h6 className="card-title">Create New Folder</h6>
                <div className="mb-3">
                  <input
                    type="text"
                    className="form-control"
                    value={newFolderName}
                    onChange={(e) => setNewFolderName(e.target.value)}
                    placeholder="Enter folder name"
                    autoFocus
                  />
                </div>
                <div className="d-flex gap-2">
                  <button
                    type="button"
                    className="btn btn-primary"
                    onClick={handleCreateFolder}
                    disabled={!newFolderName.trim() || creatingFolder}
                  >
                    {creatingFolder ? (
                      <>
                        <span className="spinner-border spinner-border-sm me-2"></span>
                        Creating...
                      </>
                    ) : (
                      <>
                        <i className="bi bi-check me-2"></i>
                        Create
                      </>
                    )}
                  </button>
                  <button
                    type="button"
                    className="btn btn-outline-secondary"
                    onClick={() => setShowCreateFolder(false)}
                  >
                    Cancel
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Tips card */}
        <div className="card bg-light border-0">
          <div className="card-body">
            <h6 className="card-title">
              <i className="bi bi-lightbulb text-warning me-2"></i>
              Organization tips
            </h6>
            <ul className="mb-0 small text-muted">
              <li><strong>Tags:</strong> Use specific, searchable keywords that describe your style, subject, or technique</li>
              <li><strong>Folders:</strong> Group related artworks together (e.g., "Character Studies", "Landscapes", "Commissions")</li>
              <li>Both tags and folders help viewers discover your work more easily</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Step4TagsFolder;