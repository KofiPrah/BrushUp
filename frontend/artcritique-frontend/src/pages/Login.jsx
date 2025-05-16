import React, { useState, useEffect } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { authAPI } from '../services/api';
import { useAuth } from '../context/AuthContext';

const Login = () => {
  const { login, isAuthenticated } = useAuth();
  const location = useLocation();
  const redirectPath = location.state?.from || '/';
  const [formData, setFormData] = useState({
    username: '',
    password: ''
  });
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  
  // Get CSRF token when component mounts
  useEffect(() => {
    const getCSRFToken = async () => {
      try {
        await authAPI.getCSRFToken();
      } catch (error) {
        console.error('Failed to get CSRF token:', error);
      }
    };
    
    getCSRFToken();
  }, []);
  
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value
    });
  };
  
  // Redirect if already authenticated and check URL for OAuth return
  useEffect(() => {
    // If user is already logged in, redirect them
    if (isAuthenticated) {
      navigate(redirectPath);
      return;
    }
    
    // Check if we're returning from OAuth process
    const urlParams = new URLSearchParams(window.location.search);
    const oauthProcess = urlParams.get('process');
    
    if (oauthProcess) {
      // Coming back from OAuth provider, show loading state
      setLoading(true);
      
      // Check if authentication was successful by calling user API
      const checkAuthStatus = async () => {
        try {
          await authAPI.fetchCurrentUser();
          // If we get a successful response, user is authenticated
          // AuthContext will update the state automatically
        } catch (err) {
          // Failed OAuth login
          setError('OAuth authentication failed. Please try again.');
        } finally {
          setLoading(false);
        }
      };
      
      checkAuthStatus();
    }
  }, [isAuthenticated, navigate, redirectPath]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    
    try {
      // Call login method from AuthContext
      const result = await login(formData);
      
      if (result.success) {
        // Redirect to the previous page or home
        navigate(redirectPath);
      } else {
        setError(result.error.message || 'Invalid username or password');
      }
    } catch (err) {
      console.error('Login error:', err);
      setError('Login failed. Please try again later.');
    } finally {
      setLoading(false);
    }
  };
  
  // Function to handle Google OAuth login
  const handleGoogleLogin = () => {
    // Store the current location to redirect back after login
    const currentPath = window.location.pathname;
    if (currentPath !== '/login') {
      sessionStorage.setItem('redirect_after_login', currentPath);
    }
    
    // Get the base URL (domain) of the application
    const appBaseUrl = window.location.origin;
    
    // Construct the Google OAuth URL
    // Django-allauth will handle the OAuth flow and redirect back to our app
    // Add process=login parameter to help identify the return from OAuth
    // The next parameter tells Django where to redirect after successful authentication
    window.location.href = `/accounts/google/login/?process=login&next=${appBaseUrl}/login?process=oauth_return`;
  };
  
  return (
    <div className="container mt-5">
      <div className="row justify-content-center">
        <div className="col-md-6">
          <div className="card shadow">
            <div className="card-header bg-primary text-white text-center">
              <h3 className="mb-0">Login to Art Critique</h3>
            </div>
            <div className="card-body">
              {error && (
                <div className="alert alert-danger" role="alert">
                  {error}
                </div>
              )}
              
              <form onSubmit={handleSubmit}>
                <div className="mb-3">
                  <label htmlFor="username" className="form-label">Username</label>
                  <input
                    type="text"
                    className="form-control"
                    id="username"
                    name="username"
                    value={formData.username}
                    onChange={handleChange}
                    required
                  />
                </div>
                
                <div className="mb-3">
                  <label htmlFor="password" className="form-label">Password</label>
                  <input
                    type="password"
                    className="form-control"
                    id="password"
                    name="password"
                    value={formData.password}
                    onChange={handleChange}
                    required
                  />
                </div>
                
                <div className="mb-3 form-check">
                  <input
                    type="checkbox"
                    className="form-check-input"
                    id="rememberMe"
                  />
                  <label className="form-check-label" htmlFor="rememberMe">
                    Remember me
                  </label>
                </div>
                
                <div className="d-grid">
                  <button
                    type="submit"
                    className="btn btn-primary"
                    disabled={loading}
                  >
                    {loading ? (
                      <>
                        <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                        Logging in...
                      </>
                    ) : 'Login'}
                  </button>
                </div>
              </form>
              
              <div className="mt-3 text-center">
                <p>
                  Don't have an account? <Link to="/register">Register</Link>
                </p>
                <div className="mt-3">
                  <button 
                    type="button"
                    className="btn btn-outline-danger"
                    onClick={handleGoogleLogin}
                  >
                    <i className="bi bi-google me-2"></i>Login with Google
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;