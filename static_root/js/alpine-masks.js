// Alpine.js Input Masks Utilities
// Usage: Include this file before Alpine.js initialization

window.AlpineMasks = {
  // CPF Mask: 000.000.000-00
  cpf: {
    format(value) {
      // Remove non-digits
      const digits = value.replace(/\D/g, '');
      // Apply CPF mask: 000.000.000-00
      if (digits.length <= 11) {
        return digits.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4');
      }
      return digits.substring(0, 11).replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4');
    },
    
    maxLength: 14,
    placeholder: '000.000.000-00'
  },
  
  // CID Mask: A00.0
  cid: {
    format(value) {
      // Convert to uppercase and remove invalid chars
      let clean = value.toUpperCase().replace(/[^A-Z0-9]/g, '');
      
      if (clean.length === 0) return '';
      
      // Apply CID mask: Letter + up to 2 digits + optional decimal + 1 digit
      if (clean.length >= 1) {
        let result = clean.charAt(0); // First letter
        
        if (clean.length > 1) {
          const numbers = clean.substring(1);
          
          if (numbers.length <= 2) {
            result += numbers;
          } else if (numbers.length === 3) {
            result += numbers.substring(0, 2) + '.' + numbers.charAt(2);
          } else {
            result += numbers.substring(0, 2) + '.' + numbers.charAt(2);
          }
        }
        
        return result;
      }
      
      return clean;
    },
    
    maxLength: 5,
    placeholder: 'A00.0'
  },
  
  // Generic mask handler creator
  createHandler(maskType, onInput) {
    return function(event) {
      const mask = AlpineMasks[maskType];
      if (!mask) return;
      
      const masked = mask.format(event.target.value);
      event.target.value = masked;
      
      // Update Alpine model if provided
      if (this[event.target.getAttribute('x-model')]) {
        this[event.target.getAttribute('x-model')] = masked;
      }
      
      // Call additional input handler if provided
      if (onInput && typeof onInput === 'function') {
        onInput.call(this, event, masked);
      }
    };
  }
};