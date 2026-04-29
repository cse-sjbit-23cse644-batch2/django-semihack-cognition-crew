// Utility functions for the application

// API request helper
async function apiRequest(url, options = {}) {
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        }
    };

    const config = { ...defaultOptions, ...options };
    
    try {
        const response = await fetch(url, config);
        if (!response.ok) {
            throw new Error(`API Error: ${response.statusText}`);
        }
        return await response.json();
    } catch (error) {
        console.error('API Request failed:', error);
        throw error;
    }
}

// Get CSRF token from cookie
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Show notification
function showNotification(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} fixed top-4 right-4 max-w-sm z-50`;
    alertDiv.textContent = message;
    
    document.body.appendChild(alertDiv);
    
    setTimeout(() => {
        alertDiv.remove();
    }, 3000);
}

// Format date
function formatDate(dateString) {
    const options = { year: 'numeric', month: 'short', day: 'numeric' };
    return new Date(dateString).toLocaleDateString(undefined, options);
}

// Format time
function formatTime(dateString) {
    const options = { hour: '2-digit', minute: '2-digit' };
    return new Date(dateString).toLocaleTimeString(undefined, options);
}

// Load notifications
async function loadNotifications() {
    try {
        const response = await fetch('/api/notifications/', {
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            }
        });
        
        if (response.status === 401 || response.status === 403) {
            if (window.notificationInterval) {
                clearInterval(window.notificationInterval);
            }
            return;
        }
        
        if (!response.ok) {
            throw new Error(`API Error: ${response.statusText}`);
        }
        
        const data = await response.json();
        const notifCount = document.getElementById('notification-count');
        if (notifCount) {
            notifCount.textContent = data.unread_count;
        }
        return data.notifications;
    } catch (error) {
        console.error('Error loading notifications:', error);
    }
}

// Mark notification as read
async function markNotificationRead(notificationId) {
    try {
        await apiRequest(`/api/notifications/${notificationId}/read/`, {
            method: 'POST'
        });
        loadNotifications();
    } catch (error) {
        console.error('Error marking notification as read:', error);
    }
}

// Load user profile
async function loadUserProfile() {
    try {
        const data = await apiRequest('/api/auth/profile/');
        return data;
    } catch (error) {
        console.error('Error loading user profile:', error);
    }
}

// Debounce function
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Initialize on document ready
document.addEventListener('DOMContentLoaded', () => {
    // Only poll if user is authenticated (indicated by global variable or logout button)
    const isAuth = window.USER_IS_AUTHENTICATED || document.querySelector('form[action*="logout"]') !== null;
    
    if (isAuth) {
        // Load notifications
        loadNotifications();
        
        // Refresh notifications every 30 seconds
        window.notificationInterval = setInterval(loadNotifications, 30000);
    }
});
