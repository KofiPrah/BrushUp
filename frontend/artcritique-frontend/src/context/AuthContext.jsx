import React, { createContext, useState, useContext, useEffect } from 'react';
import { authAPI } from '../services/api';
import { handleApiError } from '../services/errorHandler';

// Create the authentication context
const AuthContext = createContext();

// Custom hook for using the auth context
export const useAuth = () => {
  return useContext(AuthContext);
};

// Provider component that wraps the app and provides authentication state
export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Check if user is already logged in when the application loads
  useEffect(() => {
    const checkAuth = async () => {
      try {
        // First, ensure we have a CSRF token
        await authAPI.getCSRFToken();
        
        // Check if user is logged in
        const response = await authAPI.fetchCurrentUser();
        setUser(response.data);
        setError(null);
        
        // Check if this was a redirect from OAuth process
        const redirectPath = sessionStorage.getItem('redirect_after_login');
        if (redirectPath) {
          // Clear the stored path
          sessionStorage.removeItem('redirect_after_login');
          // Redirect to the stored path if needed
          // This will be handled by components using the auth context
        }
      } catch (err) {
        // Only set error if it's not a 401 (unauthorized), since that's expected when not logged in
        if (err.response && err.response.status !== 401) {
          handleApiError(err, setError);
        }
        // Clear user data
        setUser(null);
      } finally {
        setLoading(false);
      }
    };

    checkAuth();
  }, []);

  // Login handler
  const login = async (credentials) => {
    setLoading(true);
    setError(null);
    
    try {
      // Login the user
      await authAPI.login(credentials);
      
      // Get user data
      const response = await authAPI.fetchCurrentUser();
      
      // Update state
      setUser(response.data);
      
      return {
        success: true,
        data: response.data
      };
    } catch (err) {
      const errorInfo = handleApiError(err, setError);
      return {
        success: false,
        error: errorInfo
      };
    } finally {
      setLoading(false);
    }
  };

  // Register handler
  const register = async (userData) => {
    setLoading(true);
    setError(null);
    
    try {
      // Register the user
      await authAPI.register(userData);
      
      // After registration, log them in
      return await login({
        username: userData.username,
        password: userData.password
      });
    } catch (err) {
      const errorInfo = handleApiError(err, setError);
      return {
        success: false,
        error: errorInfo
      };
    } finally {
      setLoading(false);
    }
  };

  // Logout handler
  const logout = async () => {
    setLoading(true);
    
    try {
      await authAPI.logout();
      setUser(null);
      return { success: true };
    } catch (err) {
      handleApiError(err, setError);
      return {
        success: false,
        error: err
      };
    } finally {
      setLoading(false);
    }
  };

  // Update user information after profile changes
  const updateUserInfo = async () => {
    try {
      const response = await authAPI.fetchCurrentUser();
      setUser(response.data);
      return {
        success: true,
        data: response.data
      };
    } catch (err) {
      handleApiError(err, setError);
      return {
        success: false,
        error: err
      };
    }
  };

  // Role checking helper functions
  const isAdmin = () => {
    return user && user.profile && user.profile.role === 'ADMIN';
  };

  const isModerator = () => {
    return user && user.profile && (user.profile.role === 'MODERATOR' || user.profile.role === 'ADMIN');
  };

  const isModeratorOrAdmin = () => {
    return user && user.profile && (user.profile.role === 'MODERATOR' || user.profile.role === 'ADMIN');
  };

  const hasRole = (role) => {
    return user && user.profile && user.profile.role === role;
  };

  // Provide the auth context value to consuming components
  const value = {
    user,
    loading,
    error,
    login,
    register,
    logout,
    updateUserInfo,
    isAuthenticated: !!user,
    isAdmin,
    isModerator,
    isModeratorOrAdmin,
    hasRole
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthContext;