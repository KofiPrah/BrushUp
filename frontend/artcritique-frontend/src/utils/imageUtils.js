/**
 * Utility functions for handling image URLs
 */

/**
 * Default placeholder image to use when an image is missing or fails to load
 * This is a data URL of a simple SVG placeholder so it works without network requests
 */
export const DEFAULT_PLACEHOLDER = 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI4MDAiIGhlaWdodD0iNjAwIiB2aWV3Qm94PSIwIDAgODAwIDYwMCI+PHJlY3Qgd2lkdGg9IjgwMCIgaGVpZ2h0PSI2MDAiIGZpbGw9IiMyYTJhMmEiLz48dGV4dCB4PSI0MDAiIHk9IjI4MCIgZm9udC1zaXplPSIzMnB4IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmaWxsPSIjZmZmZmZmIj5JbWFnZSBVbmF2YWlsYWJsZTwvdGV4dD48dGV4dCB4PSI0MDAiIHk9IjMzMCIgZm9udC1zaXplPSIyMHB4IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmaWxsPSIjOTk5OTk5Ij5JbWFnZSBub3QgZm91bmQgb3IgY291bGQgbm90IGJlIGxvYWRlZDwvdGV4dD48cmVjdCB4PSIyMCIgeT0iMjAiIHdpZHRoPSI3NjAiIGhlaWdodD0iNTYwIiBzdHJva2U9IiM0NDQ0NDQiIHN0cm9rZS13aWR0aD0iNCIgZmlsbD0ibm9uZSIvPjxjaXJjbGUgY3g9IjY1MCIgY3k9IjE1MCIgcj0iNjAiIGZpbGw9IiM0NDQ0NDQiLz48L3N2Zz4=';

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
  
  // Add a CSS class for styling
  event.target.classList.add('placeholder-image');
  
  // Set alt text for accessibility
  if (!event.target.alt || event.target.alt === '') {
    event.target.alt = 'Image unavailable';
  }
};