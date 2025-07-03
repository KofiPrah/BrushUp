import React, { useState } from 'react';

const Step5Critique = ({ seekingCritique, onSeekingCritiqueChange, critiqueFocus, onCritiqueFocusChange }) => {
  const [showFocusAreas, setShowFocusAreas] = useState(seekingCritique);

  const focusAreas = [
    { id: 'technique', label: 'Technique & Skills', icon: 'bi-brush' },
    { id: 'composition', label: 'Composition & Layout', icon: 'bi-grid-3x3' },
    { id: 'color', label: 'Color & Lighting', icon: 'bi-palette' },
    { id: 'style', label: 'Artistic Style', icon: 'bi-star' },
    { id: 'concept', label: 'Concept & Storytelling', icon: 'bi-chat-quote' },
    { id: 'improvement', label: 'Areas for Improvement', icon: 'bi-graph-up' }
  ];

  const handleSeekingToggle = (seeking) => {
    onSeekingCritiqueChange(seeking);
    setShowFocusAreas(seeking);
    if (!seeking) {
      onCritiqueFocusChange([]);
    }
  };

  const handleFocusToggle = (focusId) => {
    const currentFocus = critiqueFocus || [];
    if (currentFocus.includes(focusId)) {
      onCritiqueFocusChange(currentFocus.filter(id => id !== focusId));
    } else {
      onCritiqueFocusChange([...currentFocus, focusId]);
    }
  };

  return (
    <div className="text-center">
      <div className="mb-4">
        <i className="bi bi-chat-heart display-4 text-primary mb-3"></i>
        <h2 className="h4 mb-2">Want Feedback?</h2>
        <p className="text-muted">Let the community help you grow as an artist</p>
      </div>

      <div className="text-start">
        {/* Main critique toggle */}
        <div className="card border-2 mb-4">
          <div className="card-body">
            <div className="row align-items-center">
              <div className="col">
                <h5 className="card-title mb-2">
                  <i className="bi bi-people me-2"></i>
                  Seeking Critique
                </h5>
                <p className="card-text text-muted mb-0">
                  Would you like other artists to provide feedback on this piece?
                </p>
              </div>
              <div className="col-auto">
                <div className="form-check form-switch">
                  <input
                    className="form-check-input"
                    type="checkbox"
                    id="seekingCritique"
                    checked={seekingCritique}
                    onChange={(e) => handleSeekingToggle(e.target.checked)}
                    style={{ transform: 'scale(1.5)' }}
                  />
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Focus areas (shown when seeking critique) */}
        {showFocusAreas && seekingCritique && (
          <div className="mb-4">
            <h6 className="fw-bold mb-3">
              <i className="bi bi-bullseye me-2"></i>
              What areas would you like feedback on? (Optional)
            </h6>
            <p className="text-muted small mb-3">
              Select specific areas you'd like reviewers to focus on
            </p>
            
            <div className="row g-2">
              {focusAreas.map((area) => (
                <div key={area.id} className="col-md-6">
                  <button
                    type="button"
                    className={`btn w-100 text-start d-flex align-items-center ${
                      (critiqueFocus || []).includes(area.id)
                        ? 'btn-primary'
                        : 'btn-outline-secondary'
                    }`}
                    onClick={() => handleFocusToggle(area.id)}
                  >
                    <i className={`${area.icon} me-2`}></i>
                    {area.label}
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* How it works info */}
        <div className="card bg-light border-0">
          <div className="card-body">
            <h6 className="card-title">
              <i className="bi bi-info-circle text-info me-2"></i>
              How critiques work
            </h6>
            <div className="row">
              <div className="col-md-6">
                <ul className="mb-0 small text-muted">
                  <li>Other artists can provide constructive feedback</li>
                  <li>You'll receive thoughtful insights to improve your skills</li>
                  <li>Both giving and receiving critiques earns karma points</li>
                </ul>
              </div>
              <div className="col-md-6">
                <ul className="mb-0 small text-muted">
                  <li>Community reactions help identify helpful feedback</li>
                  <li>You can always turn off critique requests later</li>
                  <li>Quality feedback builds your artistic reputation</li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        {seekingCritique && (
          <div className="alert alert-success mt-3">
            <i className="bi bi-check-circle me-2"></i>
            <strong>Great choice!</strong> Your artwork will be open for community feedback. 
            This is a wonderful way to grow as an artist and connect with other creatives.
          </div>
        )}
      </div>
    </div>
  );
};

export default Step5Critique;