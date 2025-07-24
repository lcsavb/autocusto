/**
 * Form Handler Module - Class-based Reusable Form Management
 * Replaces Alpine.js form handling with vanilla JS classes
 * Features: Loading states, error handling, PDF modal integration, extensive debugging
 */

// Centralized Form Configuration
const FORM_CONFIG = {
    debug: {
        enabled: false,
        performanceMetrics: false,
        stateTracking: false,
        eventTracking: false
    },
    defaults: {
        loadingText: 'Enviando...',
        submitSelector: 'button[type="submit"]',
        loadingClass: 'btn-loading',
        disabledClass: 'btn-disabled',
        progressBarClass: 'progress-bar-fill'
    },
    delays: {
        buttonReEnable: 500,
        buttonReEnableError: 1500,
        successDelay: 1000
    },
    selectors: {
        submitText: '.submit-text',
        loadingText: '.loading-text',
        progressBar: '.progress-bar-fill'
    }
};

// Form Handler Module
window.FormHandler = (function() {
    'use strict';
    
    // Private utilities
    function log(level, message, data = null, formId = 'unknown') {
        // Debug logging disabled
        return;
    }

    function measurePerformance(operation, fn, formId) {
        if (!FORM_CONFIG.debug.performanceMetrics) return fn();
        
        const startTime = performance.now();
        const result = fn();
        const endTime = performance.now();
        const duration = endTime - startTime;
        
        log('PERF', `${operation} took ${duration.toFixed(2)}ms`, null, formId);
        return result;
    }

    function validateElement(element, type, formId) {
        if (!element) {
            log('ERROR', `Required ${type} element not found`, null, formId);
            return false;
        }
        return true;
    }

    // Base FormHandler Class
    class BaseFormHandler {
        constructor(formSelector) {
            this.formSelector = formSelector;
            this.form = null;
            this.submitBtn = null;
            this.formId = 'unknown';
            
            // State management
            this.isLoading = false;
            this.hasError = false;
            this.isInitialized = false;
            
            // Configuration
            this.config = {
                loadingText: FORM_CONFIG.defaults.loadingText,
                successCallback: null,
                errorCallback: null,
                beforeSubmitCallback: null,
                afterSubmitCallback: null,
                successRedirect: null,
                customHeaders: {},
                validateBeforeSubmit: true,
                debugMode: FORM_CONFIG.debug.enabled
            };
            
            // UI elements
            this.elements = {
                submitText: null,
                loadingText: null,
                progressBar: null
            };
            
            // Performance tracking
            this.metrics = {
                submitCount: 0,
                successCount: 0,
                errorCount: 0,
                averageSubmitTime: 0,
                lastSubmitTime: null
            };
            
            log('INIT', 'FormHandler instance created', { formSelector }, this.formId);
        }

        // Fluent API Configuration Methods
        withLoadingText(text) {
            this.config.loadingText = text;
            log('CONFIG', `Loading text set: "${text}"`, null, this.formId);
            return this;
        }

        withSuccessCallback(callback) {
            if (typeof callback !== 'function') {
                log('ERROR', 'Success callback must be a function', null, this.formId);
                return this;
            }
            this.config.successCallback = callback;
            log('CONFIG', 'Success callback registered', null, this.formId);
            return this;
        }

        withErrorCallback(callback) {
            if (typeof callback !== 'function') {
                log('ERROR', 'Error callback must be a function', null, this.formId);
                return this;
            }
            this.config.errorCallback = callback;
            log('CONFIG', 'Error callback registered', null, this.formId);
            return this;
        }

        withSuccessRedirect(url) {
            this.config.successRedirect = url;
            log('CONFIG', `Success redirect set: "${url}"`, null, this.formId);
            return this;
        }

        withBeforeSubmit(callback) {
            if (typeof callback !== 'function') {
                log('ERROR', 'Before submit callback must be a function', null, this.formId);
                return this;
            }
            this.config.beforeSubmitCallback = callback;
            log('CONFIG', 'Before submit callback registered', null, this.formId);
            return this;
        }

        withAfterSubmit(callback) {
            if (typeof callback !== 'function') {
                log('ERROR', 'After submit callback must be a function', null, this.formId);
                return this;
            }
            this.config.afterSubmitCallback = callback;
            log('CONFIG', 'After submit callback registered', null, this.formId);
            return this;
        }

        withCustomHeaders(headers) {
            this.config.customHeaders = { ...this.config.customHeaders, ...headers };
            log('CONFIG', 'Custom headers set', headers, this.formId);
            return this;
        }

        withDebugMode(enabled) {
            this.config.debugMode = enabled;
            log('CONFIG', `Debug mode ${enabled ? 'enabled' : 'disabled'}`, null, this.formId);
            return this;
        }

        withProgressDuration(duration) {
            this.config.estimatedDuration = duration;
            log('CONFIG', `Progress animation duration set: ${duration}ms`, null, this.formId);
            return this;
        }

        // Initialization
        init() {
            return measurePerformance('INIT', () => {
                log('INIT', 'Initializing FormHandler', { config: this.config }, this.formId);
                
                // Find form element
                this.form = document.querySelector(this.formSelector);
                if (!validateElement(this.form, 'form', this.formId)) {
                    return false;
                }
                
                // Set formId from form ID or generate one
                this.formId = this.form.id || `form-${Date.now()}`;
                if (!this.form.id) {
                    this.form.id = this.formId;
                }
                
                // Find submit button
                this.submitBtn = this.form.querySelector(FORM_CONFIG.defaults.submitSelector);
                if (!validateElement(this.submitBtn, 'submit button', this.formId)) {
                    return false;
                }
                
                // Find UI elements
                this.findUIElements();
                
                // Set up form submission handler
                this.setupFormHandler();
                
                // Mark as initialized
                this.isInitialized = true;
                
                log('INIT', 'FormHandler initialized successfully', {
                    formId: this.formId,
                    hasSubmitBtn: !!this.submitBtn,
                    hasUIElements: this.hasUIElements()
                }, this.formId);
                
                return true;
            }, this.formId);
        }

        findUIElements() {
            log('UI', 'Finding UI elements', null, this.formId);
            
            this.elements.submitText = this.submitBtn.querySelector(FORM_CONFIG.selectors.submitText);
            this.elements.loadingText = this.submitBtn.querySelector(FORM_CONFIG.selectors.loadingText);
            this.elements.progressBar = this.submitBtn.querySelector(FORM_CONFIG.selectors.progressBar);
            
            // Create loading text if it doesn't exist
            if (!this.elements.loadingText) {
                this.createLoadingText();
            }
            
            // Create progress bar if it doesn't exist
            if (!this.elements.progressBar) {
                this.createProgressBar();
            }
            
            log('UI', 'UI elements found/created', {
                hasSubmitText: !!this.elements.submitText,
                hasLoadingText: !!this.elements.loadingText,
                hasProgressBar: !!this.elements.progressBar
            }, this.formId);
        }

        createLoadingText() {
            log('UI', 'Creating loading text element', null, this.formId);
            
            const loadingSpan = document.createElement('span');
            loadingSpan.className = 'loading-text';
            loadingSpan.style.display = 'none';
            loadingSpan.textContent = this.config.loadingText;
            
            // Insert after submit text or at the end
            if (this.elements.submitText) {
                this.elements.submitText.parentNode.insertBefore(loadingSpan, this.elements.submitText.nextSibling);
            } else {
                this.submitBtn.appendChild(loadingSpan);
            }
            
            this.elements.loadingText = loadingSpan;
        }

        createProgressBar() {
            log('UI', 'Creating progress bar element', null, this.formId);
            
            const progressDiv = document.createElement('div');
            progressDiv.className = 'progress-bar-fill position-absolute';
            progressDiv.style.cssText = 'display: none; top: 0; left: 0; height: 100%; background: linear-gradient(90deg, rgba(255,255,255,0.1), rgba(255,255,255,0.3)); width: 0%; animation: fillProgress 3s ease-out forwards;';
            
            this.submitBtn.appendChild(progressDiv);
            this.elements.progressBar = progressDiv;
        }

        hasUIElements() {
            return !!(this.elements.submitText || this.elements.loadingText);
        }

        setupFormHandler() {
            log('HANDLER', 'Setting up form submission handler', null, this.formId);
            
            this.form.addEventListener('submit', (e) => this.handleSubmit(e));
            
            // Add form-specific debugging attributes
            this.form.setAttribute('data-form-handler', 'true');
            this.form.setAttribute('data-form-id', this.formId);
        }

        async handleSubmit(event) {
            event.preventDefault();
            
            // Check if medication validation failed (from med.js)
            if (this.form.getAttribute('data-medication-validation-failed') === 'true') {
                log('VALIDATION', 'Medication validation failed - aborting form submission', null, this.formId);
                return; // Exit early - don't process the form
            }
            
            const submitStartTime = performance.now();
            this.metrics.submitCount++;
            
            log('SUBMIT', 'Form submission started', {
                submitCount: this.metrics.submitCount,
                formData: this.getFormDataSummary()
            }, this.formId);
            
            // Prevent double submission
            if (this.isLoading) {
                log('WARN', 'Form submission blocked - already loading', null, this.formId);
                return;
            }
            
            // Before submit callback
            if (this.config.beforeSubmitCallback) {
                log('CALLBACK', 'Executing before submit callback', null, this.formId);
                try {
                    const proceed = await this.config.beforeSubmitCallback(this.form, this);
                    if (proceed === false) {
                        log('CALLBACK', 'Before submit callback prevented submission', null, this.formId);
                        return;
                    }
                } catch (error) {
                    log('ERROR', 'Before submit callback failed', error, this.formId);
                    return;
                }
            }
            
            // Clear any previous validation errors
            this.clearFieldValidationErrors();
            
            // Set loading state
            this.setLoadingState(true);
            
            try {
                // Perform the actual submission
                const result = await this.performSubmission();
                
                if (result.success) {
                    this.metrics.successCount++;
                    log('SUCCESS', 'Form submission succeeded', result.data, this.formId);
                    await this.handleSuccess(result.data);
                } else {
                    this.metrics.errorCount++;
                    log('ERROR', 'Form submission failed', result.error, this.formId);
                    await this.handleError(result.error);
                }
                
            } catch (error) {
                this.metrics.errorCount++;
                log('ERROR', 'Form submission threw exception', error, this.formId);
                await this.handleError(error);
            } finally {
                // Calculate and store submission time
                const submitEndTime = performance.now();
                const submitDuration = submitEndTime - submitStartTime;
                this.metrics.lastSubmitTime = submitDuration;
                this.metrics.averageSubmitTime = 
                    (this.metrics.averageSubmitTime * (this.metrics.submitCount - 1) + submitDuration) / this.metrics.submitCount;
                
                log('PERF', `Form submission completed in ${submitDuration.toFixed(2)}ms`, {
                    averageTime: this.metrics.averageSubmitTime.toFixed(2),
                    totalSubmissions: this.metrics.submitCount
                }, this.formId);
                
                // After submit callback
                if (this.config.afterSubmitCallback) {
                    log('CALLBACK', 'Executing after submit callback', null, this.formId);
                    try {
                        await this.config.afterSubmitCallback(this.form, this);
                    } catch (error) {
                        log('ERROR', 'After submit callback failed', error, this.formId);
                    }
                }
                
                // Reset loading state
                this.resetLoadingState();
            }
        }

        async performSubmission() {
            log('SUBMIT', 'Performing HTTP submission', null, this.formId);
            
            const formData = new FormData(this.form);
            const headers = {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || '',
                'Accept': 'application/json',
                ...this.config.customHeaders
            };
            
            try {
                const response = await fetch(this.form.action || window.location.pathname, {
                    method: 'POST',
                    headers: headers,
                    body: formData
                });
                
                const data = await response.json();
                
                if (data.success) {
                    return { success: true, data: data };
                } else {
                    return { success: false, error: data };
                }
                
            } catch (error) {
                return { success: false, error: error };
            }
        }

        async handleSuccess(data) {
            log('SUCCESS', 'Handling successful submission', data, this.formId);
            
            // Complete the button progress animation
            this.completeButtonProgress();
            
            // Custom success callback
            if (this.config.successCallback) {
                log('CALLBACK', 'Executing success callback', null, this.formId);
                try {
                    await this.config.successCallback(data, this);
                } catch (error) {
                    log('ERROR', 'Success callback failed', error, this.formId);
                }
            }
            
            // Success redirect
            if (this.config.successRedirect) {
                log('REDIRECT', `Redirecting to: ${this.config.successRedirect}`, null, this.formId);
                setTimeout(() => {
                    window.location.href = this.config.successRedirect;
                }, FORM_CONFIG.delays.successDelay);
            }
        }

        async handleError(error) {
            log('ERROR', 'Handling form submission error', error, this.formId);
            this.hasError = true;
            
            // Reset the button progress on error
            this.resetButtonProgress();
            
            // Custom error callback
            if (this.config.errorCallback) {
                log('CALLBACK', 'Executing error callback', null, this.formId);
                try {
                    await this.config.errorCallback(error, this);
                    return; // Custom callback handled the error
                } catch (callbackError) {
                    log('ERROR', 'Error callback failed', callbackError, this.formId);
                }
            }
            
            // Default error handling
            if (error.form_errors) {
                const errorMessages = [];
                
                // Apply field-specific validation styling (like crispy forms)
                Object.entries(error.form_errors).forEach(([fieldName, fieldErrors]) => {
                    fieldErrors.forEach(err => errorMessages.push(err));
                    this.addFieldValidationError(fieldName, fieldErrors);
                });
                
                if (window.Toast) {
                    Toast.addSummaryToast(errorMessages, 'error');
                } else {
                    console.error('Toast system not available', errorMessages);
                }
            } else if (error.error) {
                if (window.Toast) {
                    Toast.error(error.error);
                } else {
                    console.error('Form error:', error.error);
                }
            } else if (error.message) {
                if (window.Toast) {
                    Toast.networkError('Erro de conexão: ' + error.message);
                } else {
                    console.error('Network error:', error.message);
                }
            } else {
                if (window.Toast) {
                    Toast.error('Erro desconhecido');
                } else {
                    console.error('Unknown error:', error);
                }
            }
        }

        setLoadingState(loading) {
            measurePerformance('SET_LOADING_STATE', () => {
                log('STATE', `Setting loading state: ${loading}`, null, this.formId);
                
                this.isLoading = loading;
                this.submitBtn.disabled = loading;
                
                if (this.elements.submitText) {
                    this.elements.submitText.style.display = loading ? 'none' : 'inline';
                }
                
                if (this.elements.loadingText) {
                    this.elements.loadingText.style.display = loading ? 'inline' : 'none';
                    this.elements.loadingText.textContent = this.config.loadingText;
                }
                
                // Enhanced button-as-progress-bar
                if (loading) {
                    this.submitBtn.classList.add(FORM_CONFIG.defaults.loadingClass);
                    this.initializeButtonProgress();
                } else {
                    this.submitBtn.classList.remove(FORM_CONFIG.defaults.loadingClass);
                    this.resetButtonProgress();
                }
                
                // Hide old progress bar (we're using the button itself now)
                if (this.elements.progressBar) {
                    this.elements.progressBar.style.display = 'none';
                }
                
                log('STATE', `Loading state applied`, {
                    isLoading: this.isLoading,
                    buttonDisabled: this.submitBtn.disabled
                }, this.formId);
            }, this.formId);
        }

        initializeButtonProgress() {
            log('PROGRESS', 'Initializing button-as-progress-bar', null, this.formId);
            
            // Set CSS custom properties for the button
            this.submitBtn.style.setProperty('--progress', '0%');
            this.submitBtn.style.position = 'relative';
            this.submitBtn.style.overflow = 'hidden';
            
            // Add progress background styles
            const originalBackground = getComputedStyle(this.submitBtn).background;
            this.submitBtn.setAttribute('data-original-background', originalBackground);
            
            // Apply button-as-progress styling
            this.submitBtn.style.background = `
                linear-gradient(90deg, 
                    rgba(40, 167, 69, 0.8) var(--progress, 0%), 
                    transparent var(--progress, 0%)
                ),
                ${originalBackground}
            `;
            this.submitBtn.style.transition = 'all 0.3s ease';
            
            // Start progress animation
            this.startProgressAnimation();
        }

        startProgressAnimation() {
            let progress = 0;
            const duration = this.config.estimatedDuration || 3000; // 3 seconds default
            const interval = 50; // Update every 50ms
            const increment = (100 / (duration / interval));
            
            log('PROGRESS', `Starting progress animation (${duration}ms)`, null, this.formId);
            
            this.progressInterval = setInterval(() => {
                progress = Math.min(progress + increment, 85); // Cap at 85% until actual completion
                this.updateButtonProgress(progress);
                
                if (progress >= 85) {
                    clearInterval(this.progressInterval);
                    log('PROGRESS', 'Progress animation reached 85% - waiting for completion', null, this.formId);
                }
            }, interval);
        }

        updateButtonProgress(percentage) {
            if (this.submitBtn) {
                this.submitBtn.style.setProperty('--progress', `${percentage}%`);
                log('PROGRESS', `Button progress updated: ${percentage.toFixed(1)}%`, null, this.formId);
            }
        }

        completeButtonProgress() {
            log('PROGRESS', 'Completing button progress to 100%', null, this.formId);
            
            if (this.progressInterval) {
                clearInterval(this.progressInterval);
            }
            
            // Animate to 100%
            this.updateButtonProgress(100);
            
            // Hold at 100% briefly before reset
            setTimeout(() => {
                this.resetButtonProgress();
            }, 500);
        }

        resetButtonProgress() {
            log('PROGRESS', 'Resetting button progress', null, this.formId);
            
            if (this.progressInterval) {
                clearInterval(this.progressInterval);
                this.progressInterval = null;
            }
            
            if (this.submitBtn) {
                // Restore original styling
                const originalBackground = this.submitBtn.getAttribute('data-original-background');
                if (originalBackground) {
                    this.submitBtn.style.background = originalBackground;
                    this.submitBtn.removeAttribute('data-original-background');
                }
                
                this.submitBtn.style.removeProperty('--progress');
                this.submitBtn.style.position = '';
                this.submitBtn.style.overflow = '';
                this.submitBtn.style.transition = '';
            }
        }

        resetLoadingState() {
            const delay = this.hasError ? 
                FORM_CONFIG.delays.buttonReEnableError : 
                FORM_CONFIG.delays.buttonReEnable;
            
            log('STATE', `Resetting loading state with ${delay}ms delay`, null, this.formId);
            
            setTimeout(() => {
                this.setLoadingState(false);
                this.hasError = false;
                log('STATE', 'Loading state reset completed', null, this.formId);
            }, delay);
        }

        addFieldValidationError(fieldName, fieldErrors) {
            // Find the field (try multiple patterns like crispy forms)
            const field = this.form.querySelector(`#id_${fieldName}`) || 
                         this.form.querySelector(`[name="${fieldName}"]`);
            
            if (field) {
                // Apply the same styling that crispy forms would apply
                field.classList.add('is-invalid');
                
                // Find or create invalid-feedback div (like crispy forms does)
                let feedbackDiv = field.parentNode.querySelector('.invalid-feedback');
                if (!feedbackDiv) {
                    feedbackDiv = document.createElement('div');
                    feedbackDiv.className = 'invalid-feedback';
                    field.parentNode.appendChild(feedbackDiv);
                }
                
                feedbackDiv.textContent = fieldErrors.join(', ');
                feedbackDiv.style.display = 'block';
            }
        }

        clearFieldValidationErrors() {
            // Clear validation styling (reverse what crispy forms would do)
            this.form.querySelectorAll('.is-invalid').forEach(field => {
                field.classList.remove('is-invalid');
            });
            
            this.form.querySelectorAll('.invalid-feedback').forEach(div => {
                div.style.display = 'none';
            });
        }

        getFormDataSummary() {
            const formData = new FormData(this.form);
            const summary = {};
            let fieldCount = 0;
            
            for (let [key, value] of formData.entries()) {
                if (fieldCount < 5) { // Limit to prevent log spam
                    summary[key] = typeof value === 'string' ? 
                        (value.length > 50 ? value.substring(0, 50) + '...' : value) : 
                        '[File]';
                }
                fieldCount++;
            }
            
            if (fieldCount > 5) {
                summary['...'] = `and ${fieldCount - 5} more fields`;
            }
            
            return summary;
        }

        // Public methods for external access
        getMetrics() {
            return { ...this.metrics };
        }

        getState() {
            return {
                formId: this.formId,
                isLoading: this.isLoading,
                hasError: this.hasError,
                isInitialized: this.isInitialized,
                config: { ...this.config },
                metrics: this.getMetrics()
            };
        }

        destroy() {
            log('DESTROY', 'Destroying FormHandler instance', null, this.formId);
            
            if (this.form) {
                this.form.removeEventListener('submit', this.handleSubmit);
                this.form.removeAttribute('data-form-handler');
                this.form.removeAttribute('data-form-id');
            }
            
            this.isInitialized = false;
        }
    }

    // Specialized PDF Form Handler
    class PdfFormHandler extends BaseFormHandler {
        constructor(formSelector) {
            super(formSelector);
            
            // PDF-specific configuration
            this.config.pdfModal = false;
            this.config.pdfSuccessRedirect = '/';
            
            log('INIT', 'PdfFormHandler instance created', { formSelector }, this.formId);
        }

        withPdfModal(enabled = true) {
            this.config.pdfModal = enabled;
            log('CONFIG', `PDF modal ${enabled ? 'enabled' : 'disabled'}`, null, this.formId);
            return this;
        }

        async handleSuccess(data) {
            log('SUCCESS', 'Handling PDF form success', data, this.formId);
            log('SUCCESS', 'PDF modal config enabled?', this.config.pdfModal, this.formId);
            log('SUCCESS', 'PDF URL in response?', !!data.pdf_url, this.formId);
            
            if (data.pdf_url) {
                if (this.config.pdfModal) {
                    log('PDF', 'Opening PDF in modal', { url: data.pdf_url }, this.formId);
                    log('PDF', 'Checking for Alpine.js availability...', null, this.formId);
                    
                    // Find PDF modal element first
                    const pdfModalElement = document.querySelector('[x-data*="pdfModal"]');
                    log('PDF', 'PDF modal element found?', !!pdfModalElement, this.formId);
                    
                    // Check if Alpine.js is available
                    if (window.Alpine) {
                        log('PDF', 'Alpine.js found - checking for PDF modal element', null, this.formId);
                        
                        if (pdfModalElement) {
                            log('PDF', 'Dispatching Alpine.js event to PDF modal element', null, this.formId);
                            
                            // Try Alpine.js dispatch method
                            pdfModalElement.dispatchEvent(new CustomEvent('open-pdf', {
                                detail: {
                                    url: data.pdf_url,
                                    title: 'PDF Gerado',
                                    allowDownload: true,
                                    allowEdit: true
                                }
                            }));
                            
                            // Try to access Alpine.js component directly as another fallback
                            if (pdfModalElement._x_dataStack) {
                                log('PDF', 'Trying direct Alpine.js component access', null, this.formId);
                                try {
                                    const alpineComponent = pdfModalElement._x_dataStack[0];
                                    if (alpineComponent && alpineComponent.openPdf) {
                                        log('PDF', 'Calling openPdf directly on Alpine.js component', null, this.formId);
                                        alpineComponent.openPdf(data.pdf_url, 'PDF Gerado', true, true);
                                        
                                        // Show success toast when modal opens (like renovacao_rapida.html)
                                        if (window.Toast) {
                                            Toast.success(data.message || 'PDF gerado com sucesso!');
                                            log('PDF', 'Success toast shown for PDF generation', null, this.formId);
                                        }
                                    } else {
                                        log('WARN', 'Alpine.js component found but no openPdf method', alpineComponent, this.formId);
                                    }
                                } catch (error) {
                                    log('ERROR', 'Failed to access Alpine.js component directly', error, this.formId);
                                }
                            }
                        }
                    } else {
                        log('WARN', 'Alpine.js not found - trying global event dispatch', null, this.formId);
                    }
                    
                    // Also dispatch global event as fallback
                    log('PDF', 'Dispatching global PDF event', null, this.formId);
                    const pdfEvent = new CustomEvent('open-pdf', {
                        detail: {
                            url: data.pdf_url,
                            title: 'PDF Gerado',
                            allowDownload: true,
                            allowEdit: true
                        }
                    });
                    document.dispatchEvent(pdfEvent);
                    
                    // Listen for modal close to redirect
                    document.addEventListener('modal-closed', () => {
                        log('PDF', 'PDF modal closed - redirecting', null, this.formId);
                        if (this.config.successRedirect) {
                            window.location.href = this.config.successRedirect;
                        }
                    }, { once: true });
                    
                    // IMPORTANT: Don't call parent success handler which triggers immediate redirect
                    log('PDF', 'Skipping parent success handler to prevent immediate redirect', null, this.formId);
                    return; // Exit early to prevent parent.handleSuccess() call
                } else {
                    // Direct download or redirect
                    log('PDF', 'PDF generated - redirecting or downloading', null, this.formId);
                    window.open(data.pdf_url, '_blank');
                }
            } else {
                log('ERROR', 'PDF URL not provided in success response', data, this.formId);
                if (window.Toast) {
                    Toast.pdfGenerationError('PDF não foi gerado. Tente novamente.');
                }
            }
            
            // Call parent success handler
            await super.handleSuccess(data);
        }
    }

    // Export classes
    return {
        BaseFormHandler,
        PdfFormHandler,
        getConfig: () => ({ ...FORM_CONFIG })
    };
})();

// Global aliases for convenience - fix the reference issue
window.BaseFormHandler = window.FormHandler.BaseFormHandler;
window.PdfFormHandler = window.FormHandler.PdfFormHandler;

// Optional: Expose debugging tools
if (FORM_CONFIG.debug.enabled) {
    window.FormHandlerDebug = {
        getConfig: () => window.FormHandler.getConfig(),
        getAllForms: () => {
            const forms = document.querySelectorAll('[data-form-handler="true"]');
            return Array.from(forms).map(form => ({
                id: form.id,
                formId: form.getAttribute('data-form-id'),
                action: form.action || 'current-page',
                method: form.method || 'GET'
            }));
        }
    };
}