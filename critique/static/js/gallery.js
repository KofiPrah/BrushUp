/**
 * Advanced Gallery Component with Search, Filtering, and Infinite Scroll
 * 
 * This component demonstrates the frontend implementation requested in Phase 11,
 * providing a React-like experience using vanilla JavaScript that integrates
 * with the Django backend API.
 */

class ArtworkGallery {
    constructor(containerId, options = {}) {
        this.container = document.getElementById(containerId);
        this.options = {
            apiBaseUrl: '/api/artworks/',
            infiniteScrollUrl: '/api/artworks/infinite-scroll/',
            pageSize: 12,
            searchDebounceMs: 500,
            loadMoreButton: true,
            autoInfiniteScroll: false,
            ...options
        };
        
        // State management
        this.state = {
            artworks: [],
            loading: false,
            hasNextPage: false,
            currentPage: 1,
            totalCount: 0,
            searchQuery: '',
            filters: {
                artist: '',
                medium: '',
                ordering: '-created_at',
                visibility: '',
                created_after: '',
                created_before: ''
            }
        };
        
        // Debounce timer for search
        this.searchTimeout = null;
        
        this.init();
    }
    
    init() {
        this.createGalleryHTML();
        this.bindEventListeners();
        this.loadArtworks(true); // Initial load
    }
    
    createGalleryHTML() {
        this.container.innerHTML = `
            <div class="gallery-container">
                <!-- Search and Filter Controls -->
                <div class="card bg-dark border-secondary mb-4">
                    <div class="card-body">
                        <!-- Main Search Bar -->
                        <div class="row mb-3">
                            <div class="col-md-8">
                                <div class="input-group">
                                    <span class="input-group-text bg-secondary border-secondary">
                                        <i class="bi bi-search text-white"></i>
                                    </span>
                                    <input 
                                        type="text" 
                                        id="gallerySearch"
                                        class="form-control bg-dark border-secondary text-white" 
                                        placeholder="Search artworks by title, description, or artist..."
                                    >
                                </div>
                            </div>
                            <div class="col-md-4">
                                <select id="galleryOrdering" class="form-select bg-dark border-secondary text-white">
                                    <option value="-created_at">📅 Newest First</option>
                                    <option value="created_at">📅 Oldest First</option>
                                    <option value="-popularity_score">🔥 Most Popular</option>
                                    <option value="-likes_count">❤️ Most Liked</option>
                                    <option value="-critiques_count">💬 Most Critiques</option>
                                    <option value="title">🔤 Title A-Z</option>
                                    <option value="-title">🔤 Title Z-A</option>
                                </select>
                            </div>
                        </div>
                        
                        <!-- Advanced Filters (Collapsible) -->
                        <div class="row mb-3">
                            <div class="col-12">
                                <button 
                                    type="button" 
                                    class="btn btn-outline-info btn-sm" 
                                    id="toggleFiltersBtn"
                                    data-bs-toggle="collapse" 
                                    data-bs-target="#advancedFilters"
                                >
                                    <i class="bi bi-funnel"></i> Advanced Filters
                                </button>
                                <button 
                                    type="button" 
                                    class="btn btn-outline-secondary btn-sm ms-2" 
                                    id="clearFiltersBtn"
                                >
                                    <i class="bi bi-arrow-clockwise"></i> Clear All
                                </button>
                            </div>
                        </div>
                        
                        <div class="collapse" id="advancedFilters">
                            <div class="row">
                                <div class="col-md-3 mb-2">
                                    <label class="form-label text-white-50">Artist</label>
                                    <input 
                                        type="text" 
                                        id="artistFilter"
                                        class="form-control bg-dark border-secondary text-white" 
                                        placeholder="Artist username"
                                    >
                                </div>
                                <div class="col-md-3 mb-2">
                                    <label class="form-label text-white-50">Medium</label>
                                    <input 
                                        type="text" 
                                        id="mediumFilter"
                                        class="form-control bg-dark border-secondary text-white" 
                                        placeholder="e.g., Oil, Digital"
                                    >
                                </div>
                                <div class="col-md-3 mb-2">
                                    <label class="form-label text-white-50">Created After</label>
                                    <input 
                                        type="date" 
                                        id="createdAfterFilter"
                                        class="form-control bg-dark border-secondary text-white"
                                    >
                                </div>
                                <div class="col-md-3 mb-2">
                                    <label class="form-label text-white-50">Created Before</label>
                                    <input 
                                        type="date" 
                                        id="createdBeforeFilter"
                                        class="form-control bg-dark border-secondary text-white"
                                    >
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Results Info -->
                <div id="resultsInfo" class="mb-3"></div>
                
                <!-- Loading Indicator -->
                <div id="loadingIndicator" class="text-center mb-4" style="display: none;">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                    <p class="mt-2">Loading artworks...</p>
                </div>
                
                <!-- Gallery Grid -->
                <div id="artworkGrid" class="row row-cols-1 row-cols-md-3 g-4"></div>
                
                <!-- Load More Button -->
                <div class="text-center mt-4">
                    <button 
                        id="loadMoreBtn" 
                        class="btn btn-primary btn-lg" 
                        style="display: none;"
                    >
                        Load More Artworks
                    </button>
                </div>
                
                <!-- No Results Message -->
                <div id="noResults" class="alert alert-info text-center" style="display: none;">
                    <i class="bi bi-search"></i>
                    <h5>No artworks found</h5>
                    <p>Try adjusting your search criteria or clearing filters.</p>
                </div>
            </div>
        `;
    }
    
    bindEventListeners() {
        // Search input with debouncing
        const searchInput = document.getElementById('gallerySearch');
        searchInput.addEventListener('input', (e) => {
            clearTimeout(this.searchTimeout);
            this.searchTimeout = setTimeout(() => {
                this.updateSearch(e.target.value);
            }, this.options.searchDebounceMs);
        });
        
        // Ordering dropdown
        document.getElementById('galleryOrdering').addEventListener('change', (e) => {
            this.updateFilter('ordering', e.target.value);
        });
        
        // Advanced filters
        ['artistFilter', 'mediumFilter', 'createdAfterFilter', 'createdBeforeFilter'].forEach(id => {
            document.getElementById(id).addEventListener('change', (e) => {
                const filterKey = id.replace('Filter', '').replace('createdAfter', 'created_after').replace('createdBefore', 'created_before');
                this.updateFilter(filterKey, e.target.value);
            });
        });
        
        // Clear filters button
        document.getElementById('clearFiltersBtn').addEventListener('click', () => {
            this.clearAllFilters();
        });
        
        // Load more button
        document.getElementById('loadMoreBtn').addEventListener('click', () => {
            this.loadMoreArtworks();
        });
        
        // Auto infinite scroll (if enabled)
        if (this.options.autoInfiniteScroll) {
            window.addEventListener('scroll', this.throttle(() => {
                if (window.innerHeight + window.scrollY >= document.body.offsetHeight - 1000) {
                    if (this.state.hasNextPage && !this.state.loading) {
                        this.loadMoreArtworks();
                    }
                }
            }, 250));
        }
    }
    
    updateSearch(query) {
        this.state.searchQuery = query;
        this.state.currentPage = 1;
        this.loadArtworks(true);
    }
    
    updateFilter(key, value) {
        this.state.filters[key] = value;
        this.state.currentPage = 1;
        this.loadArtworks(true);
    }
    
    clearAllFilters() {
        // Reset search
        document.getElementById('gallerySearch').value = '';
        this.state.searchQuery = '';
        
        // Reset filters
        this.state.filters = {
            artist: '',
            medium: '',
            ordering: '-created_at',
            visibility: '',
            created_after: '',
            created_before: ''
        };
        
        // Update UI
        document.getElementById('galleryOrdering').value = '-created_at';
        document.getElementById('artistFilter').value = '';
        document.getElementById('mediumFilter').value = '';
        document.getElementById('createdAfterFilter').value = '';
        document.getElementById('createdBeforeFilter').value = '';
        
        // Reload
        this.state.currentPage = 1;
        this.loadArtworks(true);
    }
    
    async loadArtworks(reset = false) {
        if (this.state.loading) return;
        
        this.state.loading = true;
        this.showLoading(true);
        
        try {
            const params = new URLSearchParams({
                page: reset ? 1 : this.state.currentPage,
                page_size: this.options.pageSize,
                search: this.state.searchQuery,
                ...this.state.filters
            });
            
            // Remove empty parameters
            for (const [key, value] of [...params]) {
                if (!value) params.delete(key);
            }
            
            const url = `${this.options.apiBaseUrl}?${params}`;
            const response = await fetch(url);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (reset) {
                this.state.artworks = data.results;
            } else {
                this.state.artworks = [...this.state.artworks, ...data.results];
            }
            
            this.state.hasNextPage = data.has_next || false;
            this.state.totalCount = data.count || 0;
            this.state.currentPage = reset ? 2 : this.state.currentPage + 1;
            
            this.renderArtworks(reset);
            this.updateResultsInfo();
            
        } catch (error) {
            console.error('Error loading artworks:', error);
            this.showError('Failed to load artworks. Please try again.');
        } finally {
            this.state.loading = false;
            this.showLoading(false);
        }
    }
    
    async loadMoreArtworks() {
        await this.loadArtworks(false);
    }
    
    renderArtworks(reset = false) {
        const grid = document.getElementById('artworkGrid');
        
        if (reset) {
            grid.innerHTML = '';
        }
        
        if (this.state.artworks.length === 0) {
            document.getElementById('noResults').style.display = 'block';
            document.getElementById('loadMoreBtn').style.display = 'none';
            return;
        }
        
        document.getElementById('noResults').style.display = 'none';
        
        // Render new artworks
        const newArtworks = reset ? this.state.artworks : this.state.artworks.slice(-(this.options.pageSize));
        
        newArtworks.forEach(artwork => {
            const artworkCard = this.createArtworkCard(artwork);
            grid.appendChild(artworkCard);
        });
        
        // Update load more button
        const loadMoreBtn = document.getElementById('loadMoreBtn');
        if (this.options.loadMoreButton) {
            loadMoreBtn.style.display = this.state.hasNextPage ? 'block' : 'none';
        }
    }
    
    createArtworkCard(artwork) {
        const col = document.createElement('div');
        col.className = 'col';
        
        const imageUrl = artwork.image || artwork.image_url || '';
        const imageHtml = imageUrl ? 
            `<img src="${imageUrl}" class="card-img-top" alt="${artwork.title}" style="height: 220px; object-fit: cover;">` :
            `<div class="bg-secondary text-white d-flex justify-content-center align-items-center" style="height: 220px;">
                <span>No Image</span>
            </div>`;
        
        col.innerHTML = `
            <div class="card h-100 bg-dark text-white artwork-card" data-artwork-id="${artwork.id}">
                <a href="/artworks/${artwork.id}/" class="text-decoration-none">
                    ${imageHtml}
                </a>
                <div class="card-body">
                    <h5 class="card-title">${artwork.title}</h5>
                    <p class="card-text">${this.truncateText(artwork.description, 60)}</p>
                    <small class="text-muted">by ${artwork.author?.username || 'Unknown'}</small>
                </div>
                <div class="card-footer">
                    <div class="d-flex justify-content-between align-items-center">
                        <small class="text-muted">
                            <i class="bi bi-calendar"></i> ${new Date(artwork.created_at).toLocaleDateString()}
                        </small>
                        <div class="d-flex gap-2">
                            <small class="text-info">
                                <i class="bi bi-heart"></i> ${artwork.likes_count || 0}
                            </small>
                            <small class="text-success">
                                <i class="bi bi-chat"></i> ${artwork.critiques_count || 0}
                            </small>
                        </div>
                    </div>
                    <div class="mt-2">
                        <a href="/artworks/${artwork.id}/" class="btn btn-primary btn-sm w-100">
                            View Details
                        </a>
                    </div>
                </div>
            </div>
        `;
        
        return col;
    }
    
    updateResultsInfo() {
        const info = document.getElementById('resultsInfo');
        
        if (this.state.totalCount === 0) {
            info.innerHTML = '';
            return;
        }
        
        let infoText = `Showing ${this.state.artworks.length} of ${this.state.totalCount} artworks`;
        
        if (this.state.searchQuery) {
            infoText += ` for "${this.state.searchQuery}"`;
        }
        
        info.innerHTML = `
            <div class="alert alert-info">
                <i class="bi bi-info-circle"></i> ${infoText}
            </div>
        `;
    }
    
    showLoading(show) {
        document.getElementById('loadingIndicator').style.display = show ? 'block' : 'none';
    }
    
    showError(message) {
        const info = document.getElementById('resultsInfo');
        info.innerHTML = `
            <div class="alert alert-danger">
                <i class="bi bi-exclamation-triangle"></i> ${message}
            </div>
        `;
    }
    
    // Utility methods
    truncateText(text, maxLength) {
        if (!text) return '';
        if (text.length <= maxLength) return text;
        return text.substr(0, maxLength) + '...';
    }
    
    throttle(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        }
    }
}

// Initialize gallery when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Check if we have a gallery container on the page
    const galleryContainer = document.getElementById('artworkGalleryApp');
    if (galleryContainer) {
        // Initialize the gallery with custom options if needed
        const gallery = new ArtworkGallery('artworkGalleryApp', {
            pageSize: 12,
            loadMoreButton: true,
            autoInfiniteScroll: false // Can be enabled for true infinite scroll
        });
        
        // Make gallery accessible globally for debugging
        window.artworkGallery = gallery;
    }
});

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ArtworkGallery;
}