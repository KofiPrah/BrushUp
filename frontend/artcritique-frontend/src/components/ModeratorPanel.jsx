import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';

const ModeratorPanel = () => {
  const { user, isModeratorOrAdmin } = useAuth();
  const [reports, setReports] = useState([]);
  const [flaggedContent, setFlaggedContent] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  // Redirect non-moderator users
  useEffect(() => {
    if (!isModeratorOrAdmin()) {
      navigate('/');
      return;
    }
  }, [isModeratorOrAdmin, navigate]);

  // Fetch moderation data
  useEffect(() => {
    const fetchModerationData = async () => {
      try {
        // This would be replaced with actual API calls
        setReports([
          {
            id: 1,
            type: 'inappropriate_content',
            reportedBy: 'user123',
            targetUser: 'artist456',
            targetContent: 'Artwork: "Abstract Dreams"',
            reason: 'Contains inappropriate imagery',
            status: 'pending',
            createdAt: '2024-01-15T10:30:00Z'
          },
          {
            id: 2,
            type: 'harassment',
            reportedBy: 'user789',
            targetUser: 'critic999',
            targetContent: 'Critique on "Sunset Painting"',
            reason: 'Offensive language and personal attacks',
            status: 'pending',
            createdAt: '2024-01-15T09:15:00Z'
          }
        ]);

        setFlaggedContent([
          {
            id: 1,
            type: 'artwork',
            title: 'Abstract Dreams',
            author: 'artist456',
            flagCount: 3,
            reasons: ['inappropriate', 'spam'],
            status: 'under_review'
          },
          {
            id: 2,
            type: 'critique',
            title: 'Harsh critique on landscape painting',
            author: 'critic999',
            flagCount: 2,
            reasons: ['harassment'],
            status: 'under_review'
          }
        ]);
      } catch (error) {
        console.error('Error fetching moderation data:', error);
      } finally {
        setLoading(false);
      }
    };

    if (isModeratorOrAdmin()) {
      fetchModerationData();
    }
  }, [isModeratorOrAdmin]);

  // Show nothing if not moderator (should be redirected anyway)
  if (!isModeratorOrAdmin()) {
    return null;
  }

  if (loading) {
    return (
      <div className="container py-5">
        <div className="d-flex justify-content-center">
          <div className="spinner-border" role="status">
            <span className="visually-hidden">Loading...</span>
          </div>
        </div>
      </div>
    );
  }

  const handleReportAction = (reportId, action) => {
    console.log(`Report ${reportId} ${action}`);
    // This would be replaced with actual API call
    setReports(reports.map(report => 
      report.id === reportId 
        ? { ...report, status: action === 'approve' ? 'resolved' : 'dismissed' }
        : report
    ));
  };

  const handleContentAction = (contentId, action) => {
    console.log(`Content ${contentId} ${action}`);
    // This would be replaced with actual API call
    setFlaggedContent(flaggedContent.map(content => 
      content.id === contentId 
        ? { ...content, status: action === 'remove' ? 'removed' : 'approved' }
        : content
    ));
  };

  return (
    <div className="container py-5">
      <div className="row">
        <div className="col-12">
          <div className="d-flex justify-content-between align-items-center mb-4">
            <h1>
              <i className="bi bi-shield-check me-2"></i>
              Moderation Panel
            </h1>
            <span className="badge bg-warning">
              <i className="bi bi-shield me-1"></i>
              Moderator Access
            </span>
          </div>

          {/* Reports Section */}
          <div className="card border-0 shadow-sm mb-4">
            <div className="card-header bg-danger text-white">
              <h5 className="mb-0">
                <i className="bi bi-exclamation-triangle me-2"></i>
                Pending Reports ({reports.filter(r => r.status === 'pending').length})
              </h5>
            </div>
            <div className="card-body">
              {reports.filter(r => r.status === 'pending').length === 0 ? (
                <p className="text-muted mb-0">No pending reports to review.</p>
              ) : (
                <div className="list-group list-group-flush">
                  {reports.filter(r => r.status === 'pending').map(report => (
                    <div key={report.id} className="list-group-item">
                      <div className="d-flex w-100 justify-content-between">
                        <h6 className="mb-1">
                          <span className="badge bg-secondary me-2">{report.type.replace('_', ' ')}</span>
                          {report.targetContent}
                        </h6>
                        <small>{new Date(report.createdAt).toLocaleDateString()}</small>
                      </div>
                      <p className="mb-1"><strong>Reported by:</strong> {report.reportedBy}</p>
                      <p className="mb-1"><strong>Target user:</strong> {report.targetUser}</p>
                      <p className="mb-3"><strong>Reason:</strong> {report.reason}</p>
                      <div className="btn-group" role="group">
                        <button 
                          className="btn btn-success btn-sm"
                          onClick={() => handleReportAction(report.id, 'approve')}
                        >
                          <i className="bi bi-check-lg me-1"></i>
                          Take Action
                        </button>
                        <button 
                          className="btn btn-secondary btn-sm"
                          onClick={() => handleReportAction(report.id, 'dismiss')}
                        >
                          <i className="bi bi-x-lg me-1"></i>
                          Dismiss
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Flagged Content Section */}
          <div className="card border-0 shadow-sm mb-4">
            <div className="card-header bg-warning text-dark">
              <h5 className="mb-0">
                <i className="bi bi-flag me-2"></i>
                Flagged Content ({flaggedContent.filter(c => c.status === 'under_review').length})
              </h5>
            </div>
            <div className="card-body">
              {flaggedContent.filter(c => c.status === 'under_review').length === 0 ? (
                <p className="text-muted mb-0">No flagged content to review.</p>
              ) : (
                <div className="list-group list-group-flush">
                  {flaggedContent.filter(c => c.status === 'under_review').map(content => (
                    <div key={content.id} className="list-group-item">
                      <div className="d-flex w-100 justify-content-between">
                        <h6 className="mb-1">
                          <span className="badge bg-info me-2">{content.type}</span>
                          {content.title}
                        </h6>
                        <span className="badge bg-danger">{content.flagCount} flags</span>
                      </div>
                      <p className="mb-1"><strong>Author:</strong> {content.author}</p>
                      <p className="mb-3">
                        <strong>Reasons:</strong> {content.reasons.join(', ')}
                      </p>
                      <div className="btn-group" role="group">
                        <button 
                          className="btn btn-danger btn-sm"
                          onClick={() => handleContentAction(content.id, 'remove')}
                        >
                          <i className="bi bi-trash me-1"></i>
                          Remove Content
                        </button>
                        <button 
                          className="btn btn-success btn-sm"
                          onClick={() => handleContentAction(content.id, 'approve')}
                        >
                          <i className="bi bi-check-lg me-1"></i>
                          Approve Content
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Quick Actions */}
          <div className="row">
            <div className="col-md-6 mb-3">
              <div className="card border-0 shadow-sm">
                <div className="card-header bg-primary text-white">
                  <h6 className="mb-0">
                    <i className="bi bi-lightning me-2"></i>
                    Quick Actions
                  </h6>
                </div>
                <div className="card-body">
                  <div className="d-grid gap-2">
                    <button className="btn btn-outline-primary btn-sm">
                      <i className="bi bi-search me-1"></i>
                      Search Users
                    </button>
                    <button className="btn btn-outline-primary btn-sm">
                      <i className="bi bi-eye me-1"></i>
                      View All Reports
                    </button>
                    <button className="btn btn-outline-primary btn-sm">
                      <i className="bi bi-graph-up me-1"></i>
                      Moderation Stats
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <div className="col-md-6 mb-3">
              <div className="card border-0 shadow-sm">
                <div className="card-header bg-info text-white">
                  <h6 className="mb-0">
                    <i className="bi bi-clock-history me-2"></i>
                    Recent Actions
                  </h6>
                </div>
                <div className="card-body">
                  <small className="text-muted">
                    <div className="mb-2">• Approved artwork "Mountain Vista" - 2 hours ago</div>
                    <div className="mb-2">• Removed inappropriate comment - 4 hours ago</div>
                    <div className="mb-2">• Dismissed spam report - 6 hours ago</div>
                  </small>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ModeratorPanel;