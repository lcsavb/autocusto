/**
 * Vanilla JS Toast System - Module Pattern
 * Replaces Alpine.js toast functionality while preserving PDF modal Alpine.js usage
 * Features: Performance metrics, extensive debugging, centralized config
 */

// Centralized Configuration
const TOAST_CONFIG = {
    durations: {
        error: 8000,
        success: 5000,
        warning: 4000,
        info: 3000,
        summaryError: 12000,
        summaryOther: 8000
    },
    delays: {
        pdfGenerationError: 1000,
        networkError: 1500,
        buttonReEnable: 500,
        buttonReEnableError: 1500,
        dateValidation: 300,
        formErrors: 300,
        djangoMessages: 300
    },
    animations: {
        showDelay: 50,
        removeDelay: 300
    },
    debug: {
        enabled: true,
        performanceMetrics: true,
        domMutations: true,
        timingAnalysis: true
    }
};

// Toast System Module
window.Toast = (function() {
    'use strict';
    
    // Private state
    let items = [];
    let nextId = 1;
    let container = null;
    let debugMode = TOAST_CONFIG.debug.enabled;
    let performanceMetrics = {
        totalCreated: 0,
        totalRemoved: 0,
        averageCreationTime: 0,
        averageRemovalTime: 0,
        peakConcurrentToasts: 0,
        memoryUsage: []
    };

    // Private utility functions
    function log(level, message, data = null) {
        if (!debugMode) return;
        
        const timestamp = new Date().toISOString().split('T')[1].slice(0, -1);
        const prefix = `[Toast ${level.toUpperCase()}] ${timestamp}`;
        
        if (data) {
            console.log(`${prefix} ${message}`, data);
        } else {
            console.log(`${prefix} ${message}`);
        }
    }

    function measurePerformance(operation, fn) {
        if (!TOAST_CONFIG.debug.performanceMetrics) return fn();
        
        const startTime = performance.now();
        const result = fn();
        const endTime = performance.now();
        const duration = endTime - startTime;
        
        log('PERF', `${operation} took ${duration.toFixed(2)}ms`);
        
        // Update performance metrics
        if (operation === 'CREATE') {
            performanceMetrics.totalCreated++;
            performanceMetrics.averageCreationTime = 
                (performanceMetrics.averageCreationTime * (performanceMetrics.totalCreated - 1) + duration) 
                / performanceMetrics.totalCreated;
        } else if (operation === 'REMOVE') {
            performanceMetrics.totalRemoved++;
            performanceMetrics.averageRemovalTime = 
                (performanceMetrics.averageRemovalTime * (performanceMetrics.totalRemoved - 1) + duration) 
                / performanceMetrics.totalRemoved;
        }
        
        // Track peak concurrent toasts
        if (items.length > performanceMetrics.peakConcurrentToasts) {
            performanceMetrics.peakConcurrentToasts = items.length;
            log('PERF', `New peak concurrent toasts: ${items.length}`);
        }
        
        return result;
    }

    function trackMemoryUsage() {
        if (!TOAST_CONFIG.debug.performanceMetrics) return;
        
        const usage = {
            timestamp: Date.now(),
            itemCount: items.length,
            domElements: container ? container.children.length : 0,
            heapUsed: performance.memory ? performance.memory.usedJSHeapSize : 'N/A'
        };
        
        performanceMetrics.memoryUsage.push(usage);
        
        // Keep only last 100 measurements
        if (performanceMetrics.memoryUsage.length > 100) {
            performanceMetrics.memoryUsage.shift();
        }
        
        log('MEMORY', 'Memory usage tracked', usage);
    }

    function checkForConflicts() {
        const conflicts = [];
        
        // Skip conflict detection for now - just warn and continue
        log('INFO', 'Skipping conflict detection - allowing initialization to proceed');
        
        // Check for Bootstrap toast conflicts
        if (window.bootstrap && window.bootstrap.Toast) {
            log('WARN', 'Bootstrap Toast detected - potential CSS conflicts');
        }
        
        // Check for jQuery toast plugins
        if (window.$ && window.$.toast) {
            conflicts.push('jQuery toast plugin detected');
        }
        
        if (conflicts.length > 0) {
            log('ERROR', 'Toast system conflicts detected', conflicts);
        } else {
            log('INFO', 'No conflicts detected - safe to initialize');
        }
        
        return conflicts.length === 0;
    }

    function createContainer() {
        return measurePerformance('CREATE_CONTAINER', () => {
            let existingContainer = document.querySelector('.inline-toast-wrapper');
            if (existingContainer) {
                log('INFO', 'Using existing toast container');
                return existingContainer;
            }
            
            const newContainer = document.createElement('div');
            newContainer.className = 'inline-toast-wrapper';
            newContainer.setAttribute('data-toast-system', 'vanilla-js');
            
            // Ensure container has proper styling context
            if (TOAST_CONFIG.debug.domMutations) {
                log('DOM', 'Creating new toast container');
            }
            
            document.body.appendChild(newContainer);
            log('INFO', 'Toast container created and appended to body');
            
            return newContainer;
        });
    }

    function processDjangoMessages() {
        log('DJANGO', 'processDjangoMessages() called');
        log('DJANGO', 'window.djangoMessages exists?', !!window.djangoMessages);
        log('DJANGO', 'window.djangoMessages value:', window.djangoMessages);
        
        if (!window.djangoMessages || !Array.isArray(window.djangoMessages)) {
            log('INFO', 'No Django messages to process - either undefined or not array');
            return;
        }
        
        if (window.djangoMessages.length === 0) {
            log('INFO', 'Django messages array is empty');
            return;
        }
        
        log('INFO', `Processing ${window.djangoMessages.length} Django messages`);
        log('DJANGO', 'Full Django messages array:', window.djangoMessages);
        
        setTimeout(() => {
            log('DJANGO', `setTimeout fired after ${TOAST_CONFIG.delays.djangoMessages}ms`);
            
            window.djangoMessages.forEach((msg, index) => {
                let type = msg.type === 'danger' ? 'error' : msg.type;
                
                log('DJANGO', `Processing message ${index + 1}: ${type}`, {
                    originalType: msg.type,
                    mappedType: type,
                    message: msg.message
                });
                
                const toastId = add(msg.message, type);
                log('DJANGO', `Toast created with ID: ${toastId}`);
            });
            
            // Clear processed messages to prevent reprocessing
            window.djangoMessages = [];
            log('INFO', 'Django messages processed and cleared');
        }, TOAST_CONFIG.delays.djangoMessages);
    }

    function createToastElement(toast) {
        return measurePerformance('CREATE_ELEMENT', () => {
            const toastEl = document.createElement('div');
            toastEl.className = getToastClasses(toast);
            toastEl.setAttribute('role', 'alert');
            toastEl.setAttribute('aria-live', 'assertive');
            toastEl.setAttribute('aria-atomic', 'true');
            toastEl.setAttribute('data-toast-id', toast.id);
            
            toastEl.innerHTML = `
                <div class="toast-header">
                    <i class="${getIconClass(toast)} mr-2"></i>
                    <strong class="mr-auto">${getTitle(toast)}</strong>
                    <button type="button" class="ml-2 mb-1 close" aria-label="Close" data-toast-close="${toast.id}">
                        <span aria-hidden="true">&times;</span>
                    </button>
                </div>
                <div class="toast-body">${formatMessage(toast.message)}</div>
            `;

            // Add click handler for close button
            const closeBtn = toastEl.querySelector(`[data-toast-close="${toast.id}"]`);
            closeBtn.addEventListener('click', (e) => {
                e.preventDefault();
                log('USER', `User closed toast ${toast.id}`);
                remove(toast.id);
            });

            if (TOAST_CONFIG.debug.domMutations) {
                log('DOM', `Created toast element for ID ${toast.id}`, {
                    type: toast.type,
                    messageLength: toast.message.length,
                    className: toastEl.className
                });
            }

            return toastEl;
        });
    }

    function getToastClasses(toast) {
        const baseClasses = 'toast mb-3 border-0 shadow-lg';
        const showClasses = toast.show ? 'show' : '';
        const typeClasses = {
            'error': 'bg-danger text-white',
            'success': 'bg-success text-white', 
            'warning': 'bg-warning text-dark',
            'info': 'bg-info text-white'
        };
        return `${baseClasses} ${showClasses} ${typeClasses[toast.type] || typeClasses.error}`;
    }

    function getIconClass(toast) {
        const icons = {
            'error': 'oi oi-warning',
            'success': 'oi oi-check',
            'warning': 'oi oi-warning', 
            'info': 'oi oi-info'
        };
        return icons[toast.type] || icons.error;
    }

    function getTitle(toast) {
        const titles = {
            'error': 'Erro',
            'success': 'Sucesso',
            'warning': 'Atenção',
            'info': 'Informação'
        };
        return titles[toast.type] || titles.error;
    }

    function formatMessage(message) {
        if (!message) return '';
        return message.split('\n')
            .map(line => line.trim())
            .filter(line => line.length > 0)
            .join('<br>');
    }

    // Public API
    function add(message, type = 'error', duration = null) {
        return measurePerformance('ADD', () => {
            log('ADD', `Adding toast: "${message}" (Type: ${type})`);
            
            // Validate inputs
            if (!message || typeof message !== 'string') {
                log('ERROR', 'Invalid message provided to add()', { message, type });
                return null;
            }
            
            // Use centralized config for duration if not specified
            if (duration === null) {
                duration = TOAST_CONFIG.durations[type] || TOAST_CONFIG.durations.error;
            }
            
            const toast = {
                id: nextId++,
                message: message,
                type: type,
                duration: duration,
                show: false,
                removing: false,
                element: null,
                createdAt: Date.now()
            };

            items.push(toast);
            log('STATE', `Toast ${toast.id} added to items array. Total: ${items.length}`);

            // Create DOM element
            toast.element = createToastElement(toast);
            container.appendChild(toast.element);

            // Track memory usage after DOM changes
            trackMemoryUsage();

            // Trigger show animation with timing analysis
            const showTimer = setTimeout(() => {
                measurePerformance('SHOW_ANIMATION', () => {
                    toast.show = true;
                    toast.element.classList.add('show');
                    
                    if (TOAST_CONFIG.debug.timingAnalysis) {
                        log('TIMING', `Toast ${toast.id} show animation triggered after ${TOAST_CONFIG.animations.showDelay}ms`);
                    }
                });
            }, TOAST_CONFIG.animations.showDelay);

            // Auto remove with timing analysis
            if (duration > 0) {
                const removeTimer = setTimeout(() => {
                    if (TOAST_CONFIG.debug.timingAnalysis) {
                        log('TIMING', `Auto-remove timer fired for toast ${toast.id} after ${duration}ms`);
                    }
                    remove(toast.id);
                }, duration);
                
                // Store timer IDs for potential cleanup
                toast.showTimer = showTimer;
                toast.removeTimer = removeTimer;
                
                log('TIMER', `Auto-remove timer set for toast ${toast.id} (${duration}ms)`);
            }

            return toast.id;
        });
    }

    function remove(id) {
        return measurePerformance('REMOVE', () => {
            log('REMOVE', `Attempting to remove toast ${id}`);
            
            const toast = items.find(t => t.id === id);
            if (!toast) {
                log('WARN', `Toast ${id} not found for removal`);
                return false;
            }
            
            if (toast.removing) {
                log('WARN', `Toast ${id} already being removed`);
                return false;
            }

            toast.removing = true;
            toast.show = false;
            
            // Clear any pending timers
            if (toast.showTimer) clearTimeout(toast.showTimer);
            if (toast.removeTimer) clearTimeout(toast.removeTimer);

            if (toast.element) {
                toast.element.classList.remove('show');
                
                if (TOAST_CONFIG.debug.domMutations) {
                    log('DOM', `Removed 'show' class from toast ${id}`);
                }
            }

            log('STATE', `Toast ${id} marked for removal`);

            // Remove from DOM and array after animation
            setTimeout(() => {
                measurePerformance('CLEANUP', () => {
                    const index = items.findIndex(t => t.id === id);
                    if (index > -1) {
                        const removedToast = items[index];
                        
                        if (removedToast.element && removedToast.element.parentNode) {
                            removedToast.element.parentNode.removeChild(removedToast.element);
                            
                            if (TOAST_CONFIG.debug.domMutations) {
                                log('DOM', `Removed toast ${id} element from DOM`);
                            }
                        }
                        
                        items.splice(index, 1);
                        
                        // Track memory usage after cleanup
                        trackMemoryUsage();
                        
                        log('STATE', `Toast ${id} removed from items array. Remaining: ${items.length}`);
                        
                        if (TOAST_CONFIG.debug.timingAnalysis) {
                            const lifespan = Date.now() - removedToast.createdAt;
                            log('TIMING', `Toast ${id} total lifespan: ${lifespan}ms`);
                        }
                    }
                });
            }, TOAST_CONFIG.animations.removeDelay);

            return true;
        });
    }

    function clear() {
        log('CLEAR', `Clearing all ${items.length} toasts`);
        const toastIds = items.map(t => t.id);
        toastIds.forEach(id => remove(id));
    }

    // Specialized methods
    function success(message, duration = null) {
        return add(message, 'success', duration);
    }

    function error(message, duration = null) {
        return add(message, 'error', duration);
    }

    function warning(message, duration = null) {
        return add(message, 'warning', duration);
    }

    function info(message, duration = null) {
        return add(message, 'info', duration);
    }

    function pdfGenerationError(message) {
        log('SPECIALIZED', `PDF generation error with ${TOAST_CONFIG.delays.pdfGenerationError}ms delay`);
        setTimeout(() => {
            error(message);
        }, TOAST_CONFIG.delays.pdfGenerationError);
    }

    function networkError(message) {
        log('SPECIALIZED', `Network error with ${TOAST_CONFIG.delays.networkError}ms delay`);
        setTimeout(() => {
            error(message);
        }, TOAST_CONFIG.delays.networkError);
    }

    function addSummaryToast(messages, type) {
        if (!Array.isArray(messages) || messages.length === 0) {
            log('WARN', 'Invalid messages array provided to addSummaryToast', messages);
            return null;
        }
        
        const titles = {
            'error': 'Por favor, corrija os seguintes erros:',
            'success': 'Operações realizadas com sucesso:',
            'warning': 'Atenção aos seguintes itens:',
            'info': 'Informações:'
        };
        
        const title = titles[type] || titles.error;
        const messageList = messages.map(msg => `• ${msg}`).join('\n');
        const summaryMessage = `${title}\n\n${messageList}`;
        
        const duration = type === 'error' ? TOAST_CONFIG.durations.summaryError : TOAST_CONFIG.durations.summaryOther;
        
        log('SUMMARY', `Creating summary toast with ${messages.length} messages`, { type, duration });
        
        return add(summaryMessage, type, duration);
    }

    // Configuration and debugging methods
    function getConfig() {
        return { ...TOAST_CONFIG };
    }

    function getPerformanceMetrics() {
        return { ...performanceMetrics };
    }

    function setDebugMode(enabled) {
        debugMode = enabled;
        log('CONFIG', `Debug mode ${enabled ? 'enabled' : 'disabled'}`);
    }

    function getState() {
        return {
            itemCount: items.length,
            items: items.map(t => ({
                id: t.id,
                type: t.type,
                message: t.message.substring(0, 50) + (t.message.length > 50 ? '...' : ''),
                show: t.show,
                removing: t.removing,
                createdAt: t.createdAt
            })),
            containerExists: !!container,
            performanceMetrics: getPerformanceMetrics()
        };
    }

    // Initialization
    function init() {
        log('INIT', 'Initializing Toast System');
        
        // Check for conflicts
        if (!checkForConflicts()) {
            log('ERROR', 'Toast system initialization aborted due to conflicts');
            return false;
        }
        
        // Create container
        container = createContainer();
        log('INIT', 'Container created:', !!container);
        log('INIT', 'Container in DOM?', document.body.contains(container));
        
        if (!container) {
            log('ERROR', 'Failed to create toast container');
            return false;
        }
        
        // Process Django messages
        processDjangoMessages();
        
        // Set up periodic memory tracking
        if (TOAST_CONFIG.debug.performanceMetrics) {
            setInterval(trackMemoryUsage, 30000); // Every 30 seconds
        }
        
        log('INIT', 'Toast System initialized successfully');
        return true;
    }

    // Auto-initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        // DOM already ready
        setTimeout(init, 0);
    }

    // Public API
    return {
        add,
        remove,
        clear,
        success,
        error,
        warning,
        info,
        pdfGenerationError,
        networkError,
        addSummaryToast,
        getConfig,
        getPerformanceMetrics,
        setDebugMode,
        getState,
        init
    };
})();

// Optional: Expose for debugging in console
if (TOAST_CONFIG.debug.enabled) {
    window.ToastDebug = {
        getState: () => window.Toast.getState(),
        getMetrics: () => window.Toast.getPerformanceMetrics(),
        clearAll: () => window.Toast.clear(),
        toggleDebug: (enabled) => window.Toast.setDebugMode(enabled)
    };
}