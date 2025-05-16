import axios from 'axios';

// Create an axios instance with defaults configured for our API
const API = axios.create({
  baseURL: '/api',
  withCredentials: true, // Important for sending cookies with requests
  headers: {
    'Content-Type': 'application/json',
  }
});

// Request interceptor to handle common request configurations
API.interceptors.request.use(
  (config) => {
    // Get CSRF token from cookie if available
    const csrfToken = getCookie('csrftoken');
    if (csrfToken) {
      config.headers['X-CSRFToken'] = csrfToken;
    }
    return config;
  },
  (error) => {
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