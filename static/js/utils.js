// Utility functions for the application

// Show toast notification
function showToast(message, type = 'success') {
    const container = document.getElementById('toast-container');
    if (!container) return;
    
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s';
        setTimeout(() => {
            container.removeChild(toast);
        }, 300);
    }, 3000);
}

// Loading indicator
let loadingElement = null;

function showLoading() {
    if (loadingElement) return;
    
    loadingElement = document.createElement('div');
    loadingElement.className = 'loading';
    loadingElement.style.position = 'fixed';
    loadingElement.style.top = '50%';
    loadingElement.style.left = '50%';
    loadingElement.style.transform = 'translate(-50%, -50%)';
    loadingElement.style.zIndex = '9999';
    loadingElement.style.width = '50px';
    loadingElement.style.height = '50px';
    loadingElement.style.border = '5px solid #e0e0e0';
    loadingElement.style.borderTopColor = '#1a237e';
    loadingElement.style.borderRadius = '50%';
    loadingElement.style.animation = 'spin 0.8s linear infinite';
    
    document.body.appendChild(loadingElement);
}

function hideLoading() {
    if (loadingElement) {
        document.body.removeChild(loadingElement);
        loadingElement = null;
    }
}

// Format date
function formatDate(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString();
}

// Format datetime
function formatDateTime(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleString();
}

// Validate email
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

// Validate phone
function validatePhone(phone) {
    const re = /^[+]?[(]?[0-9]{3}[)]?[-\s.]?[0-9]{3}[-\s.]?[0-9]{4,6}$/;
    return re.test(phone);
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

// Check authentication
async function checkAuth() {
    try {
        const response = await fetch('/api/auth/check', { method: 'GET' });
        return response.ok;
    } catch (error) {
        return false;
    }
}

// Handle API errors
function handleApiError(error) {
    console.error('API Error:', error);
    showToast('An error occurred. Please try again.', 'error');
}

// Add slideOut animation
const style = document.createElement('style');
style.textContent = `
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);
