import axios from 'axios';

// Determine the base URL based on environment
const getBaseURL = () => {
  // In development environment
  if (import.meta.env.DEV) {
    // When running on Replit, use the Replit domain
    if (window.location.hostname.includes('replit')) {
      const replitDomain = window.location.hostname;
      return `https://${replitDomain}/api`;
    }
    // Local development - use the proxy configured in vite.config.js
    return '/api';
  }
  
  // In production, use the absolute URL to the backend API
  // First try environment variable, then current domain, finally fallback
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL;
  }
  
  // Use current domain (production environment)
  const domain = window.location.hostname;
  return `https://${domain}/api`;
};

// Create an axios instance with defaults configured for our API
const API = axios.create({
  baseURL: getBaseURL(),
  withCredentials: true, // Important for sending cookies with requests
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 second timeout
});

// Request interceptor to handle common request configurations
API.interceptors.request.use(
  (config) => {
    // Get CSRF token from cookie if available
    const csrfToken = getCookie('csrftoken');
    if (csrfToken) {
      config.headers['X-CSRFToken'] = csrfToken;
    }
    
    // For JWT token-based auth (if implemented)
    const authToken = localStorage.getItem('auth_token');
    if (authToken && !config.headers.Authorization) {
      config.headers.Authorization = `Bearer ${authToken}`;
    }
    
    return config;
  },
  (error) => {
    console.error('Request interceptor error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for global error handling
API.interceptors.response.use(
  (response) => {
    // Success case - just return the response
    return response;
  },
  (error) => {
    const originalRequest = error.config;
    
    // Handle authentication errors (redirect to login)
    if (error.response && error.response.status === 401 && !originalRequest._retry) {
      // Clear any stored authentication data
      localStorage.removeItem('auth_token');
      localStorage.removeItem('user');
      
      // Redirect to login page (if using client-side router)
      if (window.location.pathname !== '/login') {
        // Store the current location to redirect back after login
        sessionStorage.setItem('redirect_after_login', window.location.pathname);
        window.location.href = '/login';
      }
    }
    
    // Handle CSRF token errors by refreshing the token and retrying
    if (error.response && error.response.status === 403 && 
        error.response.data && 
        error.response.data.detail && 
        error.response.data.detail.includes('CSRF') && 
        !originalRequest._retry) {
      
      originalRequest._retry = true;
      
      // Get a fresh CSRF token and retry the request
      return API.get('/auth/csrf/')
        .then(() => {
          // Update the CSRF token in the original request
          originalRequest.headers['X-CSRFToken'] = getCookie('csrftoken');
          return API(originalRequest);
        });
    }
    
    // Handle rate limiting
    if (error.response && error.response.status === 429) {
      console.warn('Rate limit exceeded. Please try again later.');
    }
    
    // Log errors that might need debugging
    if (error.response) {
      console.error('API Error Response:', {
        status: error.response.status,
        data: error.response.data,
        headers: error.response.headers,
        url: originalRequest.url
      });
    } else if (error.request) {
      console.error('API Error Request:', error.request);
    } else {
      console.error('API Error:', error.message);
    }
    
    return Promise.reject(error);
  }
);

// Helper function to get cookies
function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
}

// Auth API endpoints
export const authAPI = {
  login: (credentials) => API.post('/auth/login/', credentials),
  logout: () => API.post('/auth/logout/'),
  register: (userData) => API.post('/auth/register/', userData),
  fetchCurrentUser: () => API.get('/auth/user/'),
  checkSession: () => API.get('/auth/session-check/'),
  getCSRFToken: () => API.get('/auth/csrf/')
};

// Artwork API endpoints
export const artworkAPI = {
  getArtworks: (params) => API.get('/artworks/', { params }),
  getArtwork: (id) => API.get(`/artworks/${id}/`),
  uploadArtwork: (formData) => 
    API.post('/artworks/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    }),
  updateArtwork: (id, data) => API.put(`/artworks/${id}/`, data),
  deleteArtwork: (id) => API.delete(`/artworks/${id}/`),
  likeArtwork: (id) => API.post(`/artworks/${id}/like/`),
  getUserArtworks: () => API.get('/artworks/my-artworks/')
};

// Critique API endpoints
export const critiqueAPI = {
  getArtworkCritiques: (artworkId) => API.get(`/artworks/${artworkId}/critiques/`),
  createCritique: (artworkId, data) => API.post(`/artworks/${artworkId}/critiques/`, data),
  updateCritique: (id, data) => API.put(`/critiques/${id}/`, data),
  deleteCritique: (id) => API.delete(`/critiques/${id}/`),
  toggleReaction: (id, reactionType) => API.post(`/critiques/${id}/reactions/`, { reaction_type: reactionType })
};

// Profile API endpoints
export const profileAPI = {
  getUserProfile: () => API.get('/profile/'),
  updateProfile: (data) => API.patch('/profile/', data),
  uploadProfilePicture: (formData) => 
    API.post('/profile/picture/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
};

// Notification API endpoints
export const notificationAPI = {
  getNotifications: () => API.get('/notifications/'),
  getUnreadCount: () => API.get('/notifications/unread-count/'),
  markAsRead: (id) => API.post(`/notifications/${id}/mark-read/`),
  markAllAsRead: () => API.post('/notifications/mark-all-read/'),
  markMultipleAsRead: (ids) => API.post('/notifications/mark-multiple-read/', { notification_ids: ids })
};

export default API;