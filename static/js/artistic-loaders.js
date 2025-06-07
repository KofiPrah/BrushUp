/**
 * Artistic Loading Animations Manager for BrushUp
 * Provides creative loading animations for various contexts
 */

class ArtisticLoader {
    constructor() {
        this.activeLoaders = new Set();
        this.overlayElement = null;
        this.createOverlay();
    }

    /**
     * Create the global loading overlay
     */
    createOverlay() {
        this.overlayElement = document.createElement('div');
        this.overlayElement.className = 'artistic-loading-overlay';
        this.overlayElement.innerHTML = `
            <div class="artistic-loading-content">
                <div id="overlayLoader"></div>
                <h3 id="overlayTitle">Creating art...</h3>
                <p id="overlayMessage">Please wait while we process your request</p>
            </div>
        `;
        document.body.appendChild(this.overlayElement);
    }

    /**
     * Get appropriate loader based on context
     */
    getLoaderHTML(type = 'default', size = 'medium') {
        const loaders = {
            upload: this.createPaintbrushLoader(),
            gallery: this.createPaletteLoader(),
            critique: this.createInkSplashLoader(),
            version: this.createEaselLoader(),
            canvas: this.createCanvasLoader(),
            colorwheel: this.createColorWheelLoader(),
            pencil: this.createPencilLoader(),
            watercolor: this.createWatercolorLoader(),
            default: this.createPaintbrushLoader()
        };

        const sizeClass = size === 'small' ? 'scale-75' : size === 'large' ? 'scale-125' : '';
        const loader = loaders[type] || loaders.default;
        
        return `<div class="loader-container ${sizeClass}">${loader}</div>`;
    }

    /**
     * Create paintbrush loader
     */
    createPaintbrushLoader() {
        return `
            <div class="paintbrush-loader"></div>
            <div class="loader-text">Preparing your canvas...</div>
        `;
    }

    /**
     * Create palette mixer loader
     */
    createPaletteLoader() {
        return `
            <div class="palette-loader">
                <div class="palette-color"></div>
                <div class="palette-color"></div>
                <div class="palette-color"></div>
                <div class="palette-color"></div>
            </div>
            <div class="loader-text">Mixing colors...</div>
        `;
    }

    /**
     * Create ink splash loader
     */
    createInkSplashLoader() {
        return `
            <div class="ink-splash-loader">
                <div class="ink-splash"></div>
                <div class="ink-splash"></div>
                <div class="ink-splash"></div>
                <div class="ink-splash"></div>
            </div>
            <div class="loader-text">Splashing creativity...</div>
        `;
    }

    /**
     * Create easel loader
     */
    createEaselLoader() {
        return `
            <div class="easel-loader">
                <div class="easel-stand"></div>
                <div class="easel-canvas">
                    <div class="easel-painting"></div>
                </div>
            </div>
            <div class="loader-text">Setting up easel...</div>
        `;
    }

    /**
     * Create canvas sketching loader
     */
    createCanvasLoader() {
        return `
            <div class="canvas-loader">
                <div class="sketch-line"></div>
                <div class="sketch-line"></div>
                <div class="sketch-line"></div>
                <div class="sketch-line"></div>
            </div>
            <div class="loader-text">Sketching masterpiece...</div>
        `;
    }

    /**
     * Create color wheel loader
     */
    createColorWheelLoader() {
        return `
            <div class="color-wheel-loader"></div>
            <div class="loader-text">Spinning colors...</div>
        `;
    }

    /**
     * Create pencil sharpening loader
     */
    createPencilLoader() {
        return `
            <div class="pencil-loader">
                <div class="pencil-body"></div>
                <div class="pencil-tip"></div>
                <div class="pencil-shavings"></div>
                <div class="pencil-shavings"></div>
                <div class="pencil-shavings"></div>
            </div>
            <div class="loader-text">Sharpening tools...</div>
        `;
    }

    /**
     * Create watercolor wash loader
     */
    createWatercolorLoader() {
        return `
            <div class="watercolor-loader"></div>
            <div class="loader-text">Washing colors...</div>
        `;
    }

    /**
     * Show loader in a specific container
     */
    showLoader(containerId, type = 'default', message = null) {
        const container = document.getElementById(containerId);
        if (!container) return;

        const loaderId = `loader_${containerId}_${Date.now()}`;
        const loaderHTML = this.getLoaderHTML(type);
        
        container.innerHTML = loaderHTML;
        if (message) {
            const textElement = container.querySelector('.loader-text');
            if (textElement) {
                textElement.textContent = message;
            }
        }

        this.activeLoaders.add(loaderId);
        return loaderId;
    }

    /**
     * Show full-screen overlay loader
     */
    showOverlay(type = 'default', title = 'Creating art...', message = 'Please wait while we process your request') {
        const loaderContainer = this.overlayElement.querySelector('#overlayLoader');
        const titleElement = this.overlayElement.querySelector('#overlayTitle');
        const messageElement = this.overlayElement.querySelector('#overlayMessage');

        loaderContainer.innerHTML = this.getLoaderHTML(type, 'large');
        titleElement.textContent = title;
        messageElement.textContent = message;

        this.overlayElement.classList.add('active');
        document.body.style.overflow = 'hidden';
    }

    /**
     * Hide overlay loader
     */
    hideOverlay() {
        this.overlayElement.classList.remove('active');
        document.body.style.overflow = '';
    }

    /**
     * Hide loader from container
     */
    hideLoader(containerId) {
        const container = document.getElementById(containerId);
        if (container) {
            container.innerHTML = '';
        }
    }

    /**
     * Replace existing content with loader
     */
    replaceWithLoader(element, type = 'default', message = null) {
        if (typeof element === 'string') {
            element = document.getElementById(element);
        }
        if (!element) return;

        const originalContent = element.innerHTML;
        element.innerHTML = this.getLoaderHTML(type);
        
        if (message) {
            const textElement = element.querySelector('.loader-text');
            if (textElement) {
                textElement.textContent = message;
            }
        }

        return originalContent;
    }

    /**
     * Context-specific loader methods
     */
    showUploadLoader(containerId, message = 'Uploading your artwork...') {
        return this.showLoader(containerId, 'upload', message);
    }

    showGalleryLoader(containerId, message = 'Loading gallery...') {
        return this.showLoader(containerId, 'gallery', message);
    }

    showCritiqueLoader(containerId, message = 'Loading critiques...') {
        return this.showLoader(containerId, 'critique', message);
    }

    showVersionLoader(containerId, message = 'Managing versions...') {
        return this.showLoader(containerId, 'version', message);
    }

    /**
     * Button loading states
     */
    setButtonLoading(button, type = 'pencil', originalText = null) {
        if (typeof button === 'string') {
            button = document.getElementById(button);
        }
        if (!button) return;

        const original = originalText || button.innerHTML;
        button.disabled = true;
        button.dataset.originalContent = original;
        
        const miniLoader = this.getMiniLoaderHTML(type);
        button.innerHTML = `${miniLoader} Loading...`;
        
        return original;
    }

    /**
     * Restore button from loading state
     */
    restoreButton(button) {
        if (typeof button === 'string') {
            button = document.getElementById(button);
        }
        if (!button) return;

        const originalContent = button.dataset.originalContent;
        if (originalContent) {
            button.innerHTML = originalContent;
            button.disabled = false;
            delete button.dataset.originalContent;
        }
    }

    /**
     * Get mini loader for buttons
     */
    getMiniLoaderHTML(type) {
        const miniLoaders = {
            pencil: '<div class="spinner-border spinner-border-sm me-2" role="status"></div>',
            brush: '<div class="paintbrush-loader" style="transform: scale(0.3); display: inline-block; margin-right: 8px;"></div>',
            palette: '<div class="color-wheel-loader" style="transform: scale(0.2); display: inline-block; margin-right: 8px;"></div>',
            default: '<div class="spinner-border spinner-border-sm me-2" role="status"></div>'
        };
        
        return miniLoaders[type] || miniLoaders.default;
    }

    /**
     * Show progress loader with percentage
     */
    showProgressLoader(containerId, type = 'canvas', initialMessage = 'Processing...') {
        const container = document.getElementById(containerId);
        if (!container) return;

        const progressHTML = `
            <div class="loader-container">
                ${this.getLoaderHTML(type)}
                <div class="progress mt-3" style="width: 200px;">
                    <div class="progress-bar progress-bar-striped progress-bar-animated" 
                         role="progressbar" 
                         style="width: 0%"
                         id="progressBar_${containerId}">
                    </div>
                </div>
                <div class="loader-text" id="progressText_${containerId}">${initialMessage}</div>
            </div>
        `;

        container.innerHTML = progressHTML;
    }

    /**
     * Update progress loader
     */
    updateProgress(containerId, percentage, message = null) {
        const progressBar = document.getElementById(`progressBar_${containerId}`);
        const progressText = document.getElementById(`progressText_${containerId}`);
        
        if (progressBar) {
            progressBar.style.width = `${percentage}%`;
        }
        
        if (progressText && message) {
            progressText.textContent = message;
        }
    }

    /**
     * Cleanup all loaders
     */
    cleanup() {
        this.hideOverlay();
        this.activeLoaders.clear();
    }
}

// Create global instance
const artisticLoader = new ArtisticLoader();

// Utility functions for easy access
function showArtisticLoader(containerId, type = 'default', message = null) {
    return artisticLoader.showLoader(containerId, type, message);
}

function hideArtisticLoader(containerId) {
    artisticLoader.hideLoader(containerId);
}

function showLoadingOverlay(type = 'default', title = 'Creating art...', message = 'Please wait...') {
    artisticLoader.showOverlay(type, title, message);
}

function hideLoadingOverlay() {
    artisticLoader.hideOverlay();
}

function setButtonLoading(button, type = 'pencil', originalText = null) {
    return artisticLoader.setButtonLoading(button, type, originalText);
}

function restoreButton(button) {
    artisticLoader.restoreButton(button);
}

// Context-specific shortcuts
function showUploadLoader(containerId, message) {
    return artisticLoader.showUploadLoader(containerId, message);
}

function showGalleryLoader(containerId, message) {
    return artisticLoader.showGalleryLoader(containerId, message);
}

function showCritiqueLoader(containerId, message) {
    return artisticLoader.showCritiqueLoader(containerId, message);
}

function showVersionLoader(containerId, message) {
    return artisticLoader.showVersionLoader(containerId, message);
}

// Auto-cleanup on page unload
window.addEventListener('beforeunload', () => {
    artisticLoader.cleanup();
});

// Export for module usage if needed
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { artisticLoader, ArtisticLoader };
}