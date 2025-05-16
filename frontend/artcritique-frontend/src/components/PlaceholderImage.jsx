import React from 'react';
import { DEFAULT_PLACEHOLDER } from '../utils/imageUtils';

/**
 * A placeholder component for when images fail to load
 * 
 * @param {Object} props - Component props
 * @param {string} props.alt - Alt text for the image
 * @param {string} props.className - Additional CSS classes
 * @param {Object} props.style - Additional inline styles
 * @param {number|string} props.width - Width of the image
 * @param {number|string} props.height - Height of the image
 * @param {string} props.aspectRatio - Aspect ratio of the image (e.g. '4:3', '16:9')
 */
const PlaceholderImage = ({ 
  alt = 'Image unavailable',
  className = '',
  style = {},
  width = '100%',
  height = 'auto',
  aspectRatio = '4:3',
  ...props 
}) => {
  
  // Default styles with overrides from props
  const containerStyles = {
    backgroundColor: '#2a2a2a',
    borderRadius: '0.375rem',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    flexDirection: 'column',
    color: '#ffffff',
    textAlign: 'center',
    position: 'relative',
    overflow: 'hidden',
    ...style
  };
  
  // Create image styles based on props
  const imgStyles = {
    maxWidth: '100%', 
    width: '100%',
    height: 'auto',
    aspectRatio: aspectRatio,
    display: 'block'
  };
  
  // Text overlay styles
  const textOverlayStyles = {
    position: 'absolute',
    top: '50%',
    left: '50%',
    transform: 'translate(-50%, -50%)',
    zIndex: 2,
    textAlign: 'center',
    width: '100%',
    padding: '1rem'
  };
  
  return (
    <div 
      className={`artwork-placeholder ${className}`}
      style={containerStyles}
      {...props}
    >
      {/* Base image */}
      <img 
        src={DEFAULT_PLACEHOLDER}
        alt={alt}
        style={imgStyles}
        width={width}
        height={height}
      />
      
      {/* Text overlay for better visibility */}
      <div style={textOverlayStyles}>
        <div style={{ fontSize: '1.5rem', fontWeight: 'bold', marginBottom: '0.5rem' }}>
          Image Unavailable
        </div>
        <div style={{ fontSize: '0.875rem', color: '#cccccc' }}>
          Image not found or could not be loaded
        </div>
      </div>
    </div>
  );
};

export default PlaceholderImage;