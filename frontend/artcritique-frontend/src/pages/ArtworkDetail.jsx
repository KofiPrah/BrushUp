import React, { useState, useEffect, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Container, Row, Col, Card, Form, Button, Badge, Spinner, InputGroup } from 'react-bootstrap';
import { getValidImageUrl, handleImageError } from '../utils/imageUtils';
import PlaceholderImage from '../components/PlaceholderImage';
import RoleGuard from '../components/RoleGuard';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';

const ArtworkDetail = () => {
  const { id } = useParams();
  const { user, isAuthenticated, isAdmin, isModerator, isModeratorOrAdmin } = useAuth();
  const [artwork, setArtwork] = useState(null);
  const [critiques, setCritiques] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [critiqueText, setCritiqueText] = useState('');
  const [scores, setScores] = useState({
    composition: 5,
    technique: 5,
    originality: 5
  });

  useEffect(() => {
    // In a real implementation, this would fetch data from your Django API
    // Example: fetchArtwork(id) and fetchCritiques(id)
    
    // Simulating API call with timeout
    setLoading(true);
    setTimeout(() => {
      // This would be replaced with actual API data
      const mockArtwork = {
        id: parseInt(id),
        title: 'Mountain Landscape',
        image_display_url: 'https://via.placeholder.com/800x600',
        author: { 
          username: 'nature_artist',
          profile: {
            karma: 120
          }
        },
        description: 'A serene mountain landscape at sunset, painted with acrylics on canvas. I focused on capturing the warm evening light as it bathes the mountains in a golden glow.',
        medium: 'Acrylic on Canvas',
        dimensions: '24" x 36"',
        created_at: '2025-04-15T14:30:00Z',
        likes_count: 24,
        is_liked: false,
        critiques_count: 3,
        tags: ['landscape', 'mountains', 'sunset', 'nature']
      };
      
      const mockCritiques = [
        {
          id: 1,
          author: {
            username: 'art_teacher',
            profile: {
              karma: 345
            }
          },
          text: 'Beautiful use of color in the sunset. The warm tones contrasting with the cool shadows create a wonderful depth. Consider adding a bit more detail in the foreground to enhance the sense of scale.',
          composition_score: 4,
          technique_score: 5,
          originality_score: 4,
          created_at: '2025-04-16T10:15:00Z',
          helpful_count: 12,
          inspiring_count: 8,
          detailed_count: 5,
          user_reactions: []
        },
        {
          id: 2,
          author: {
            username: 'color_master',
            profile: {
              karma: 210
            }
          },
          text: "I love the atmosphere you have created here. The gradient in the sky is executed beautifully. One suggestion would be to vary your brushwork more in the mountain textures to create more visual interest.",
          composition_score: 5,
          technique_score: 4,
          originality_score: 5,
          created_at: '2025-04-17T15:45:00Z',
          helpful_count: 7,
          inspiring_count: 10,
          detailed_count: 3,
          user_reactions: ['HELPFUL']
        }
      ];
      
      setArtwork(mockArtwork);
      setCritiques(mockCritiques);
      setLoading(false);
    }, 1000);
  }, [id]);

  const handleCritiqueSubmit = (e) => {
    e.preventDefault();
    
    // This would be replaced with actual API call to submit critique
    alert('In a real app, this would submit a critique with the following data: ' + 
          JSON.stringify({
            artwork_id: id,
            text: critiqueText,
            ...scores
          }));
    
    // Clear form
    setCritiqueText('');
    setScores({
      composition: 5,
      technique: 5,
      originality: 5
    });
  };

  const handleScoreChange = (category, value) => {
    setScores({
      ...scores,
      [category]: parseInt(value)
    });
  };

  const handleReaction = (critiqueId, reactionType) => {
    // This would be replaced with actual API call to toggle reaction
    alert(`In a real app, this would toggle a ${reactionType} reaction on critique ${critiqueId}`);
  };

  const handleLike = () => {
    // This would be replaced with actual API call to toggle like
    alert(`In a real app, this would toggle like status for artwork ${id}`);
  };

  if (loading) {
    return (
      <div className="container mt-5 text-center">
        <div className="spinner-border" role="status">
          <span className="visually-hidden">Loading...</span>
        </div>
        <p className="mt-3">Loading artwork details...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mt-5">
        <div className="alert alert-danger" role="alert">
          Error loading artwork: {error}
        </div>
        <Link to="/artworks" className="btn btn-primary">
          Back to Gallery
        </Link>
      </div>
    );
  }

  if (!artwork) {
    return (
      <div className="container mt-5">
        <div className="alert alert-warning" role="alert">
          Artwork not found.
        </div>
        <Link to="/artworks" className="btn btn-primary">
          Back to Gallery
        </Link>
      </div>
    );
  }

  return (
    <div className="container mt-4 mb-5">
      <nav aria-label="breadcrumb">
        <ol className="breadcrumb">
          <li className="breadcrumb-item"><Link to="/">Home</Link></li>
          <li className="breadcrumb-item"><Link to="/artworks">Artworks</Link></li>
          <li className="breadcrumb-item active" aria-current="page">{artwork.title}</li>
        </ol>
      </nav>
      
      {/* Artwork Details */}
      <div className="row">
        <div className="col-md-8">
          {artwork.image_display_url ? (
            <img 
              src={getValidImageUrl(artwork.image_display_url)}
              className="img-fluid rounded shadow" 
              alt={artwork.title}
              onError={handleImageError}
            />
          ) : (
            <PlaceholderImage 
              alt={`${artwork.title} (image unavailable)`}
              className="img-fluid rounded shadow"
              style={{ height: '400px' }}
            />
          )}
        </div>
        <div className="col-md-4">
          <h1 className="mb-2">{artwork.title}</h1>
          <div className="d-flex align-items-center mb-3">
            <h5 className="mb-0 me-2">by {artwork.author.username}</h5>
            <span className="badge bg-info">
              <i className="bi bi-star-fill me-1"></i>
              {artwork.author.profile.karma} karma
            </span>
          </div>
          
          <div className="mb-3">
            {artwork.tags.map(tag => (
              <span key={tag} className="badge bg-secondary me-1 mb-1">
                {tag}
              </span>
            ))}
          </div>
          
          <p>{artwork.description}</p>
          
          <div className="mb-3">
            <strong>Medium:</strong> {artwork.medium}
          </div>
          
          {artwork.dimensions && (
            <div className="mb-3">
              <strong>Dimensions:</strong> {artwork.dimensions}
            </div>
          )}
          
          <div className="mb-3">
            <strong>Created:</strong> {new Date(artwork.created_at).toLocaleDateString()}
          </div>
          
          <div className="d-flex justify-content-between align-items-center mb-4">
            <button 
              className={`btn ${artwork.is_liked ? 'btn-danger' : 'btn-outline-danger'}`}
              onClick={handleLike}
            >
              <i className={`bi ${artwork.is_liked ? 'bi-heart-fill' : 'bi-heart'} me-1`}></i>
              {artwork.likes_count} {artwork.likes_count === 1 ? 'Like' : 'Likes'}
            </button>
            
            <span className="text-muted">
              <i className="bi bi-chat-square-text me-1"></i>
              {artwork.critiques_count} {artwork.critiques_count === 1 ? 'Critique' : 'Critiques'}
            </span>
          </div>

          {/* Role-based Action Buttons */}
          <RoleGuard roles={['ADMIN', 'MODERATOR']}>
            <div className="card border-warning mb-3">
              <div className="card-header bg-warning text-dark">
                <h6 className="mb-0">
                  <i className="bi bi-shield-check me-2"></i>
                  Moderation Actions
                </h6>
              </div>
              <div className="card-body">
                <div className="d-grid gap-2">
                  <button 
                    className="btn btn-outline-warning btn-sm"
                    onClick={() => alert('Flag content for review')}
                  >
                    <i className="bi bi-flag me-1"></i>
                    Flag Content
                  </button>
                  <button 
                    className="btn btn-outline-danger btn-sm"
                    onClick={() => alert('Hide artwork from public view')}
                  >
                    <i className="bi bi-eye-slash me-1"></i>
                    Hide Artwork
                  </button>
                  <RoleGuard roles={['ADMIN']}>
                    <button 
                      className="btn btn-outline-dark btn-sm"
                      onClick={() => alert('Delete artwork permanently')}
                    >
                      <i className="bi bi-trash me-1"></i>
                      Delete Artwork
                    </button>
                  </RoleGuard>
                </div>
              </div>
            </div>
          </RoleGuard>

          {/* Admin Analytics */}
          <RoleGuard roles={['ADMIN']}>
            <div className="card border-info mb-3">
              <div className="card-header bg-info text-white">
                <h6 className="mb-0">
                  <i className="bi bi-bar-chart me-2"></i>
                  Admin Analytics
                </h6>
              </div>
              <div className="card-body">
                <small className="text-muted">
                  <div>Views: 1,245</div>
                  <div>Reports: 0</div>
                  <div>Download attempts: 23</div>
                  <div>Share count: 45</div>
                </small>
              </div>
            </div>
          </RoleGuard>
        </div>
      </div>
      
      {/* Critiques Section */}
      <div className="row mt-5">
        <div className="col-12">
          <h2 className="mb-4">Critiques ({critiques.length})</h2>
          
          {critiques.length === 0 ? (
            <div className="alert alert-info">
              No critiques yet. Be the first to provide feedback!
            </div>
          ) : (
            <div className="critique-list">
              {critiques.map(critique => (
                <div key={critique.id} className="card mb-4">
                  <div className="card-header d-flex justify-content-between align-items-center">
                    <div>
                      <strong>{critique.author.username}</strong>
                      <span className="ms-2 badge bg-info">
                        <i className="bi bi-star-fill me-1"></i>
                        {critique.author.profile.karma}
                      </span>
                    </div>
                    <small className="text-muted">
                      {new Date(critique.created_at).toLocaleDateString()}
                    </small>
                  </div>
                  <div className="card-body">
                    <p className="card-text">{critique.text}</p>
                    
                    <div className="row mb-3">
                      <div className="col-md-4">
                        <div className="score-display">
                          <strong>Composition:</strong>
                          <div className="progress">
                            <div 
                              className="progress-bar bg-success" 
                              style={{ width: `${critique.composition_score * 20}%` }}
                            >
                              {critique.composition_score}/5
                            </div>
                          </div>
                        </div>
                      </div>
                      <div className="col-md-4">
                        <div className="score-display">
                          <strong>Technique:</strong>
                          <div className="progress">
                            <div 
                              className="progress-bar bg-info" 
                              style={{ width: `${critique.technique_score * 20}%` }}
                            >
                              {critique.technique_score}/5
                            </div>
                          </div>
                        </div>
                      </div>
                      <div className="col-md-4">
                        <div className="score-display">
                          <strong>Originality:</strong>
                          <div className="progress">
                            <div 
                              className="progress-bar bg-primary" 
                              style={{ width: `${critique.originality_score * 20}%` }}
                            >
                              {critique.originality_score}/5
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                  <div className="card-footer">
                    <div className="d-flex justify-content-between align-items-center">
                      <div className="d-flex">
                        <button 
                          className={`btn btn-sm me-2 ${critique.user_reactions.includes('HELPFUL') ? 'btn-success' : 'btn-outline-success'}`}
                          onClick={() => handleReaction(critique.id, 'HELPFUL')}
                        >
                          <i className="bi bi-hand-thumbs-up me-1"></i>
                          Helpful ({critique.helpful_count})
                        </button>
                        <button 
                          className={`btn btn-sm me-2 ${critique.user_reactions.includes('INSPIRING') ? 'btn-primary' : 'btn-outline-primary'}`}
                          onClick={() => handleReaction(critique.id, 'INSPIRING')}
                        >
                          <i className="bi bi-lightbulb me-1"></i>
                          Inspiring ({critique.inspiring_count})
                        </button>
                        <button 
                          className={`btn btn-sm ${critique.user_reactions.includes('DETAILED') ? 'btn-info' : 'btn-outline-info'}`}
                          onClick={() => handleReaction(critique.id, 'DETAILED')}
                        >
                          <i className="bi bi-list-check me-1"></i>
                          Detailed ({critique.detailed_count})
                        </button>
                      </div>
                      
                      {/* Role-based Critique Moderation */}
                      <RoleGuard roles={['ADMIN', 'MODERATOR']}>
                        <div className="dropdown">
                          <button 
                            className="btn btn-outline-secondary btn-sm dropdown-toggle" 
                            type="button" 
                            data-bs-toggle="dropdown" 
                            aria-expanded="false"
                          >
                            <i className="bi bi-shield me-1"></i>
                            Moderate
                          </button>
                          <ul className="dropdown-menu">
                            <li>
                              <button 
                                className="dropdown-item" 
                                onClick={() => alert(`Hide critique ${critique.id}`)}
                              >
                                <i className="bi bi-eye-slash me-1"></i>
                                Hide Critique
                              </button>
                            </li>
                            <li>
                              <button 
                                className="dropdown-item" 
                                onClick={() => alert(`Flag critique ${critique.id}`)}
                              >
                                <i className="bi bi-flag me-1"></i>
                                Flag for Review
                              </button>
                            </li>
                            <RoleGuard roles={['ADMIN']}>
                              <li><hr className="dropdown-divider" /></li>
                              <li>
                                <button 
                                  className="dropdown-item text-danger" 
                                  onClick={() => alert(`Delete critique ${critique.id}`)}
                                >
                                  <i className="bi bi-trash me-1"></i>
                                  Delete Critique
                                </button>
                              </li>
                            </RoleGuard>
                          </ul>
                        </div>
                      </RoleGuard>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
          
          {/* Add Critique Form */}
          <div className="card mt-4">
            <div className="card-header">
              <h3 className="mb-0">Add Your Critique</h3>
            </div>
            <div className="card-body">
              <form onSubmit={handleCritiqueSubmit}>
                <div className="mb-3">
                  <label htmlFor="critiqueText" className="form-label">Your Feedback</label>
                  <textarea 
                    className="form-control" 
                    id="critiqueText" 
                    rows="4" 
                    value={critiqueText}
                    onChange={(e) => setCritiqueText(e.target.value)}
                    required
                    placeholder="Provide constructive feedback about this artwork..."
                  ></textarea>
                </div>
                
                <div className="row mb-3">
                  <div className="col-md-4">
                    <label htmlFor="compositionScore" className="form-label">Composition (1-5)</label>
                    <input 
                      type="range" 
                      className="form-range" 
                      min="1" 
                      max="5" 
                      id="compositionScore"
                      value={scores.composition}
                      onChange={(e) => handleScoreChange('composition', e.target.value)}
                    />
                    <div className="text-center">{scores.composition}/5</div>
                  </div>
                  <div className="col-md-4">
                    <label htmlFor="techniqueScore" className="form-label">Technique (1-5)</label>
                    <input 
                      type="range" 
                      className="form-range" 
                      min="1" 
                      max="5" 
                      id="techniqueScore"
                      value={scores.technique}
                      onChange={(e) => handleScoreChange('technique', e.target.value)}
                    />
                    <div className="text-center">{scores.technique}/5</div>
                  </div>
                  <div className="col-md-4">
                    <label htmlFor="originalityScore" className="form-label">Originality (1-5)</label>
                    <input 
                      type="range" 
                      className="form-range" 
                      min="1" 
                      max="5" 
                      id="originalityScore"
                      value={scores.originality}
                      onChange={(e) => handleScoreChange('originality', e.target.value)}
                    />
                    <div className="text-center">{scores.originality}/5</div>
                  </div>
                </div>
                
                <button type="submit" className="btn btn-primary">
                  Submit Critique
                </button>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ArtworkDetail;