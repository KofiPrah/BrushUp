import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';

const AdminPanel = () => {
  const { user, isAdmin, isModerator, isModeratorOrAdmin } = useAuth();
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  // Redirect non-admin users
  useEffect(() => {
    if (!isAdmin()) {
      navigate('/');
      return;
    }
  }, [isAdmin, navigate]);

  // Fetch admin statistics
  useEffect(() => {
    const fetchStats = async () => {
      try {
        // This would be replaced with actual API calls
        setStats({
          totalUsers: 150,
          totalArtworks: 320,
          totalCritiques: 480,
          reportsCount: 12,
          flaggedContent: 8
        });
      } catch (error) {
        console.error('Error fetching admin stats:', error);
      } finally {
        setLoading(false);
      }
    };

    if (isAdmin()) {
      fetchStats();
    }
  }, [isAdmin]);

  // Show nothing if not admin (should be redirected anyway)
  if (!isAdmin()) {
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

  return (
    <div className="container py-5">
      <div className="row">
        <div className="col-12">
          <div className="d-flex justify-content-between align-items-center mb-4">
            <h1>
              <i className="bi bi-gear-fill me-2"></i>
              Admin Dashboard
            </h1>
            <span className="badge bg-danger">
              <i className="bi bi-shield-fill me-1"></i>
              Admin Access
            </span>
          </div>

          {/* Admin Stats Cards */}
          <div className="row mb-4">
            <div className="col-md-3 mb-3">
              <div className="card border-0 shadow-sm">
                <div className="card-body text-center">
                  <i className="bi bi-people-fill display-4 text-primary mb-2"></i>
                  <h5 className="card-title">Total Users</h5>
                  <h3 className="text-primary">{stats?.totalUsers || 0}</h3>
                </div>
              </div>
            </div>
            <div className="col-md-3 mb-3">
              <div className="card border-0 shadow-sm">
                <div className="card-body text-center">
                  <i className="bi bi-image-fill display-4 text-success mb-2"></i>
                  <h5 className="card-title">Total Artworks</h5>
                  <h3 className="text-success">{stats?.totalArtworks || 0}</h3>
                </div>
              </div>
            </div>
            <div className="col-md-3 mb-3">
              <div className="card border-0 shadow-sm">
                <div className="card-body text-center">
                  <i className="bi bi-chat-dots-fill display-4 text-info mb-2"></i>
                  <h5 className="card-title">Total Critiques</h5>
                  <h3 className="text-info">{stats?.totalCritiques || 0}</h3>
                </div>
              </div>
            </div>
            <div className="col-md-3 mb-3">
              <div className="card border-0 shadow-sm">
                <div className="card-body text-center">
                  <i className="bi bi-flag-fill display-4 text-warning mb-2"></i>
                  <h5 className="card-title">Reports Pending</h5>
                  <h3 className="text-warning">{stats?.reportsCount || 0}</h3>
                </div>
              </div>
            </div>
          </div>

          {/* Admin Actions */}
          <div className="row">
            <div className="col-lg-6 mb-4">
              <div className="card border-0 shadow-sm">
                <div className="card-header bg-primary text-white">
                  <h5 className="mb-0">
                    <i className="bi bi-people me-2"></i>
                    User Management
                  </h5>
                </div>
                <div className="card-body">
                  <p className="card-text">Manage user accounts, roles, and permissions.</p>
                  <div className="d-grid gap-2">
                    <button 
                      className="btn btn-outline-primary"
                      onClick={() => navigate('/admin/users')}
                    >
                      <i className="bi bi-people me-1"></i>
                      Manage Users
                    </button>
                    <button 
                      className="btn btn-outline-secondary"
                      onClick={() => navigate('/admin/roles')}
                    >
                      <i className="bi bi-shield me-1"></i>
                      Manage Roles
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <div className="col-lg-6 mb-4">
              <div className="card border-0 shadow-sm">
                <div className="card-header bg-warning text-dark">
                  <h5 className="mb-0">
                    <i className="bi bi-flag me-2"></i>
                    Content Moderation
                  </h5>
                </div>
                <div className="card-body">
                  <p className="card-text">Review flagged content and user reports.</p>
                  <div className="d-grid gap-2">
                    <button 
                      className="btn btn-outline-warning"
                      onClick={() => navigate('/moderation/reports')}
                    >
                      <i className="bi bi-exclamation-triangle me-1"></i>
                      Review Reports ({stats?.reportsCount || 0})
                    </button>
                    <button 
                      className="btn btn-outline-danger"
                      onClick={() => navigate('/moderation/flagged-content')}
                    >
                      <i className="bi bi-flag me-1"></i>
                      Flagged Content ({stats?.flaggedContent || 0})
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <div className="col-lg-6 mb-4">
              <div className="card border-0 shadow-sm">
                <div className="card-header bg-info text-white">
                  <h5 className="mb-0">
                    <i className="bi bi-gear me-2"></i>
                    System Settings
                  </h5>
                </div>
                <div className="card-body">
                  <p className="card-text">Configure application settings and features.</p>
                  <div className="d-grid gap-2">
                    <button 
                      className="btn btn-outline-info"
                      onClick={() => navigate('/admin/system-settings')}
                    >
                      <i className="bi bi-sliders me-1"></i>
                      System Configuration
                    </button>
                    <button 
                      className="btn btn-outline-secondary"
                      onClick={() => navigate('/admin/logs')}
                    >
                      <i className="bi bi-file-text me-1"></i>
                      View System Logs
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <div className="col-lg-6 mb-4">
              <div className="card border-0 shadow-sm">
                <div className="card-header bg-success text-white">
                  <h5 className="mb-0">
                    <i className="bi bi-bar-chart me-2"></i>
                    Analytics
                  </h5>
                </div>
                <div className="card-body">
                  <p className="card-text">View platform analytics and statistics.</p>
                  <div className="d-grid gap-2">
                    <button 
                      className="btn btn-outline-success"
                      onClick={() => navigate('/admin/analytics')}
                    >
                      <i className="bi bi-graph-up me-1"></i>
                      User Analytics
                    </button>
                    <button 
                      className="btn btn-outline-success"
                      onClick={() => navigate('/admin/content-stats')}
                    >
                      <i className="bi bi-pie-chart me-1"></i>
                      Content Statistics
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Recent Activity */}
          <div className="card border-0 shadow-sm">
            <div className="card-header bg-dark text-white">
              <h5 className="mb-0">
                <i className="bi bi-clock-history me-2"></i>
                Recent Admin Activity
              </h5>
            </div>
            <div className="card-body">
              <div className="list-group list-group-flush">
                <div className="list-group-item d-flex justify-content-between align-items-start">
                  <div className="ms-2 me-auto">
                    <div className="fw-bold">User role updated</div>
                    <small className="text-muted">User 'artist123' promoted to MODERATOR</small>
                  </div>
                  <small className="text-muted">2 hours ago</small>
                </div>
                <div className="list-group-item d-flex justify-content-between align-items-start">
                  <div className="ms-2 me-auto">
                    <div className="fw-bold">Content flagged</div>
                    <small className="text-muted">Artwork reported for inappropriate content</small>
                  </div>
                  <small className="text-muted">5 hours ago</small>
                </div>
                <div className="list-group-item d-flex justify-content-between align-items-start">
                  <div className="ms-2 me-auto">
                    <div className="fw-bold">System maintenance</div>
                    <small className="text-muted">Database optimization completed</small>
                  </div>
                  <small className="text-muted">1 day ago</small>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminPanel;