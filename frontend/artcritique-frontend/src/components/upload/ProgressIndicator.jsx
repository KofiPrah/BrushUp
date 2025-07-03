import React from 'react';

const ProgressIndicator = ({ currentStep, totalSteps }) => {
  const steps = [
    { number: 1, title: 'Upload', icon: 'bi-cloud-upload' },
    { number: 2, title: 'Details', icon: 'bi-pencil-square' },
    { number: 3, title: 'Medium', icon: 'bi-palette' },
    { number: 4, title: 'Tags', icon: 'bi-tags' },
    { number: 5, title: 'Critique', icon: 'bi-chat-heart' },
    { number: 6, title: 'Review', icon: 'bi-check-circle' }
  ];

  const progressPercentage = ((currentStep - 1) / (totalSteps - 1)) * 100;

  return (
    <div className="mb-5">
      {/* Progress bar */}
      <div className="progress mb-4" style={{ height: '6px' }}>
        <div 
          className="progress-bar bg-primary" 
          role="progressbar" 
          style={{ width: `${progressPercentage}%` }}
          aria-valuenow={progressPercentage}
          aria-valuemin="0" 
          aria-valuemax="100"
        ></div>
      </div>

      {/* Step indicators */}
      <div className="row g-0 text-center">
        {steps.map((step) => (
          <div key={step.number} className="col">
            <div className="position-relative">
              {/* Step circle */}
              <div 
                className={`rounded-circle mx-auto d-flex align-items-center justify-content-center ${
                  step.number < currentStep 
                    ? 'bg-success text-white' 
                    : step.number === currentStep 
                      ? 'bg-primary text-white' 
                      : 'bg-light text-muted border'
                }`}
                style={{ width: '40px', height: '40px' }}
              >
                {step.number < currentStep ? (
                  <i className="bi bi-check"></i>
                ) : (
                  <i className={step.icon} style={{ fontSize: '1.1rem' }}></i>
                )}
              </div>
              
              {/* Step label */}
              <div className={`mt-2 small ${
                step.number <= currentStep ? 'text-dark fw-bold' : 'text-muted'
              }`}>
                {step.title}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Step counter */}
      <div className="text-center mt-3">
        <small className="text-muted">
          Step {currentStep} of {totalSteps}
        </small>
      </div>
    </div>
  );
};

export default ProgressIndicator;