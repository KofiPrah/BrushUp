import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { artworkAPI } from '../services/api';
import { handleApiError } from '../services/errorHandler';
import { useAuth } from '../context/AuthContext';

// Import step components
import ProgressIndicator from '../components/upload/ProgressIndicator';
import Step1UploadImage from '../components/upload/Step1UploadImage';
import Step2Details from '../components/upload/Step2Details';
import Step3Meta from '../components/upload/Step3Meta';
import Step4TagsFolder from '../components/upload/Step4TagsFolder';
import Step5Critique from '../components/upload/Step5Critique';
import Step6Review from '../components/upload/Step6Review';

// Import styles
import '../components/upload/upload-wizard.css';

const ArtworkUpload = () => {
  const navigate = useNavigate();
  const { isAuthenticated, user } = useAuth();
  
  // Wizard state
  const [currentStep, setCurrentStep] = useState(1);
  const totalSteps = 6;

  // Form state
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [medium, setMedium] = useState('');
  const [dimensions, setDimensions] = useState('');
  const [tags, setTags] = useState('');
  const [folder, setFolder] = useState(null);
  const [seekingCritique, setSeekingCritique] = useState(false);
  const [critiqueFocus, setCritiqueFocus] = useState([]);
  const [image, setImage] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  
  // UI state
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [fieldErrors, setFieldErrors] = useState({});
  const [successMessage, setSuccessMessage] = useState('');
  const [folders, setFolders] = useState([]);

  // Load folders on component mount
  useEffect(() => {
    const loadFolders = async () => {
      try {
        const response = await artworkAPI.getFolders();
        setFolders(response.data.results || []);
      } catch (error) {
        console.error('Error loading folders:', error);
        setFolders([]);
      }
    };

    if (isAuthenticated) {
      loadFolders();
    }
  }, [isAuthenticated]);
  
  // Handle image change from Step 1
  const handleImageChange = (selectedFile, errorMessage = null) => {
    if (errorMessage) {
      setFieldErrors({
        ...fieldErrors,
        image: errorMessage
      });
      return;
    }

    if (selectedFile) {
      const previewUrl = URL.createObjectURL(selectedFile);
      setImagePreview(previewUrl);
      setImage(selectedFile);
      
      // Clear any previous error
      if (fieldErrors.image) {
        const { image, ...rest } = fieldErrors;
        setFieldErrors(rest);
      }
    } else {
      // Clear image
      setImage(null);
      setImagePreview(null);
    }
  };
  
  // Step validation functions
  const validateStep = (step) => {
    const errors = {};
    
    switch (step) {
      case 1:
        if (!image) errors.image = 'Please select an image for your artwork';
        break;
      case 2:
        if (!title.trim()) errors.title = 'Title is required';
        break;
      default:
        break;
    }
    
    return errors;
  };

  // Navigation functions
  const goToNextStep = () => {
    const errors = validateStep(currentStep);
    if (Object.keys(errors).length > 0) {
      setFieldErrors(errors);
      return;
    }
    
    setFieldErrors({});
    if (currentStep < totalSteps) {
      setCurrentStep(currentStep + 1);
    }
  };

  const goToPreviousStep = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
      setFieldErrors({});
    }
  };

  const goToStep = (step) => {
    if (step >= 1 && step <= totalSteps) {
      setCurrentStep(step);
      setFieldErrors({});
    }
  };

  // Handle form submission (final step)
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Final validation
    const validationErrors = {};
    if (!title.trim()) validationErrors.title = 'Title is required';
    if (!image) validationErrors.image = 'Please select an image for your artwork';
    
    if (Object.keys(validationErrors).length > 0) {
      setFieldErrors(validationErrors);
      // Go back to the step with errors
      if (validationErrors.image) goToStep(1);
      else if (validationErrors.title) goToStep(2);
      return;
    }
    
    // Create FormData object
    const formData = new FormData();
    formData.append('title', title);
    if (description.trim()) formData.append('description', description);
    if (medium.trim()) formData.append('medium', medium);
    if (dimensions.trim()) formData.append('dimensions', dimensions);
    if (tags.trim()) formData.append('tags', tags);
    if (folder) formData.append('folder', folder);
    formData.append('seeking_critique', seekingCritique);
    if (critiqueFocus.length > 0) {
      formData.append('critique_focus', critiqueFocus.join(','));
    }
    formData.append('image', image);
    
    // Submit the form
    try {
      setLoading(true);
      setError(null);
      setFieldErrors({});
      
      const response = await artworkAPI.uploadArtwork(formData);
      
      setSuccessMessage('Artwork uploaded successfully!');
      
      // Navigate to the new artwork's detail page after a brief delay
      setTimeout(() => {
        navigate(`/app/artworks/${response.data.id}`);
      }, 2000);
      
    } catch (err) {
      handleApiError(err, setError, setFieldErrors);
      // If there are field errors, navigate to appropriate step
      if (err.response?.data) {
        const errorData = err.response.data;
        if (errorData.image) goToStep(1);
        else if (errorData.title || errorData.description) goToStep(2);
      }
    } finally {
      setLoading(false);
    }
  };
  
  // Render step content
  const renderStepContent = () => {
    switch (currentStep) {
      case 1:
        return (
          <Step1UploadImage
            image={image}
            imagePreview={imagePreview}
            onImageChange={handleImageChange}
            fieldErrors={fieldErrors}
          />
        );
      case 2:
        return (
          <Step2Details
            title={title}
            description={description}
            onTitleChange={setTitle}
            onDescriptionChange={setDescription}
            fieldErrors={fieldErrors}
          />
        );
      case 3:
        return (
          <Step3Meta
            medium={medium}
            dimensions={dimensions}
            onMediumChange={setMedium}
            onDimensionsChange={setDimensions}
          />
        );
      case 4:
        return (
          <Step4TagsFolder
            tags={tags}
            folder={folder}
            onTagsChange={setTags}
            onFolderChange={setFolder}
            folders={folders}
            setFolders={setFolders}
          />
        );
      case 5:
        return (
          <Step5Critique
            seekingCritique={seekingCritique}
            onSeekingCritiqueChange={setSeekingCritique}
            critiqueFocus={critiqueFocus}
            onCritiqueFocusChange={setCritiqueFocus}
          />
        );
      case 6:
        return (
          <Step6Review
            title={title}
            description={description}
            medium={medium}
            dimensions={dimensions}
            tags={tags}
            folder={folder}
            folders={folders}
            seekingCritique={seekingCritique}
            critiqueFocus={critiqueFocus}
            imagePreview={imagePreview}
            loading={loading}
          />
        );
      default:
        return null;
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
            onClick={() => navigate('/login', { state: { from: '/app/upload' } })}
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
        <div className="col-lg-10 mx-auto">
          <div className="card shadow-lg border-0">
            <div className="card-header bg-gradient bg-primary text-white">
              <h1 className="h3 mb-0">
                <i className="bi bi-upload me-2"></i>
                Share Your Artwork
              </h1>
            </div>
            <div className="card-body p-4">
              {/* Progress indicator */}
              <ProgressIndicator 
                currentStep={currentStep} 
                totalSteps={totalSteps} 
              />

              {/* Success message */}
              {successMessage && (
                <div className="alert alert-success alert-dismissible fade show" role="alert">
                  <i className="bi bi-check-circle me-2"></i>
                  {successMessage}
                </div>
              )}
              
              {/* Error message */}
              {error && (
                <div className="alert alert-danger alert-dismissible fade show" role="alert">
                  <i className="bi bi-exclamation-triangle me-2"></i>
                  {error}
                </div>
              )}
              
              {/* Step content */}
              <form onSubmit={handleSubmit}>
                <div className="step-content mb-4">
                  {renderStepContent()}
                </div>

                {/* Navigation buttons */}
                <div className="d-flex justify-content-between">
                  <div>
                    {currentStep > 1 && (
                      <button 
                        type="button" 
                        className="btn btn-outline-secondary"
                        onClick={goToPreviousStep}
                        disabled={loading}
                      >
                        <i className="bi bi-arrow-left me-2"></i>
                        Previous
                      </button>
                    )}
                  </div>
                  
                  <div>
                    {currentStep < totalSteps ? (
                      <button 
                        type="button" 
                        className="btn btn-primary"
                        onClick={goToNextStep}
                        disabled={loading}
                      >
                        Next
                        <i className="bi bi-arrow-right ms-2"></i>
                      </button>
                    ) : (
                      <button 
                        type="submit" 
                        className="btn btn-success btn-lg"
                        disabled={loading}
                      >
                        {loading ? (
                          <>
                            <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                            Uploading...
                          </>
                        ) : (
                          <>
                            <i className="bi bi-cloud-upload me-2"></i>
                            Upload Artwork
                          </>
                        )}
                      </button>
                    )}
                  </div>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ArtworkUpload;