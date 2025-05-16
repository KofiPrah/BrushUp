/**
 * Common error handler for API requests
 * This utility module helps standardize error handling across the application
 */

/**
 * Extracts meaningful error messages from API error responses
 * @param {Error} error - The error from an Axios request
 * @returns {Object} Object containing error message and details
 */
export const extractErrorMessage = (error) => {
  // Default error information
  const errorInfo = {
    message: 'An unexpected error occurred. Please try again later.',
    statusCode: null,
    details: null,
    fieldErrors: {}
  };

  if (!error) {
    return errorInfo;
  }

  // Add the error name if available
  if (error.name) {
    errorInfo.name = error.name;
  }

  // Handle network errors (no response from server)
  if (error.message === 'Network Error') {
    errorInfo.message = 'Unable to connect to the server. Please check your internet connection.';
    return errorInfo;
  }

  // Handle timeout errors
  if (error.code === 'ECONNABORTED') {
    errorInfo.message = 'The request took too long to complete. Please try again.';
    return errorInfo;
  }

  // If we have a response from the server
  if (error.response) {
    const { status, data } = error.response;
    errorInfo.statusCode = status;

    // Handle different status codes
    switch (status) {
      case 400: // Bad Request
        errorInfo.message = 'The request was invalid. Please check your input and try again.';
        break;
      case 401: // Unauthorized
        errorInfo.message = 'Authentication required. Please log in.';
        break;
      case 403: // Forbidden
        errorInfo.message = 'You do not have permission to access this resource.';
        break;
      case 404: // Not Found
        errorInfo.message = 'The requested resource could not be found.';
        break;
      case 429: // Too Many Requests
        errorInfo.message = 'Too many requests. Please try again later.';
        break;
      case 500: // Internal Server Error
        errorInfo.message = 'Server error. Please try again later.';
        break;
      default:
        errorInfo.message = `Error: ${status}`;
    }

    // Extract more detailed error information from the response data
    if (data) {
      // Handle Django Rest Framework error format
      if (data.detail) {
        errorInfo.message = data.detail;
      } 
      
      // Handle non-field errors
      if (data.non_field_errors && Array.isArray(data.non_field_errors)) {
        errorInfo.message = data.non_field_errors[0];
      }
      
      // Handle form validation errors (field-specific)
      const fieldErrors = {};
      if (typeof data === 'object' && !Array.isArray(data)) {
        Object.keys(data).forEach(key => {
          // Skip non-field errors, they're handled separately
          if (key === 'non_field_errors' || key === 'detail') return;
          
          // Extract field errors
          if (Array.isArray(data[key])) {
            fieldErrors[key] = data[key][0]; // Take the first error
          } else if (typeof data[key] === 'string') {
            fieldErrors[key] = data[key];
          }
        });
        
        if (Object.keys(fieldErrors).length > 0) {
          errorInfo.fieldErrors = fieldErrors;
        }
      }
      
      // Save the raw error details for debugging if needed
      errorInfo.details = data;
    }
  }

  return errorInfo;
};

/**
 * Handles API errors and provides a user-friendly message
 * @param {Error} error - The error from an Axios request
 * @param {Function} setError - State setter function for the error message
 * @param {Function} setFieldErrors - Optional state setter function for field-specific errors
 */
export const handleApiError = (error, setError, setFieldErrors = null) => {
  const errorInfo = extractErrorMessage(error);
  
  // Set the main error message
  if (setError) {
    setError(errorInfo.message);
  }
  
  // Set field-specific errors if applicable
  if (setFieldErrors && Object.keys(errorInfo.fieldErrors).length > 0) {
    setFieldErrors(errorInfo.fieldErrors);
  }
  
  // Log errors for debugging
  console.error('API Error:', errorInfo);
  
  return errorInfo;
};

export default {
  extractErrorMessage,
  handleApiError
};