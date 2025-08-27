// Main JavaScript functionality for LinkedIn Scheduler

// Utility functions
function showLoading() {
    document.getElementById('loading-overlay').style.display = 'flex';
}

function hideLoading() {
    document.getElementById('loading-overlay').style.display = 'none';
}

function showFlashMessage(message, type = 'info') {
    const flashContainer = document.querySelector('.flash-messages') || createFlashContainer();
    
    const flashMessage = document.createElement('div');
    flashMessage.className = `flash-message flash-${type}`;
    flashMessage.innerHTML = `
        <span>${message}</span>
        <button class="flash-close" onclick="this.parentElement.remove()">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    flashContainer.appendChild(flashMessage);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (flashMessage.parentElement) {
            flashMessage.remove();
        }
    }, 5000);
}

function createFlashContainer() {
    const container = document.createElement('div');
    container.className = 'flash-messages';
    document.body.appendChild(container);
    return container;
}

// API helper functions
async function apiCall(url, options = {}) {
    try {
        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('API call failed:', error);
        throw error;
    }
}

// Auto-hide flash messages on click
document.addEventListener('DOMContentLoaded', function() {
    // Auto-hide existing flash messages
    const flashMessages = document.querySelectorAll('.flash-message');
    flashMessages.forEach(message => {
        setTimeout(() => {
            if (message.parentElement) {
                message.remove();
            }
        }, 5000);
    });
    
    // Handle flash message close buttons
    document.addEventListener('click', function(e) {
        if (e.target.closest('.flash-close')) {
            e.target.closest('.flash-message').remove();
        }
    });
});

// Form validation helpers
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

function validateUrl(url) {
    try {
        new URL(url);
        return true;
    } catch {
        return false;
    }
}

// Date and time utilities
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

function formatDateTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: 'numeric',
        minute: '2-digit',
        hour12: true
    });
}

function getLocalISOString(date = new Date()) {
    const offset = date.getTimezoneOffset();
    const localDate = new Date(date.getTime() - offset * 60000);
    return localDate.toISOString().slice(0, 16);
}

// Image handling utilities
function validateImageFile(file) {
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif'];
    const maxSize = 16 * 1024 * 1024; // 16MB
    
    if (!allowedTypes.includes(file.type)) {
        throw new Error('Please select a valid image file (JPEG, PNG, or GIF)');
    }
    
    if (file.size > maxSize) {
        throw new Error('File size must be less than 16MB');
    }
    
    return true;
}

function createImagePreview(file, callback) {
    const reader = new FileReader();
    reader.onload = function(e) {
        callback(e.target.result);
    };
    reader.readAsDataURL(file);
}

// Text utilities
function truncateText(text, maxLength) {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
}

function countCharacters(text) {
    return text.length;
}

function formatCharacterCount(current, max) {
    const percentage = (current / max) * 100;
    let className = '';
    
    if (percentage > 90) {
        className = 'text-danger';
    } else if (percentage > 80) {
        className = 'text-warning';
    }
    
    return {
        text: `${current} / ${max}`,
        className
    };
}

// Local storage utilities
function saveToLocalStorage(key, data) {
    try {
        localStorage.setItem(key, JSON.stringify(data));
        return true;
    } catch (error) {
        console.error('Failed to save to localStorage:', error);
        return false;
    }
}

function getFromLocalStorage(key, defaultValue = null) {
    try {
        const item = localStorage.getItem(key);
        return item ? JSON.parse(item) : defaultValue;
    } catch (error) {
        console.error('Failed to get from localStorage:', error);
        return defaultValue;
    }
}

function removeFromLocalStorage(key) {
    try {
        localStorage.removeItem(key);
        return true;
    } catch (error) {
        console.error('Failed to remove from localStorage:', error);
        return false;
    }
}

// Draft auto-save functionality
class DraftManager {
    constructor(key, saveInterval = 30000) { // 30 seconds
        this.key = key;
        this.saveInterval = saveInterval;
        this.autoSaveTimer = null;
        this.isDirty = false;
    }
    
    startAutoSave(getDataFn) {
        this.stopAutoSave();
        this.autoSaveTimer = setInterval(() => {
            if (this.isDirty) {
                const data = getDataFn();
                if (data && (data.content || data.image)) {
                    this.saveDraft(data);
                    this.isDirty = false;
                    console.log('Draft auto-saved');
                }
            }
        }, this.saveInterval);
    }
    
    stopAutoSave() {
        if (this.autoSaveTimer) {
            clearInterval(this.autoSaveTimer);
            this.autoSaveTimer = null;
        }
    }
    
    markDirty() {
        this.isDirty = true;
    }
    
    saveDraft(data) {
        const draftData = {
            ...data,
            timestamp: new Date().toISOString()
        };
        return saveToLocalStorage(this.key, draftData);
    }
    
    loadDraft() {
        return getFromLocalStorage(this.key);
    }
    
    clearDraft() {
        this.stopAutoSave();
        return removeFromLocalStorage(this.key);
    }
}

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + S to save (prevent default browser save)
    if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        e.preventDefault();
        
        // Trigger save if we're on a form page
        const submitBtn = document.querySelector('form button[type="submit"]');
        if (submitBtn && !submitBtn.disabled) {
            submitBtn.click();
        }
    }
    
    // Escape to close modals
    if (e.key === 'Escape') {
        const openModal = document.querySelector('.modal[style*="flex"]');
        if (openModal) {
            openModal.style.display = 'none';
        }
    }
});

// Smooth scrolling for anchor links
document.addEventListener('click', function(e) {
    const link = e.target.closest('a[href^="#"]');
    if (link) {
        e.preventDefault();
        const targetId = link.getAttribute('href').substring(1);
        const targetElement = document.getElementById(targetId);
        
        if (targetElement) {
            targetElement.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    }
});

// Handle form submissions with loading states
function handleFormSubmission(form, submitHandler) {
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const submitBtn = form.querySelector('button[type="submit"]');
        const originalText = submitBtn.innerHTML;
        
        // Disable form and show loading
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
        showLoading();
        
        try {
            await submitHandler(new FormData(form));
        } catch (error) {
            showFlashMessage(error.message || 'An error occurred', 'error');
        } finally {
            // Re-enable form and hide loading
            submitBtn.disabled = false;
            submitBtn.innerHTML = originalText;
            hideLoading();
        }
    });
}

// Initialize tooltips (if using a tooltip library)
function initializeTooltips() {
    const tooltipElements = document.querySelectorAll('[data-tooltip]');
    tooltipElements.forEach(element => {
        element.addEventListener('mouseenter', function() {
            const tooltip = document.createElement('div');
            tooltip.className = 'tooltip';
            tooltip.textContent = this.dataset.tooltip;
            document.body.appendChild(tooltip);
            
            const rect = this.getBoundingClientRect();
            tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';
            tooltip.style.top = rect.top - tooltip.offsetHeight - 10 + 'px';
        });
        
        element.addEventListener('mouseleave', function() {
            const tooltip = document.querySelector('.tooltip');
            if (tooltip) {
                tooltip.remove();
            }
        });
    });
}

// Debounce function for performance
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

// Throttle function for performance
function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// Initialize common functionality when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    initializeTooltips();
    
    // Add loading states to all buttons with data-loading attribute
    const loadingButtons = document.querySelectorAll('button[data-loading]');
    loadingButtons.forEach(button => {
        button.addEventListener('click', function() {
            if (!this.disabled) {
                const originalText = this.innerHTML;
                this.disabled = true;
                this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> ' + (this.dataset.loading || 'Loading...');
                
                // Re-enable after 5 seconds as fallback
                setTimeout(() => {
                    this.disabled = false;
                    this.innerHTML = originalText;
                }, 5000);
            }
        });
    });
    
    // Add confirmation dialogs to buttons with data-confirm attribute
    const confirmButtons = document.querySelectorAll('button[data-confirm], a[data-confirm]');
    confirmButtons.forEach(element => {
        element.addEventListener('click', function(e) {
            const message = this.dataset.confirm || 'Are you sure?';
            if (!confirm(message)) {
                e.preventDefault();
                return false;
            }
        });
    });
});

// Export utilities for use in other scripts
window.LinkedInScheduler = {
    showLoading,
    hideLoading,
    showFlashMessage,
    apiCall,
    validateImageFile,
    createImagePreview,
    formatDate,
    formatDateTime,
    getLocalISOString,
    DraftManager,
    debounce,
    throttle,
    saveToLocalStorage,
    getFromLocalStorage,
    removeFromLocalStorage
};
