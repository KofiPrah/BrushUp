import React from 'react';
import { useAuth } from '../context/AuthContext';
import RoleGuard from './RoleGuard';

/**
 * Demonstration component showing role-based conditional rendering
 * This component showcases how different UI elements appear based on user roles
 */
const RoleDemo = () => {
  const { user, isAuthenticated, isAdmin, isModerator, isModeratorOrAdmin, hasRole } = useAuth();

  if (!isAuthenticated) {
    return (
      <div className="container py-5">
        <div className="alert alert-info">
          <h4>Role-Based Access Demo</h4>
          <p>Please log in to see role-based features in action.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container py-5">
      <div className="row">
        <div className="col-12">
          <h1 className="mb-4">
            <i className="bi bi-shield-check me-2"></i>
            Role-Based Access Control Demo
          </h1>
          
          {/* User Info */}
          <div className="card mb-4">
            <div className="card-header bg-primary text-white">
              <h5 className="mb-0">Current User Information</h5>
            </div>
            <div className="card-body">
              <p><strong>Username:</strong> {user?.username || 'N/A'}</p>
              <p><strong>Role:</strong> {user?.profile?.role || 'USER'}</p>
              <p><strong>Is Admin:</strong> {isAdmin() ? 'Yes' : 'No'}</p>
              <p><strong>Is Moderator:</strong> {isModerator() ? 'Yes' : 'No'}</p>
              <p><strong>Is Moderator or Admin:</strong> {isModeratorOrAdmin() ? 'Yes' : 'No'}</p>
            </div>
          </div>

          {/* Regular User Features */}
          <div className="card mb-4">
            <div className="card-header bg-success text-white">
              <h5 className="mb-0">Features Available to All Users</h5>
            </div>
            <div className="card-body">
              <div className="row">
                <div className="col-md-4 mb-2">
                  <button className="btn btn-outline-success btn-sm w-100">
                    <i className="bi bi-upload me-1"></i>
                    Upload Artwork
                  </button>
                </div>
                <div className="col-md-4 mb-2">
                  <button className="btn btn-outline-success btn-sm w-100">
                    <i className="bi bi-chat-dots me-1"></i>
                    Write Critiques
                  </button>
                </div>
                <div className="col-md-4 mb-2">
                  <button className="btn btn-outline-success btn-sm w-100">
                    <i className="bi bi-heart me-1"></i>
                    Like Artworks
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* Moderator Features */}
          <RoleGuard 
            roles={['MODERATOR', 'ADMIN']}
            fallback={
              <div className="card mb-4">
                <div className="card-header bg-secondary text-white">
                  <h5 className="mb-0">Moderator Features (Not Available)</h5>
                </div>
                <div className="card-body">
                  <p className="text-muted">
                    <i className="bi bi-lock me-1"></i>
                    These features are only available to Moderators and Administrators.
                  </p>
                </div>
              </div>
            }
          >
            <div className="card mb-4">
              <div className="card-header bg-warning text-dark">
                <h5 className="mb-0">
                  <i className="bi bi-shield me-2"></i>
                  Moderator Features
                </h5>
              </div>
              <div className="card-body">
                <div className="row">
                  <div className="col-md-4 mb-2">
                    <button className="btn btn-outline-warning btn-sm w-100">
                      <i className="bi bi-flag me-1"></i>
                      Review Reports
                    </button>
                  </div>
                  <div className="col-md-4 mb-2">
                    <button className="btn btn-outline-warning btn-sm w-100">
                      <i className="bi bi-eye-slash me-1"></i>
                      Hide Content
                    </button>
                  </div>
                  <div className="col-md-4 mb-2">
                    <button className="btn btn-outline-warning btn-sm w-100">
                      <i className="bi bi-shield-check me-1"></i>
                      Moderate Users
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </RoleGuard>

          {/* Admin Features */}
          <RoleGuard 
            roles={['ADMIN']}
            fallback={
              <div className="card mb-4">
                <div className="card-header bg-secondary text-white">
                  <h5 className="mb-0">Admin Features (Not Available)</h5>
                </div>
                <div className="card-body">
                  <p className="text-muted">
                    <i className="bi bi-lock me-1"></i>
                    These features are only available to Administrators.
                  </p>
                </div>
              </div>
            }
          >
            <div className="card mb-4">
              <div className="card-header bg-danger text-white">
                <h5 className="mb-0">
                  <i className="bi bi-gear me-2"></i>
                  Administrator Features
                </h5>
              </div>
              <div className="card-body">
                <div className="row">
                  <div className="col-md-3 mb-2">
                    <button className="btn btn-outline-danger btn-sm w-100">
                      <i className="bi bi-people me-1"></i>
                      Manage Users
                    </button>
                  </div>
                  <div className="col-md-3 mb-2">
                    <button className="btn btn-outline-danger btn-sm w-100">
                      <i className="bi bi-trash me-1"></i>
                      Delete Content
                    </button>
                  </div>
                  <div className="col-md-3 mb-2">
                    <button className="btn btn-outline-danger btn-sm w-100">
                      <i className="bi bi-sliders me-1"></i>
                      System Settings
                    </button>
                  </div>
                  <div className="col-md-3 mb-2">
                    <button className="btn btn-outline-danger btn-sm w-100">
                      <i className="bi bi-bar-chart me-1"></i>
                      Analytics
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </RoleGuard>

          {/* Role-Specific Messages */}
          <div className="row">
            <div className="col-md-4">
              <RoleGuard roles={['USER']}>
                <div className="alert alert-info">
                  <h6>Welcome, User!</h6>
                  <p className="mb-0">You can upload art and provide critiques.</p>
                </div>
              </RoleGuard>
            </div>
            <div className="col-md-4">
              <RoleGuard roles={['MODERATOR']}>
                <div className="alert alert-warning">
                  <h6>Moderator Access</h6>
                  <p className="mb-0">You can moderate content and review reports.</p>
                </div>
              </RoleGuard>
            </div>
            <div className="col-md-4">
              <RoleGuard roles={['ADMIN']}>
                <div className="alert alert-danger">
                  <h6>Administrator Access</h6>
                  <p className="mb-0">You have full system access and control.</p>
                </div>
              </RoleGuard>
            </div>
          </div>

          {/* Nested Role Example */}
          <div className="card">
            <div className="card-header bg-dark text-white">
              <h5 className="mb-0">Nested Role Guard Example</h5>
            </div>
            <div className="card-body">
              <p>This demonstrates nested role guards:</p>
              <RoleGuard roles={['MODERATOR', 'ADMIN']}>
                <div className="alert alert-warning mb-2">
                  <strong>Moderator Level:</strong> You can see moderation features.
                  <RoleGuard roles={['ADMIN']}>
                    <div className="alert alert-danger mt-2 mb-0">
                      <strong>Admin Level:</strong> You can also see admin-only features within moderation.
                    </div>
                  </RoleGuard>
                </div>
              </RoleGuard>
              <RoleGuard 
                roles={['ADMIN', 'MODERATOR']}
                fallback={
                  <div className="alert alert-secondary">
                    <strong>Regular User:</strong> You don't have moderation privileges.
                  </div>
                }
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RoleDemo;