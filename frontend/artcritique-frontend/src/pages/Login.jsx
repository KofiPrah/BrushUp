import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { authAPI } from '../services/api';

const Login = ({ onLogin }) => {
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
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    
    try {
      // Call Django login API
      const response = await authAPI.login(formData);
      
      // Get user data after successful login
      const userResponse = await authAPI.fetchCurrentUser();
      const userData = userResponse.data;
      
      if (onLogin) {
        onLogin(userData);
      }
      
      navigate('/');
    } catch (err) {
      console.error('Login error:', err);
      if (err.response && err.response.data) {
        if (err.response.data.non_field_errors) {
          setError(err.response.data.non_field_errors[0]);
        } else if (err.response.data.detail) {
          setError(err.response.data.detail);
        } else {
          setError('Invalid username or password. Please try again.');
        }
      } else {
        setError('Login failed. Please try again later.');
      }
    } finally {
      setLoading(false);
    }
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
                  <button className="btn btn-outline-danger">
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