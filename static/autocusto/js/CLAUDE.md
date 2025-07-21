# AutoCusto JavaScript Module Documentation

This directory contains the client-side JavaScript modules for the AutoCusto Django application, focusing on form handling, PDF generation workflows, and user interface interactions.

## Architecture Overview

The JavaScript architecture follows a **modular approach** with three main patterns:

1. **Module Pattern** - Self-contained modules with private/public APIs (`form-handler.js`, `toast-system.js`)
2. **Alpine.js Components** - Reactive components for specific UI interactions (`pdf-modal.js`)
3. **jQuery Legacy** - Traditional jQuery for form masks and AJAX (`mascaras.js`, `buscaDoencas.js`)

## Core Modules

### Form Handling System

**Primary Files:**
- `form-handler.js` - Main form processing engine
- `adicionar-processo.js` - Process creation forms
- `processoEdit.js` - Process editing workflows

**Key Features:**
- **Class-based Architecture**: `BaseFormHandler` and specialized `PdfFormHandler`
- **Fluent API**: Chainable configuration methods
- **Loading States**: Button progress animations and UI feedback
- **Error Handling**: Field-level validation with Bootstrap styling
- **Performance Monitoring**: Extensive debugging and metrics collection

**Usage Pattern:**
```javascript
// Standard form handling
new BaseFormHandler('#my-form')
    .withLoadingText('Enviando...')
    .withSuccessCallback(handleSuccess)
    .withErrorCallback(handleError)
    .init();

// PDF-specific form handling
new PdfFormHandler('#pdf-form')
    .withPdfModal(true)
    .withSuccessRedirect('/success/')
    .init();
```

### Toast Notification System

**Primary File:** `toast-system.js`

**Key Features:**
- **Performance-optimized**: Memory tracking and performance metrics
- **Django Integration**: Automatic processing of Django messages
- **Specialized Methods**: PDF errors, network errors, summary toasts
- **Centralized Configuration**: Duration and delay settings

**Usage Pattern:**
```javascript
Toast.success('Operation completed successfully');
Toast.error('Validation failed');
Toast.addSummaryToast(['Error 1', 'Error 2'], 'error');
```

### PDF Modal System

**Primary File:** `pdf-modal.js`

**Architecture:** Alpine.js components for reactive PDF viewing

**Components:**
- `pdfModal` - PDF viewer with download/print functionality
- `renovacaoForm` - Process renewal form with date validation

**Key Features:**
- **Modal Management**: PDF viewing with fullscreen support
- **Date Validation**: Real-time Brazilian date format validation (DD/MM/AAAA)
- **Print Integration**: Browser print dialog integration
- **Edit Mode**: Conditional form submission for editing workflows

## Utility Modules

### Input Masking & Validation

**Files:**
- `mascaras.js` - jQuery Mask Plugin integration
- `alpine-masks.js` - Alpine.js-compatible masking
- `celular.js` - Phone number formatting
- `cep-handler.js` - Brazilian postal code handling

**Supported Formats:**
- **CPF**: `000.000.000-00`
- **Dates**: `00/00/0000`
- **Phone**: `(00) 0000.0000`
- **CEP**: `00000-000`
- **CID Codes**: `A00.0` (Medical classification)

### Search & AJAX

**Files:**
- `buscaDoencas.js` - Disease/condition search
- `buscaPacientes.js` - Patient search
- `med.js` - Medication search

**Pattern:**
- Real-time search with debouncing
- List-based result selection
- Form field population

## Medical Workflow Modules

### Process Management

**Files:**
- `processo.js` - Core process form logic
- `processoEdit.js` - Process editing workflows
- `documentosAdicionais.js` - Additional document handling
- `emitirExames.js` - Medical exam generation

**Key Features:**
- **Conditional Fields**: Dynamic form field visibility based on radio selections
- **Medical Logic**: Disease-specific field requirements
- **Document Generation**: PDF generation workflows

### Protocol Display

**File:** `mostrarProtocolo.js`

**Purpose:** Dynamic protocol content display based on selected medical conditions

## Configuration and Debugging

### Debug Configuration

Most modules include extensive debugging capabilities:

```javascript
// Form Handler debugging
window.FormHandlerDebug.getAllForms()
window.FormHandlerDebug.getConfig()

// Toast system debugging  
window.ToastDebug.getState()
window.ToastDebug.getMetrics()
```

### Performance Monitoring

The system includes built-in performance tracking:
- **Form submission times**
- **Toast lifecycle metrics** 
- **Memory usage tracking**
- **DOM mutation monitoring**

## Integration Patterns

### Django Integration

**CSRF Handling:**
```javascript
headers: {
    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || ''
}
```

**Django Messages Processing:**
```javascript
// Automatic processing of window.djangoMessages
processDjangoMessages()
```

### Bootstrap Integration

**Form Validation:**
- Uses Bootstrap `.is-invalid` classes
- Creates `.invalid-feedback` elements
- Maintains consistency with Django Crispy Forms

**Modal Integration:**
- Compatible with Bootstrap modal system
- Custom styling for PDF viewer

### Alpine.js Integration

**Component Registration:**
```javascript
document.addEventListener('alpine:init', () => {
    Alpine.data('componentName', () => ({
        // component definition
    }));
});
```

**Event System:**
```javascript
// Custom event dispatching
this.$dispatch('open-pdf', { url, title });

// Global event listening
document.addEventListener('open-pdf', handlePdfEvent);
```

## Development Guidelines

### Adding New Form Handlers

1. **Extend BaseFormHandler** for standard forms
2. **Extend PdfFormHandler** for PDF-generating forms
3. **Use fluent API** for configuration
4. **Add performance logging** for complex operations

### Error Handling Standards

1. **Field-level errors** - Apply Bootstrap validation classes
2. **Form-level errors** - Use Toast system for user feedback
3. **Network errors** - Implement retry logic and user guidance
4. **Debug logging** - Include context and performance data

### Performance Best Practices

1. **Lazy initialization** - Initialize modules only when needed
2. **Event delegation** - Use document-level event handlers
3. **Memory cleanup** - Remove event listeners and clear intervals
4. **Debounced searches** - Prevent excessive AJAX calls

### Testing Considerations

1. **DOM Dependencies** - Modules expect specific HTML structure
2. **CSRF Tokens** - Forms require valid Django CSRF tokens
3. **Alpine.js Timing** - Components must wait for Alpine initialization
4. **Bootstrap Classes** - Validation styling depends on Bootstrap CSS

## File Dependencies

### Required Libraries

- **jQuery** - Legacy modules (mascaras.js, buscaDoencas.js)
- **jQuery Mask Plugin** - Input masking
- **Alpine.js** - Reactive components (pdf-modal.js)
- **Bootstrap 4** - Styling and form validation classes

### Module Dependencies

```
form-handler.js → toast-system.js
pdf-modal.js → toast-system.js
processo.js → mascaras.js
buscaDoencas.js → jQuery
```

## Browser Compatibility

**Target Support:**
- Modern browsers with ES6 support
- Modules use `const`, `let`, arrow functions
- Alpine.js requires IE11+ or modern browsers
- Performance APIs require Chrome 60+, Firefox 58+

**Fallbacks:**
- Performance metrics gracefully degrade
- Console logging has null checks
- DOM APIs include existence checks

## Medical Domain Context

This JavaScript handles sensitive medical data processing including:

- **Patient Information** - CPF, medical records, personal data
- **Medical Conditions** - CID codes, disease classifications
- **Legal Documents** - PDF generation for official medical processes
- **Healthcare Workflows** - Doctor-patient-clinic relationships

**Security Considerations:**
- All AJAX requests include CSRF protection
- No sensitive data logged in production mode
- PDF URLs are temporary and session-based
- Form validation prevents malicious input

## Maintenance Notes

### Debugging Production Issues

1. **Enable debug mode**: Set `FORM_CONFIG.debug.enabled = true`
2. **Check performance metrics**: Use `window.FormHandlerDebug`
3. **Monitor toast state**: Use `window.ToastDebug.getState()`
4. **Verify DOM structure**: Check for required Bootstrap classes

### Common Issues

1. **Alpine.js not loading** - PDF modal functionality breaks
2. **Missing CSRF token** - Form submissions fail
3. **Bootstrap CSS missing** - Validation styling not applied
4. **jQuery version conflicts** - Mask plugin compatibility issues

### Future Refactoring Considerations

1. **jQuery Migration** - Legacy modules could move to vanilla JS
2. **Alpine.js Consolidation** - More components could benefit from reactivity  
3. **Module Bundling** - Consider webpack/rollup for production builds
4. **TypeScript Migration** - Add type safety for better maintainability