# Form Button with Loading Animation Guide

Simple guide for creating forms with submit buttons that have proper loading animations using PdfFormHandler.

## HTML Structure

```html
<form method="POST" novalidate class="your-form-class" id="your-form-id">
    {% csrf_token %}
    <input type="hidden" name="your_hidden_field" value="your_value">
    
    <!-- Your form fields -->
    <input type="text" name="field1" class="form-control">
    <select name="field2" class="form-control">
        <option value="1">Option 1</option>
    </select>
    <input type="checkbox" name="field3">
    
    <!-- Submit button with loading animation -->
    <button type="submit" class="btn btn-primary btn-submit-process">
        <span class="oi oi-check mr-2"></span>
        <span class="submit-text">Submit</span>
        <span class="loading-text" style="display: none;">Processing...</span>
        <div class="progress-bar-fill" style="display: none;"></div>
    </button>
</form>
```

## CSS for Button Animation

```css
/* Fix button height consistency during loading animation */
.btn-submit-process {
    min-height: 38px; /* Consistent height */
    position: relative;
    overflow: hidden;
}

.btn-submit-process .progress-bar-fill {
    position: absolute;
    top: 0;
    left: 0;
    height: 100%;
    width: 0%;
    background: linear-gradient(90deg, rgba(255,255,255,0.1), rgba(255,255,255,0.3));
    animation: fillProgress 3s ease-out forwards;
    z-index: 0;
}

.btn-submit-process span {
    position: relative;
    z-index: 1;
}
```

## JavaScript Initialization

```javascript
document.addEventListener('DOMContentLoaded', function() {
    new PdfFormHandler('#your-form-id')
        .withLoadingText('Processing...')
        .withPdfModal(true)
        .withProgressDuration(3000)
        .withCustomHeaders({
            'X-Requested-With': 'XMLHttpRequest'
        })
        .init();
});
```

## Key Points

1. **Button Structure**: Must have `.submit-text`, `.loading-text`, and `.progress-bar-fill` elements
2. **CSS Height**: Use `min-height` to prevent button height changes during loading
3. **Z-index**: Progress bar behind text, text elements in front
4. **Form Handler**: Initialize with proper configuration for your needs

That's it! Simple, isolated form with animated submit button.