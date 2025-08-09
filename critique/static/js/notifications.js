/**
 * Real-Time Notifications System
 * 
 * Handles WebSocket connections for live notifications including:
 * - Connection management with automatic reconnection
 * - Real-time notification updates
 * - UI integration with notification badge and toasts
 * - Fallback to polling when WebSocket is unavailable
 */

class NotificationManager {
    constructor(options = {}) {
        this.options = {
            wsUrl: this.getWebSocketUrl(),
            pollInterval: 30000, // 30 seconds fallback polling
            maxReconnectAttempts: 5,
            reconnectInterval: 5000, // 5 seconds
            enablePollingFallback: true,
            enableToastNotifications: true,
            toastDuration: 5000,
            ...options
        };
        
        this.socket = null;
        this.reconnectAttempts = 0;
        this.notifications = [];
        this.unreadCount = 0;
        this.isConnected = false;
        this.pollTimer = null;
        
        // UI elements
        this.notificationBadge = null;
        this.notificationDropdown = null;
        this.notificationList = null;
        
        this.init();
    }
    
    init() {
        this.initializeUI();
        
        if (this.isUserAuthenticated()) {
            this.connectWebSocket();
        }
        
        // Bind event listeners
        document.addEventListener('DOMContentLoaded', () => {
            this.bindUIEvents();
        });
        
        // Handle page visibility changes for connection management
        document.addEventListener('visibilitychange', () => {
            if (document.visibilityState === 'visible' && !this.isConnected) {
                this.connectWebSocket();
            }
        });
    }
    
    getWebSocketUrl() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const host = window.location.host;
        return `${protocol}//${host}/ws/notifications/`;
    }
    
    isUserAuthenticated() {
        // Check if user is authenticated (look for session data or user info in DOM)
        return document.body.dataset.userId || 
               document.querySelector('meta[name="user-authenticated"]') ||
               window.currentUserId;
    }
    
    connectWebSocket() {
        if (this.socket && (this.socket.readyState === WebSocket.CONNECTING || 
                          this.socket.readyState === WebSocket.OPEN)) {
            return;
        }
        
        try {
            this.socket = new WebSocket(this.options.wsUrl);
            
            this.socket.onopen = (event) => {
                console.log('WebSocket connected for notifications');
                this.isConnected = true;
                this.reconnectAttempts = 0;
                this.stopPolling();
                this.updateConnectionStatus(true);
            };
            
            this.socket.onmessage = (event) => {
                this.handleWebSocketMessage(event);
            };
            
            this.socket.onclose = (event) => {
                console.log('WebSocket disconnected:', event.code, event.reason);
                this.isConnected = false;
                this.updateConnectionStatus(false);
                
                // Attempt to reconnect unless it was a clean close
                if (event.code !== 1000 && this.reconnectAttempts < this.options.maxReconnectAttempts) {
                    this.scheduleReconnect();
                } else if (this.options.enablePollingFallback) {
                    this.startPolling();
                }
            };
            
            this.socket.onerror = (error) => {
                console.error('WebSocket error:', error);
                if (this.options.enablePollingFallback) {
                    this.startPolling();
                }
            };
            
        } catch (error) {
            console.error('Failed to create WebSocket connection:', error);
            if (this.options.enablePollingFallback) {
                this.startPolling();
            }
        }
    }
    
    handleWebSocketMessage(event) {
        try {
            const data = JSON.parse(event.data);
            
            switch (data.type) {
                case 'connection_established':
                    console.log('Notification WebSocket established for user:', data.user_id);
                    this.requestInitialNotifications();
                    break;
                    
                case 'new_notification':
                    this.handleNewNotification(data.notification);
                    break;
                    
                case 'unread_count':
                    this.updateUnreadCount(data.count);
                    break;
                    
                case 'notifications_list':
                    this.updateNotificationsList(data.notifications);
                    break;
                    
                case 'notification_marked_read':
                    this.markNotificationAsRead(data.notification_id);
                    break;
                    
                case 'all_notifications_marked_read':
                    this.markAllNotificationsAsRead();
                    break;
                    
                case 'error':
                    console.error('WebSocket error:', data.message);
                    break;
            }
        } catch (error) {
            console.error('Error parsing WebSocket message:', error);
        }
    }
    
    scheduleReconnect() {
        this.reconnectAttempts++;
        const delay = this.options.reconnectInterval * this.reconnectAttempts;
        
        setTimeout(() => {
            console.log(`Attempting to reconnect WebSocket (${this.reconnectAttempts}/${this.options.maxReconnectAttempts})`);
            this.connectWebSocket();
        }, delay);
    }
    
    // Polling fallback for when WebSocket is unavailable
    startPolling() {
        if (this.pollTimer) return;
        
        console.log('Starting notification polling fallback');
        this.pollTimer = setInterval(() => {
            this.fetchNotifications();
        }, this.options.pollInterval);
        
        // Immediate fetch
        this.fetchNotifications();
    }
    
    stopPolling() {
        if (this.pollTimer) {
            clearInterval(this.pollTimer);
            this.pollTimer = null;
            console.log('Stopped notification polling');
        }
    }
    
    async fetchNotifications() {
        try {
            const response = await fetch('/api/notifications/', {
                credentials: 'same-origin'
            });
            
            if (response.ok) {
                const data = await response.json();
                this.updateNotificationsList(data.results);
                this.updateUnreadCount(data.results.filter(n => !n.read).length);
            }
        } catch (error) {
            console.error('Error fetching notifications:', error);
        }
    }
    
    // WebSocket message sending
    sendMessage(message) {
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            this.socket.send(JSON.stringify(message));
            return true;
        }
        return false;
    }
    
    requestInitialNotifications() {
        this.sendMessage({ type: 'get_notifications' });
    }
    
    markNotificationRead(notificationId) {
        this.sendMessage({ 
            type: 'mark_read', 
            notification_id: notificationId 
        });
    }
    
    markAllNotificationsRead() {
        this.sendMessage({ type: 'mark_all_read' });
    }
    
    // UI Management
    initializeUI() {
        // Create notification UI if it doesn't exist
        this.createNotificationUI();
        
        // Get references to UI elements
        this.notificationBadge = document.getElementById('notificationBadge');
        this.notificationDropdown = document.getElementById('notificationDropdown');
        this.notificationList = document.getElementById('notificationList');
    }
    
    createNotificationUI() {
        // Check if notification UI already exists
        if (document.getElementById('notificationBell')) {
            return;
        }
        
        // Find the navbar or create a container
        let navbarNav = document.querySelector('.navbar-nav');
        if (!navbarNav) {
            // Create a simple notification container if no navbar
            navbarNav = document.createElement('div');
            navbarNav.className = 'notification-container position-fixed top-0 end-0 p-3';
            navbarNav.style.zIndex = '9999';
            document.body.appendChild(navbarNav);
        }
        
        // Create notification bell dropdown
        const notificationHTML = `
            <li class="nav-item dropdown" id="notificationBell">
                <a class="nav-link dropdown-toggle position-relative" href="#" id="notificationDropdown" 
                   role="button" data-bs-toggle="dropdown" aria-expanded="false">
                    <i class="bi bi-bell"></i>
                    <span id="notificationBadge" class="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger" 
                          style="display: none;">0</span>
                </a>
                <ul class="dropdown-menu dropdown-menu-end notification-dropdown" aria-labelledby="notificationDropdown" 
                    style="width: 320px; max-height: 400px; overflow-y: auto;">
                    <li class="dropdown-header d-flex justify-content-between align-items-center">
                        Notifications
                        <button class="btn btn-sm btn-link p-0" id="markAllReadBtn" style="display: none;">
                            Mark all read
                        </button>
                    </li>
                    <li><hr class="dropdown-divider"></li>
                    <li id="notificationList">
                        <div class="dropdown-item text-center text-muted">
                            Loading notifications...
                        </div>
                    </li>
                    <li class="dropdown-footer">
                        <hr class="dropdown-divider">
                        <a class="dropdown-item text-center small" href="/notifications/">View All Notifications</a>
                    </li>
                </ul>
            </li>
            
            <!-- Connection status indicator -->
            <li class="nav-item">
                <span id="connectionStatus" class="badge bg-secondary ms-2" style="display: none;">Offline</span>
            </li>
        `;
        
        navbarNav.insertAdjacentHTML('beforeend', notificationHTML);
    }
    
    bindUIEvents() {
        // Mark all notifications as read
        const markAllReadBtn = document.getElementById('markAllReadBtn');
        if (markAllReadBtn) {
            markAllReadBtn.addEventListener('click', () => {
                this.markAllNotificationsRead();
            });
        }
        
        // Handle notification item clicks
        document.addEventListener('click', (event) => {
            if (event.target.closest('.notification-item')) {
                const notificationItem = event.target.closest('.notification-item');
                const notificationId = notificationItem.dataset.notificationId;
                const url = notificationItem.dataset.url;
                
                if (notificationId) {
                    this.markNotificationRead(notificationId);
                }
                
                if (url) {
                    window.location.href = url;
                }
            }
        });
    }
    
    handleNewNotification(notification) {
        this.notifications.unshift(notification);
        this.updateNotificationsList(this.notifications);
        this.updateUnreadCount(this.unreadCount + 1);
        
        // Show toast notification
        if (this.options.enableToastNotifications) {
            this.showToastNotification(notification);
        }
        
        // Play notification sound (optional)
        this.playNotificationSound();
    }
    
    updateNotificationsList(notifications) {
        this.notifications = notifications;
        
        const notificationList = document.getElementById('notificationList');
        if (!notificationList) return;
        
        if (notifications.length === 0) {
            notificationList.innerHTML = `
                <div class="dropdown-item text-center text-muted">
                    No notifications yet
                </div>
            `;
            return;
        }
        
        const notificationHTML = notifications.slice(0, 10).map(notification => `
            <li>
                <a class="dropdown-item notification-item ${!notification.read ? 'bg-light' : ''}" 
                   href="#" 
                   data-notification-id="${notification.id}"
                   data-url="${notification.url}">
                    <div class="d-flex align-items-start">
                        <div class="flex-grow-1">
                            <div class="fw-bold">${notification.title || 'Notification'}</div>
                            <div class="small text-muted">${notification.message}</div>
                            <div class="small text-muted">${this.formatTimeAgo(notification.created_at)}</div>
                        </div>
                        ${!notification.read ? '<div class="badge bg-primary ms-2">New</div>' : ''}
                    </div>
                </a>
            </li>
        `).join('');
        
        notificationList.innerHTML = notificationHTML;
    }
    
    updateUnreadCount(count) {
        this.unreadCount = count;
        
        const badge = document.getElementById('notificationBadge');
        const markAllReadBtn = document.getElementById('markAllReadBtn');
        
        if (badge) {
            if (count > 0) {
                badge.textContent = count > 99 ? '99+' : count.toString();
                badge.style.display = 'inline';
            } else {
                badge.style.display = 'none';
            }
        }
        
        if (markAllReadBtn) {
            markAllReadBtn.style.display = count > 0 ? 'inline' : 'none';
        }
        
        // Update page title with notification count
        this.updatePageTitle(count);
    }
    
    markNotificationAsRead(notificationId) {
        this.notifications = this.notifications.map(notification => 
            notification.id == notificationId 
                ? { ...notification, read: true }
                : notification
        );
        
        this.updateNotificationsList(this.notifications);
        this.updateUnreadCount(Math.max(0, this.unreadCount - 1));
    }
    
    markAllNotificationsAsRead() {
        this.notifications = this.notifications.map(notification => 
            ({ ...notification, read: true })
        );
        
        this.updateNotificationsList(this.notifications);
        this.updateUnreadCount(0);
    }
    
    showToastNotification(notification) {
        // Create toast container if it doesn't exist
        let toastContainer = document.getElementById('toastContainer');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.id = 'toastContainer';
            toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
            toastContainer.style.zIndex = '9999';
            document.body.appendChild(toastContainer);
        }
        
        // Create toast element
        const toastId = `toast-${Date.now()}`;
        const toastHTML = `
            <div id="${toastId}" class="toast align-items-center text-white bg-primary border-0" role="alert" aria-live="assertive" aria-atomic="true">
                <div class="d-flex">
                    <div class="toast-body">
                        <strong>${notification.title || 'New Notification'}</strong><br>
                        ${notification.message}
                    </div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
                </div>
            </div>
        `;
        
        toastContainer.insertAdjacentHTML('beforeend', toastHTML);
        
        // Initialize and show toast
        const toastElement = document.getElementById(toastId);
        const toast = new bootstrap.Toast(toastElement, {
            autohide: true,
            delay: this.options.toastDuration
        });
        
        toast.show();
        
        // Remove toast element after hiding
        toastElement.addEventListener('hidden.bs.toast', () => {
            toastElement.remove();
        });
    }
    
    playNotificationSound() {
        // Optional: Play a subtle notification sound
        try {
            const audio = new Audio('data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+Dxu2slBTCM0fLNeSsFJHfH8N2QQAoUXrTp66hVFApGn+Dxu2slBTCM0fLNeSsFJHfH8N2QQAoUXrTp66hVFApGn+Dxu2slBTCM0fLNeSsFJHfH8N2QQAoUXrTp66hVFApGn+Dxu2slBTCM0fLNeSsFJHfH8N2QQAoUXrTp66hVFApGn+Dxu2slBTCM0fLNeSsFJHfH8N2QQAoUXrTp66hVFApGn+Dxu2slBTCM0fLNeSsFJHfH8N2QQAoUXrTp66hVFApGn+Dxu2slBTCM0fLNeSsFJHfH8N2QQAoUXrTp66hVFApGn+Dxu2slBTCM0fLNeSsFJHfH8N2QQAoUXrTp66hVFApGn+Dxu2slBTCM0fLNeSsFJHfH8N2QQAoUXrTp66hVFApGn+Dxu2slBTCM0fLNeSsFJHfH8N2QQAoUXrTp66hVFApGn+Dxu2slBTCM0fLNeSsFJHfH8N2QQAoUXrTp66hVFApGn+Dxu2slBTCM0fLNeSsFJHfH8N2QQAoUXrTp66hVFApGn+Dxu2slBTCM0fLNeSsFJHfH8N2QQAoUXrTp66hVFApGn+Dxu2slBTCM0fLNeSsFJHfH8N2QQAoUXrTp66hVFApGn+Dxu2slBTCM0fLNeSsFJHfH8N2QQAoUXrTp66hVFApGn+Dxu2slBTCM0fLNeSsFJHfH8N2QQAoUXrTp66hVFApGn+Dxu2slBTCM0fLNeSsFJHfH8N2QQAoUXrTp66hVFApGn+Dxu2slBTCM0fLNeSsFJHfH8N2QQAoUXrTp66hVFApGn+Dxu2slBTCM0fLNeSwFJHfH8N2QQAoUXrTp66hVFApGn+Dxu2slBTCM0fLNeSsFJHfH8N2QQAoUXrTp66hVFApGn+Dxu2slBTCM0fLNeSsFJHfH8N2QQAoUXrTp66hVFApGn+Dxu2slBTCM0fLNeSsFJHfH8N2QQAoUXrTp66hVFApGn+Dxu2slBTCM0fLNeSsFJHfH8N2QQAoUXrTp66hVFApGn+Dxu2slBTCM0fLNeSsFJHfH8N2QQAoUXrTp66hVFApGn+Dxu2slBTCM0fLNeSsFJHfH8N2QQAoUXrTp66hVFApGn+Dxu2slBTCM0fLNeSsFJHfH8N2QQAoUXrTp66hVFApGn+Dxu2slBTCM0fLNeSsFJHfH8N2QQAoUXrTp66hVFApGn+Dxu2slBTCM0fLNeSsFJHfH8N2QQAoUXrTp66hVFApGn+Dxu2slBTCM0fLNeSsFJHfH8N2QQAoUXrTp66hVFApGn+Dxu2slBTCM0fLNeSsFJHfH8N2QQAoUXrTp66hVFApGn+Dxu2slBTCM0fLNeSsFJHfH8N2QQAoUXrTp66hVFApGn+Dxu2slBTCM0fLNeSsFJHfH8N2QQAoUXrTp66hVFA==');
            audio.volume = 0.3;
            audio.play().catch(() => {
                // Ignore audio play errors (browser restrictions)
            });
        } catch (error) {
            // Ignore audio errors
        }
    }
    
    updateConnectionStatus(connected) {
        const statusElement = document.getElementById('connectionStatus');
        if (statusElement) {
            if (connected) {
                statusElement.textContent = 'Live';
                statusElement.className = 'badge bg-success ms-2';
                statusElement.style.display = 'none'; // Hide when connected
            } else {
                statusElement.textContent = 'Offline';
                statusElement.className = 'badge bg-warning ms-2';
                statusElement.style.display = 'inline';
            }
        }
    }
    
    updatePageTitle(unreadCount) {
        const baseTitle = document.title.replace(/^\(\d+\) /, '');
        if (unreadCount > 0) {
            document.title = `(${unreadCount}) ${baseTitle}`;
        } else {
            document.title = baseTitle;
        }
    }
    
    formatTimeAgo(dateString) {
        const date = new Date(dateString);
        const now = new Date();
        const diffInSeconds = Math.floor((now - date) / 1000);
        
        if (diffInSeconds < 60) return 'Just now';
        if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
        if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`;
        if (diffInSeconds < 2592000) return `${Math.floor(diffInSeconds / 86400)}d ago`;
        
        return date.toLocaleDateString();
    }
    
    // Public API methods
    disconnect() {
        if (this.socket) {
            this.socket.close(1000, 'Manual disconnect');
        }
        this.stopPolling();
    }
    
    reconnect() {
        this.disconnect();
        setTimeout(() => {
            this.connectWebSocket();
        }, 1000);
    }
}

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Only initialize if user is authenticated
    const isAuthenticated = document.body.dataset.userId || 
                           document.querySelector('meta[name="user-authenticated"]') ||
                           window.currentUserId;
    
    if (isAuthenticated) {
        window.notificationManager = new NotificationManager();
    }
});

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = NotificationManager;
}