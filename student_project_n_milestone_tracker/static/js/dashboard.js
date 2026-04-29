/**
 * MilestoneTrack Dashboard JavaScript
 * Handles interactivity, charts, and AJAX operations
 * Production-ready, clean, and modular
 */

// =====================================================
// CHART.JS INITIALIZATION
// =====================================================

/**
 * Initialize Phase-wise Completion Bar Chart
 * Shows progress across each phase
 */
function initPhaseChart(data = {}) {
    const ctx = document.getElementById('phaseChart');
    if (!ctx) return;

    const labels = data.labels || ['Synopsis', 'Phase 1', 'Phase 2', 'Final Report', 'Publication'];
    const values = data.values || [0, 0, 0, 0, 0];
    const colors = values.map(value => value >= 75 ? '#10b981' : value >= 40 ? '#3b82f6' : '#9ca3af');

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels,
            datasets: [{
                label: 'Submissions by Phase',
                data: values,
                backgroundColor: colors,
                borderRadius: 8,
                borderSkipped: false,
            }]
        },
        options: {
            indexAxis: 'x',
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        font: { size: 12, weight: '500' },
                        color: '#6b7280',
                        padding: 15
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: (value) => `${value}`,
                        font: { size: 11 },
                        color: '#9ca3af'
                    },
                    grid: {
                        drawBorder: false,
                        color: '#f3f4f6'
                    }
                },
                x: {
                    ticks: {
                        font: { size: 12, weight: '500' },
                        color: '#6b7280'
                    },
                    grid: {
                        display: false,
                        drawBorder: false
                    }
                }
            }
        }
    });
}

/**
 * Initialize Domain Distribution Pie Chart
 * Shows project distribution across domains
 */
function initDomainChart(data = {}) {
    const ctx = document.getElementById('domainChart');
    if (!ctx) return;

    const labels = data.labels || ['AI/ML', 'IoT', 'Blockchain', 'Security', 'Web'];
    const values = data.values || [0, 0, 0, 0, 0];
    const palette = ['#3b82f6', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981'];

    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels,
            datasets: [{
                data: values,
                backgroundColor: palette.slice(0, values.length),
                borderColor: '#ffffff',
                borderWidth: 2,
                hoverOffset: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        font: { size: 12, weight: '500' },
                        color: '#6b7280',
                        padding: 15,
                        usePointStyle: true
                    }
                }
            }
        }
    });
}

/**
 * Initialize Submission Trends Line Chart
 * Shows submission activity over time
 */
function initTrendChart(data = {}) {
    const ctx = document.getElementById('trendChart');
    if (!ctx) return;

    const labels = data.labels || [];
    const values = data.values || [];

    new Chart(ctx, {
        type: 'line',
        data: {
            labels,
            datasets: [{
                label: 'New Projects',
                data: values,
                borderColor: '#3b82f6',
                backgroundColor: 'rgba(59, 130, 246, 0.1)',
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                pointRadius: 5,
                pointBackgroundColor: '#3b82f6',
                pointBorderColor: '#ffffff',
                pointBorderWidth: 2,
                pointHoverRadius: 7
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        font: { size: 12, weight: '500' },
                        color: '#6b7280',
                        usePointStyle: true
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        font: { size: 11 },
                        color: '#9ca3af'
                    },
                    grid: {
                        drawBorder: false,
                        color: '#f3f4f6'
                    }
                },
                x: {
                    ticks: {
                        font: { size: 11, weight: '500' },
                        color: '#6b7280'
                    },
                    grid: {
                        display: false,
                        drawBorder: false
                    }
                }
            }
        }
    });
}

// =====================================================
// SEARCH & FILTER FUNCTIONALITY
// =====================================================

/**
 * Project Search with Real-time Filtering
 * Filters table rows based on search input
 */
document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('projectSearch');
    if (searchInput) {
        searchInput.addEventListener('input', function(e) {
            const searchTerm = e.target.value.toLowerCase();
            const tableRows = document.querySelectorAll('table tbody tr');
            
            tableRows.forEach(row => {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(searchTerm) ? '' : 'none';
            });
        });
    }
});

// =====================================================
// AJAX OPERATIONS
// =====================================================

/**
 * Generic AJAX Request Handler
 * @param {string} url - The endpoint URL
 * @param {string} method - HTTP method (GET, POST, etc.)
 * @param {object} data - Data to send (for POST)
 * @returns {Promise}
 */
function makeAjaxRequest(url, method = 'GET', data = null) {
    const options = {
        method: method,
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        }
    };

    if (data && method !== 'GET') {
        options.body = JSON.stringify(data);
    }

    return fetch(url, options)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .catch(error => {
            console.error('AJAX Error:', error);
            showNotification('An error occurred. Please try again.', 'error');
            throw error;
        });
}

/**
 * Get CSRF Token from Cookie
 * Required for Django CSRF protection
 */
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

/**
 * Check Project Title Validity
 * AJAX call to validate title against existing projects
 */
function validateProjectTitle(title, teamId = null) {
    const data = {
        title: title,
        team_id: teamId
    };

    return makeAjaxRequest('/api/validate-title/', 'POST', data)
        .then(response => {
            return response.valid;
        });
}

/**
 * Check Similarity Between Projects
 * AJAX call to similarity service
 */
function checkSimilarity(projectId1, projectId2) {
    const data = {
        project1_id: projectId1,
        project2_id: projectId2
    };

    return makeAjaxRequest('/api/check-similarity/', 'POST', data)
        .then(response => {
            return {
                similarity_score: response.similarity_score,
                is_flagged: response.is_flagged
            };
        });
}

/**
 * Submit Feedback Response
 * AJAX call to submit feedback resolution
 */
function submitFeedbackResponse(feedbackId, responseText) {
    const data = {
        feedback_id: feedbackId,
        response: responseText
    };

    return makeAjaxRequest('/api/feedback/respond/', 'POST', data)
        .then(response => {
            if (response.success) {
                showNotification('Feedback submitted successfully', 'success');
                return response;
            } else {
                throw new Error(response.error);
            }
        });
}

/**
 * Upload Submission Version
 * Handles file upload with progress tracking
 */
function uploadSubmissionVersion(submissionId, fileInput, changeSummary = '') {
    const formData = new FormData();
    formData.append('submission_id', submissionId);
    formData.append('file', fileInput.files[0]);
    formData.append('change_summary', changeSummary);
    formData.append('csrftoken', getCookie('csrftoken'));

    return new Promise((resolve, reject) => {
        fetch('/api/submissions/upload/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification('File uploaded successfully', 'success');
                resolve(data);
            } else {
                throw new Error(data.error);
            }
        })
        .catch(error => {
            console.error('Upload Error:', error);
            showNotification('Upload failed. Please try again.', 'error');
            reject(error);
        });
    });
}

/**
 * Mark Feedback as Resolved
 * Updates feedback status
 */
function markFeedbackResolved(feedbackId) {
    const data = {
        feedback_id: feedbackId,
        resolved: true
    };

    return makeAjaxRequest(`/projects/feedback/${feedbackId}/resolve/`, 'POST', data)
        .then(response => {
            if (response.success) {
                showNotification('Feedback marked as resolved', 'success');
                // Remove the element from DOM with animation
                const feedbackCard = document.querySelector(`[data-feedback-id="${feedbackId}"]`);
                if (feedbackCard) {
                    feedbackCard.style.opacity = '0';
                    feedbackCard.style.transform = 'translateX(20px)';
                    setTimeout(() => feedbackCard.remove(), 300);
                }
                return response;
            }
        });
}

// =====================================================
// NOTIFICATION SYSTEM
// =====================================================

/**
 * Show Notification Toast
 * @param {string} message - Message to display
 * @param {string} type - 'success', 'error', 'warning', 'info'
 * @param {number} duration - Duration in milliseconds (default: 3000)
 */
function showNotification(message, type = 'info', duration = 3000) {
    const notification = document.createElement('div');
    notification.className = `fixed top-4 right-4 p-4 rounded-lg shadow-lg transform transition-all duration-300 z-50`;
    
    const typeClasses = {
        success: 'bg-green-100 text-green-800 border border-green-300',
        error: 'bg-red-100 text-red-800 border border-red-300',
        warning: 'bg-yellow-100 text-yellow-800 border border-yellow-300',
        info: 'bg-blue-100 text-blue-800 border border-blue-300'
    };

    const icons = {
        success: 'ph-check-circle',
        error: 'ph-x-circle',
        warning: 'ph-warning-circle',
        info: 'ph-info'
    };

    notification.className += ` ${typeClasses[type] || typeClasses.info}`;
    notification.innerHTML = `
        <div class="flex items-center gap-3">
            <i class="ph ${icons[type] || icons.info} text-xl"></i>
            <span>${message}</span>
        </div>
    `;

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.style.opacity = '0';
        notification.style.transform = 'translateY(-10px)';
        setTimeout(() => notification.remove(), 300);
    }, duration);
}

// =====================================================
// INTERACTIVE COMPONENTS
// =====================================================

/**
 * Initialize Modal Functionality
 * Simple modal open/close system
 */
function initModals() {
    // Open modal
    document.querySelectorAll('[data-modal-trigger]').forEach(trigger => {
        trigger.addEventListener('click', function() {
            const modalId = this.getAttribute('data-modal-trigger');
            const modal = document.getElementById(modalId);
            if (modal) {
                modal.classList.remove('hidden');
                modal.classList.add('flex');
            }
        });
    });

    // Close modal
    document.querySelectorAll('[data-modal-close]').forEach(closeBtn => {
        closeBtn.addEventListener('click', function() {
            const modal = this.closest('[data-modal]');
            if (modal) {
                modal.classList.add('hidden');
                modal.classList.remove('flex');
            }
        });
    });

    // Close on background click
    document.querySelectorAll('[data-modal]').forEach(modal => {
        modal.addEventListener('click', function(e) {
            if (e.target === this) {
                this.classList.add('hidden');
                this.classList.remove('flex');
            }
        });
    });
}

/**
 * Initialize Dropdown Menus
 * Simple dropdown functionality
 */
function initDropdowns() {
    document.querySelectorAll('[data-dropdown-trigger]').forEach(trigger => {
        trigger.addEventListener('click', function() {
            const dropdown = this.nextElementSibling;
            if (dropdown && dropdown.classList.contains('dropdown-menu')) {
                dropdown.classList.toggle('hidden');
            }
        });
    });

    // Close dropdown when clicking outside
    document.addEventListener('click', function(e) {
        document.querySelectorAll('.dropdown-menu').forEach(menu => {
            if (!menu.previousElementSibling.contains(e.target) && !menu.contains(e.target)) {
                menu.classList.add('hidden');
            }
        });
    });
}

/**
 * Initialize Status Badges
 * Add color coding to status elements
 */
function initStatusBadges() {
    const statusMap = {
        'approved': { bg: '#dcfce7', text: '#166534', icon: 'ph-check-circle' },
        'pending': { bg: '#fef3c7', text: '#92400e', icon: 'ph-clock' },
        'blocked': { bg: '#fee2e2', text: '#991b1b', icon: 'ph-x-circle' },
        'active': { bg: '#dbeafe', text: '#1e40af', icon: 'ph-arrow-circle-right' }
    };

    document.querySelectorAll('[data-status]').forEach(element => {
        const status = element.getAttribute('data-status').toLowerCase();
        if (statusMap[status]) {
            const colors = statusMap[status];
            element.style.backgroundColor = colors.bg;
            element.style.color = colors.text;
        }
    });
}

/**
 * Initialize Animated Progress Bars
 * Trigger animation on scroll into view
 */
function initProgressBars() {
    const progressBars = document.querySelectorAll('[data-progress]');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const progressValue = entry.target.getAttribute('data-progress');
                entry.target.style.width = progressValue + '%';
                observer.unobserve(entry.target);
            }
        });
    });

    progressBars.forEach(bar => observer.observe(bar));
}

/**
 * Initialize Smooth Scroll Behavior
 * Smooth scrolling for anchor links
 */
function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });
}

/**
 * Initialize Keyboard Shortcuts
 * Global keyboard shortcuts for power users
 */
function initKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
        // Cmd/Ctrl + S: Save (prevent browser save)
        if ((e.metaKey || e.ctrlKey) && e.key === 's') {
            e.preventDefault();
            showNotification('Changes are saved automatically', 'info');
        }

        // Cmd/Ctrl + K: Open command palette (future feature)
        if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
            e.preventDefault();
            console.log('Command palette would open here');
        }

        // Esc: Close any open modals
        if (e.key === 'Escape') {
            document.querySelectorAll('[data-modal]').forEach(modal => {
                modal.classList.add('hidden');
            });
        }
    });
}

// =====================================================
// INITIALIZATION ON PAGE LOAD
// =====================================================

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all components
    initModals();
    initDropdowns();
    initStatusBadges();
    initProgressBars();
    initSmoothScroll();
    initKeyboardShortcuts();

    // Add fade-in animation to page
    document.body.style.opacity = '1';
});

// =====================================================
// UTILITY FUNCTIONS
// =====================================================

/**
 * Format Date to Readable String
 * @param {Date} date - Date object
 * @returns {string} Formatted date
 */
function formatDate(date) {
    const options = { year: 'numeric', month: 'short', day: 'numeric' };
    return new Date(date).toLocaleDateString('en-US', options);
}

/**
 * Calculate Days Ago
 * @param {Date} date - Date object
 * @returns {string} Relative time string
 */
function daysAgo(date) {
    const now = new Date();
    const then = new Date(date);
    const diffTime = Math.abs(now - then);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 0) return 'Today';
    if (diffDays === 1) return 'Yesterday';
    if (diffDays < 7) return diffDays + ' days ago';
    if (diffDays < 30) return Math.floor(diffDays / 7) + ' weeks ago';
    return Math.floor(diffDays / 30) + ' months ago';
}

/**
 * Debounce Function
 * Prevents excessive function calls
 */
function debounce(func, delay = 300) {
    let timeoutId;
    return function(...args) {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => func.apply(this, args), delay);
    };
}

/**
 * Throttle Function
 * Limits function call frequency
 */
function throttle(func, limit = 300) {
    let inThrottle;
    return function(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// Export for use in modules if needed
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        makeAjaxRequest,
        getCookie,
        validateProjectTitle,
        checkSimilarity,
        submitFeedbackResponse,
        uploadSubmissionVersion,
        markFeedbackResolved,
        showNotification,
        formatDate,
        daysAgo,
        debounce,
        throttle
    };
}
