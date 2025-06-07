"""
File validation utilities for artwork uploads
Supports multiple image formats with size and security restrictions
"""
import mimetypes
from django.core.exceptions import ValidationError
from django.conf import settings
from PIL import Image
import io

# Supported file types with their MIME types and extensions
SUPPORTED_IMAGE_TYPES = {
    'image/jpeg': ['.jpg', '.jpeg'],
    'image/png': ['.png'],
    'image/gif': ['.gif'],
    'image/webp': ['.webp'],
    'image/svg+xml': ['.svg'],
    'image/bmp': ['.bmp'],
    'image/tiff': ['.tiff', '.tif'],
}

# File size limits (in bytes)
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB
MAX_DIMENSIONS = (5000, 5000)  # 5000x5000 pixels
MAX_GIF_FRAMES = 100  # Maximum frames for animated GIFs

def validate_image_file(file):
    """
    Comprehensive image file validator
    Checks file type, size, dimensions, and security
    """
    # Check file size
    if file.size > MAX_FILE_SIZE:
        raise ValidationError(f'File size too large. Maximum size is {MAX_FILE_SIZE // (1024*1024)}MB.')
    
    # Get file extension and MIME type
    file_extension = None
    if hasattr(file, 'name') and file.name:
        file_extension = '.' + file.name.split('.')[-1].lower()
    
    # Detect MIME type
    mime_type = None
    if hasattr(file, 'content_type'):
        mime_type = file.content_type
    elif file_extension:
        mime_type, _ = mimetypes.guess_type(file.name)
    
    # Validate MIME type
    if mime_type not in SUPPORTED_IMAGE_TYPES:
        supported_types = ', '.join(SUPPORTED_IMAGE_TYPES.keys())
        raise ValidationError(f'Unsupported file type: {mime_type}. Supported types: {supported_types}')
    
    # Validate file extension
    if file_extension and file_extension not in SUPPORTED_IMAGE_TYPES[mime_type]:
        expected_extensions = ', '.join(SUPPORTED_IMAGE_TYPES[mime_type])
        raise ValidationError(f'File extension {file_extension} does not match MIME type {mime_type}. Expected: {expected_extensions}')
    
    # Special handling for different file types
    try:
        file.seek(0)  # Reset file pointer
        
        if mime_type == 'image/svg+xml':
            validate_svg_file(file)
        elif mime_type == 'image/gif':
            validate_gif_file(file)
        else:
            validate_standard_image(file, mime_type)
            
    except Exception as e:
        if isinstance(e, ValidationError):
            raise
        raise ValidationError(f'Invalid or corrupted image file: {str(e)}')
    finally:
        file.seek(0)  # Reset file pointer for further processing

def validate_svg_file(file):
    """
    Validate SVG files for security and content
    """
    content = file.read()
    if isinstance(content, bytes):
        content = content.decode('utf-8', errors='ignore')
    
    # Basic security checks - look for potentially dangerous content
    dangerous_elements = ['script', 'object', 'embed', 'iframe', 'link', 'style']
    content_lower = content.lower()
    
    for element in dangerous_elements:
        if f'<{element}' in content_lower:
            raise ValidationError(f'SVG files cannot contain <{element}> elements for security reasons.')
    
    # Check for external references
    if 'href=' in content_lower and ('http://' in content_lower or 'https://' in content_lower):
        raise ValidationError('SVG files cannot contain external references for security reasons.')
    
    # Basic SVG structure validation
    if '<svg' not in content_lower:
        raise ValidationError('Invalid SVG file: missing <svg> element.')

def validate_gif_file(file):
    """
    Validate GIF files including animated GIFs
    """
    try:
        with Image.open(file) as img:
            # Check dimensions
            if img.size[0] > MAX_DIMENSIONS[0] or img.size[1] > MAX_DIMENSIONS[1]:
                raise ValidationError(f'Image dimensions too large. Maximum: {MAX_DIMENSIONS[0]}x{MAX_DIMENSIONS[1]} pixels.')
            
            # Check for animation and frame count
            if hasattr(img, 'is_animated') and img.is_animated:
                frame_count = getattr(img, 'n_frames', 1)
                if frame_count > MAX_GIF_FRAMES:
                    raise ValidationError(f'Animated GIF has too many frames. Maximum: {MAX_GIF_FRAMES} frames.')
    except Exception as e:
        if isinstance(e, ValidationError):
            raise
        raise ValidationError('Invalid GIF file.')

def validate_standard_image(file, mime_type):
    """
    Validate standard image formats (JPEG, PNG, WEBP, BMP, TIFF)
    """
    try:
        with Image.open(file) as img:
            # Verify the image can be opened and processed
            img.verify()
            
            # Re-open for dimension check (verify() invalidates the image)
            file.seek(0)
            with Image.open(file) as img2:
                # Check dimensions
                if img2.size[0] > MAX_DIMENSIONS[0] or img2.size[1] > MAX_DIMENSIONS[1]:
                    raise ValidationError(f'Image dimensions too large. Maximum: {MAX_DIMENSIONS[0]}x{MAX_DIMENSIONS[1]} pixels.')
                
                # Additional format-specific checks
                if mime_type == 'image/webp':
                    # WebP can be animated, check frame count
                    if hasattr(img2, 'is_animated') and img2.is_animated:
                        frame_count = getattr(img2, 'n_frames', 1)
                        if frame_count > MAX_GIF_FRAMES:
                            raise ValidationError(f'Animated WebP has too many frames. Maximum: {MAX_GIF_FRAMES} frames.')
                            
    except Exception as e:
        if isinstance(e, ValidationError):
            raise
        raise ValidationError(f'Invalid {mime_type} file.')

def get_file_info(file):
    """
    Extract useful information about uploaded files
    Returns dict with file info for logging/display
    """
    info = {
        'filename': getattr(file, 'name', 'unknown'),
        'size': getattr(file, 'size', 0),
        'content_type': getattr(file, 'content_type', 'unknown'),
    }
    
    # Try to get image dimensions
    try:
        file.seek(0)
        if info['content_type'] != 'image/svg+xml':
            with Image.open(file) as img:
                info['dimensions'] = img.size
                info['format'] = img.format
                info['mode'] = img.mode
                
                # Check for animation
                if hasattr(img, 'is_animated'):
                    info['animated'] = img.is_animated
                    if img.is_animated:
                        info['frames'] = getattr(img, 'n_frames', 1)
        file.seek(0)
    except Exception:
        pass
    
    return info