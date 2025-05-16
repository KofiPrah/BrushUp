/**
 * Utility functions for handling image URLs
 */

/**
 * Default placeholder image to use when an image is missing or fails to load
 */
export const DEFAULT_PLACEHOLDER = 'https://via.placeholder.com/800x600?text=Image+Unavailable';

/**
 * Get a valid image URL, with fallback to a placeholder if the URL is invalid
 * 
 * @param {string} imageUrl - The image URL to validate
 * @returns {string} A valid image URL or a placeholder
 */
export const getValidImageUrl = (imageUrl) => {
  // If no URL is provided, return placeholder
  if (!imageUrl) {
    return DEFAULT_PLACEHOLDER;
  }
  
  // If URL is relative (no protocol/domain), prepend the API base URL
  if (imageUrl.startsWith('/')) {
    // In development, this would be http://localhost:8000
    // In production, use the site domain
    const baseUrl = process.env.REACT_APP_API_BASE_URL || 'https://brushup.replit.app';
    return `${baseUrl}${imageUrl}`;
  }
  
  // If URL already has protocol, return as is
  return imageUrl;
};

/**
 * Handle image load errors by replacing with a placeholder
 * 
 * @param {Event} event - The error event from the img element
 */
export const handleImageError = (event) => {
  event.target.src = DEFAULT_PLACEHOLDER;
  event.target.onerror = null; // Prevents infinite loops
};