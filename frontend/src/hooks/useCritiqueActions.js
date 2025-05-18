import { useState } from 'react';
import axios from 'axios';

// Create the hook for critique actions
const useCritiqueActions = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  // Set up axios instance with proper CSRF token handling
  const API = axios.create({
    baseURL: '/api',
    withCredentials: true,
    headers: {
      'Content-Type': 'application/json',
      'X-Requested-With': 'XMLHttpRequest'
    }
  });

  // Ensure CSRF token is included in requests
  API.interceptors.request.use(config => {
    const token = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
    if (token) {
      config.headers['X-CSRFToken'] = token;
    }
    return config;
  });

  // Function to hide a critique
  const hideCritique = async (critiqueId, reason = '') => {
    setLoading(true);
    setError(null);
    setSuccess(null);
    
    try {
      const response = await API.post(`/critiques/${critiqueId}/hide/`, { reason });
      setSuccess('Critique has been hidden successfully.');
      setLoading(false);
      return response.data;
    } catch (err) {
      setError(err.response?.data?.error || 'An error occurred while hiding the critique.');
      setLoading(false);
      throw err;
    }
  };

  // Function to unhide a critique
  const unhideCritique = async (critiqueId) => {
    setLoading(true);
    setError(null);
    setSuccess(null);
    
    try {
      const response = await API.post(`/critiques/${critiqueId}/unhide/`);
      setSuccess('Critique has been unhidden successfully.');
      setLoading(false);
      return response.data;
    } catch (err) {
      setError(err.response?.data?.error || 'An error occurred while unhiding the critique.');
      setLoading(false);
      throw err;
    }
  };

  // Function to flag a critique
  const flagCritique = async (critiqueId, reason) => {
    setLoading(true);
    setError(null);
    setSuccess(null);
    
    try {
      const response = await API.post(`/critiques/${critiqueId}/flag/`, { reason });
      setSuccess('Critique has been flagged successfully.');
      setLoading(false);
      return response.data;
    } catch (err) {
      setError(err.response?.data?.error || 'An error occurred while flagging the critique.');
      setLoading(false);
      throw err;
    }
  };

  // Function to reply to a critique
  const replyCritique = async (critiqueId, text) => {
    setLoading(true);
    setError(null);
    setSuccess(null);
    
    try {
      const response = await API.post(`/critiques/${critiqueId}/reply/`, { text });
      setSuccess('Your reply has been added successfully.');
      setLoading(false);
      return response.data;
    } catch (err) {
      setError(err.response?.data?.error || 'An error occurred while adding your reply.');
      setLoading(false);
      throw err;
    }
  };

  return {
    loading,
    error,
    success,
    hideCritique,
    unhideCritique,
    flagCritique,
    replyCritique
  };
};

export default useCritiqueActions;