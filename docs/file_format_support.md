# Comprehensive File Format Support for BrushUp

## Overview

BrushUp now supports a wide range of image formats to accommodate diverse digital artwork types, from traditional photography to modern vector graphics and animated content.

## Supported File Formats

### Standard Image Formats
- **JPEG/JPG** - Ideal for photographs and complex artwork with many colors
- **PNG** - Perfect for artwork with transparency or sharp edges
- **BMP** - Uncompressed bitmap format for high-quality images
- **TIFF** - Professional format supporting high bit depths and lossless compression

### Modern Web Formats
- **WebP** - Google's modern format offering superior compression
- **GIF** - Classic format supporting animation (up to 100 frames)

### Vector Graphics
- **SVG** - Scalable vector graphics for crisp artwork at any size

## File Specifications

### Size Limits
- **Maximum file size**: 20MB per upload
- **Maximum dimensions**: 5000x5000 pixels for raster images
- **Maximum animation frames**: 100 frames for GIF and WebP

### Security Features
- Comprehensive file validation using PIL (Python Imaging Library)
- SVG security filtering to prevent malicious content
- MIME type verification to ensure file integrity
- File header validation to detect spoofed files

## Special Format Features

### Animated Content
- **Animated GIFs**: Full support for traditional animated artwork
- **Animated WebP**: Modern animated format with better compression
- Frame count validation ensures reasonable file sizes

### Vector Graphics (SVG)
- Security-focused validation removes potentially dangerous elements
- Supports inline styles and paths for complex artwork
- Blocks external references and script elements for safety

### High-Quality Formats
- **TIFF**: Supports multiple compression types and color depths
- **BMP**: Uncompressed format for maximum quality preservation
- **PNG**: Lossless compression with full transparency support

## Implementation Details

### File Validation Pipeline
1. **Size Check**: Validates file size against 20MB limit
2. **MIME Type Detection**: Verifies file type from headers
3. **Extension Validation**: Ensures extension matches content
4. **Format-Specific Validation**: Applies specialized checks per format
5. **Dimension Validation**: Confirms image dimensions are within limits
6. **Security Screening**: Removes potentially harmful content (SVG)

### Storage Integration
- Seamless integration with AWS S3 for cloud storage
- Automatic format preservation during upload process
- Optimized URLs for fast content delivery

## Usage Guidelines

### For Artists
- Choose **JPEG** for photographs and realistic artwork
- Use **PNG** for artwork with transparency or text
- Select **GIF** for simple animations or pixel art
- Choose **WebP** for modern animated content with better compression
- Use **SVG** for logos, icons, and scalable vector artwork
- Select **TIFF** or **BMP** for archival-quality uploads

### For Digital Art
- **Vector illustrations**: SVG format recommended
- **Digital paintings**: PNG or TIFF for high quality
- **Animated artwork**: GIF for compatibility, WebP for efficiency
- **Photography-based art**: JPEG with high quality settings

## Technical Implementation

### Model Updates
```python
# Both ArtWork and ArtWorkVersion models now include:
validators=[validate_image_file]
help_text="Supported formats: JPEG, PNG, GIF, WebP, SVG, BMP, TIFF (max 20MB)"
```

### Frontend Integration
- File input accepts specific MIME types
- Clear format guidance shown to users
- Real-time validation feedback
- Preview functionality for supported formats

## Error Handling

### Common Validation Errors
- **File too large**: Exceeds 20MB limit
- **Unsupported format**: Not in approved format list
- **Corrupted file**: Cannot be processed by imaging library
- **Security violation**: SVG contains dangerous elements
- **Animation too complex**: Exceeds frame limit

### User Feedback
- Clear error messages explaining specific issues
- Guidance on how to resolve common problems
- Format recommendations based on artwork type

## Future Enhancements

### Planned Additions
- **AVIF** support for next-generation compression
- **HEIC** support for Apple ecosystem compatibility
- Advanced **WebP** optimization settings
- Batch upload with format conversion options

This comprehensive file format support ensures BrushUp can handle virtually any type of digital artwork while maintaining security and performance standards.