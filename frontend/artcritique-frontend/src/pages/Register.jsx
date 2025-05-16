import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { authAPI } from '../services/api';

const Register = ({ onLogin }) => {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: ''
  });
  const [error, setError] = useState(null);
  const [fieldErrors, setFieldErrors] = useState({});
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
    
    // Clear field-specific error when user starts typing again
    if (fieldErrors[name]) {
      setFieldErrors({
        ...fieldErrors,
        [name]: null
      });
    }
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Password validation
    if (formData.password !== formData.confirmPassword) {
      setFieldErrors({
        ...fieldErrors,
        confirmPassword: 'Passwords do not match'
      });
      return;
    }
    
    setLoading(true);
    setError(null);
    setFieldErrors({});
    
    try {
      // Register the user
      await authAPI.register({
        username: formData.username,
        email: formData.email,
        password: formData.password
      });
      
      // After successful registration, log them in
      await authAPI.login({
        username: formData.username,
        password: formData.password
      });
      
      // Get user data
      const userResponse = await authAPI.fetchCurrentUser();
      const userData = userResponse.data;
      
      if (onLogin) {
        onLogin(userData);
      }
      
      navigate('/');
    } catch (err) {
      console.error('Registration error:', err);
      
      if (err.response && err.response.data) {
        // Django REST Framework returns field-specific errors in this format
        if (typeof err.response.data === 'object' && !Array.isArray(err.response.data)) {
          const newFieldErrors = {};
          
          // Process field-specific errors
          Object.keys(err.response.data).forEach(field => {
            if (Array.isArray(err.response.data[field])) {
              newFieldErrors[field] = err.response.data[field][0];
            } else {
              newFieldErrors[field] = err.response.data[field];
            }
          });
          
          setFieldErrors(newFieldErrors);
          
          // If there's a non-field error, show it as the main error
          if (err.response.data.non_field_errors) {
            setError(err.response.data.non_field_errors[0]);
          } else if (!Object.keys(newFieldErrors).length) {
            setError('Registration failed. Please try again.');
          }
        } else {
          setError('Registration failed. Please try again with different information.');
        }
      } else {
        setError('Registration failed. Please try again later.');
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
              <h3 className="mb-0">Create an Account</h3>
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
                  <label htmlFor="email" className="form-label">Email</label>
                  <input
                    type="email"
                    className="form-control"
                    id="email"
                    name="email"
                    value={formData.email}
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
                    minLength="8"
                  />
                  <small className="form-text text-muted">
                    Password must be at least 8 characters long.
                  </small>
                </div>
                
                <div className="mb-3">
                  <label htmlFor="confirmPassword" className="form-label">Confirm Password</label>
                  <input
                    type="password"
                    className="form-control"
                    id="confirmPassword"
                    name="confirmPassword"
                    value={formData.confirmPassword}
                    onChange={handleChange}
                    required
                  />
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
                        Registering...
                      </>
                    ) : 'Register'}
                  </button>
                </div>
              </form>
              
              <div className="mt-3 text-center">
                <p>
                  Already have an account? <Link to="/login">Login</Link>
                </p>
                <div className="mt-3">
                  <button className="btn btn-outline-danger">
                    <i className="bi bi-google me-2"></i>Register with Google
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

export default Register;