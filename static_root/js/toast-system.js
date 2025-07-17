// Global Toast System - Reusable Alpine.js Component
// Can be used across all forms incrementally

window.ToastSystem = {
    // Global toast store
    toasts: [],
    nextId: 1,

    // Add a new toast
    add(message, type = 'error', duration = 5000) {
        const toast = {
            id: this.nextId++,
            message: message,
            type: type,
            duration: duration,
            show: false,
            removing: false
        };

        this.toasts.push(toast);

        // Trigger show animation
        setTimeout(() => {
            toast.show = true;
        }, 50);

        // Auto remove
        if (duration > 0) {
            setTimeout(() => {
                this.remove(toast.id);
            }, duration);
        }

        return toast.id;
    },

    // Remove a toast
    remove(id) {
        const toast = this.toasts.find(t => t.id === id);
        if (toast && !toast.removing) {
            toast.removing = true;
            toast.show = false;

            // Remove from array after animation
            setTimeout(() => {
                const index = this.toasts.findIndex(t => t.id === id);
                if (index > -1) {
                    this.toasts.splice(index, 1);
                }
            }, 300);
        }
    },

    // Clear all toasts
    clear() {
        this.toasts.forEach(toast => {
            this.remove(toast.id);
        });
    },

    // Helper: Show form errors from Django
    showFormErrors(errors, delay = 300) {
        if (!errors || errors.length === 0) {
            return;
        }
        
        errors.forEach((error, index) => {
            setTimeout(() => {
                this.add(error, 'error');
            }, index * delay);
        });
    },

    // Helper: Show Django messages with proper types
    showDjangoMessages(messages, delay = 300) {
        if (!messages || messages.length === 0) {
            return;
        }
        
        // Group messages by type
        const groupedMessages = {};
        messages.forEach(msgObj => {
            const toastType = this.mapDjangoTagsToType(msgObj.type);
            if (!groupedMessages[toastType]) {
                groupedMessages[toastType] = [];
            }
            groupedMessages[toastType].push(msgObj.message);
        });
        
        // Create summary toasts for each type
        Object.keys(groupedMessages).forEach((type, index) => {
            setTimeout(() => {
                if (groupedMessages[type].length === 1) {
                    // Single message - show as is with longer duration
                    this.add(groupedMessages[type][0], type, type === 'error' ? 10000 : 6000);
                } else {
                    // Multiple messages - create summary
                    this.addSummaryToast(groupedMessages[type], type);
                }
            }, index * delay);
        });
    },

    // Add summary toast for multiple messages
    addSummaryToast(messages, type) {
        const titles = {
            'error': 'Por favor, corrija os seguintes erros:',
            'success': 'Operações realizadas com sucesso:',
            'warning': 'Atenção aos seguintes itens:',
            'info': 'Informações:'
        };
        
        const title = titles[type] || titles.error;
        const messageList = messages.map(msg => `• ${msg}`).join('\n');
        const summaryMessage = `${title}\n\n${messageList}`;
        
        this.add(summaryMessage, type, type === 'error' ? 12000 : 8000);
    },

    // Map Django message tags to toast types
    mapDjangoTagsToType(tags) {
        if (tags === 'danger' || tags === 'error') return 'error';
        if (tags === 'success') return 'success';
        if (tags === 'warning') return 'warning';
        if (tags === 'info' || tags === 'debug') return 'info';
        return 'error'; // default
    },

    // Helper: Show success message
    success(message, duration = 3000) {
        return this.add(message, 'success', duration);
    },

    // Helper: Show error message  
    error(message, duration = 8000) {
        return this.add(message, 'error', duration);
    },

    // Helper: Show warning message
    warning(message, duration = 4000) {
        return this.add(message, 'warning', duration);
    },

    // Helper: Show info message
    info(message, duration = 3000) {
        return this.add(message, 'info', duration);
    }
};

// Alpine.js Toast Component
function toastContainer() {
    return {
        toasts: [],
        
        init() {
            // Set up a watcher to sync with ToastSystem
            setInterval(() => {
                if (JSON.stringify(this.toasts) !== JSON.stringify(window.ToastSystem.toasts)) {
                    this.toasts = [...window.ToastSystem.toasts];
                }
            }, 100);
        },

        removeToast(id) {
            window.ToastSystem.remove(id);
        },

        getToastClasses(toast) {
            const baseClasses = 'toast mb-3 border-0 shadow-lg';
            const showClasses = toast.show ? 'show' : '';
            const typeClasses = {
                'error': 'bg-danger text-white',
                'success': 'bg-success text-white', 
                'warning': 'bg-warning text-dark',
                'info': 'bg-info text-white'
            };
            return `${baseClasses} ${showClasses} ${typeClasses[toast.type] || typeClasses.error}`;
        },

        getIconClass(toast) {
            const icons = {
                'error': 'oi oi-warning',
                'success': 'oi oi-check',
                'warning': 'oi oi-warning', 
                'info': 'oi oi-info'
            };
            return icons[toast.type] || icons.error;
        },

        getTitle(toast) {
            const titles = {
                'error': 'Erro',
                'success': 'Sucesso',
                'warning': 'Atenção',
                'info': 'Informação'
            };
            return titles[toast.type] || titles.error;
        },

        checkForFormErrors() {
            // Check for Django messages
            if (window.djangoMessages && window.djangoMessages.length > 0) {
                if (window.ToastSystem) {
                    window.ToastSystem.showDjangoMessages(window.djangoMessages);
                }
            }
        }
    }
}

// Make it globally available
window.toastContainer = toastContainer;