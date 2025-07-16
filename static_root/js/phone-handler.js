/**
 * Phone Handler for Brazilian phone numbers using Alpine.js
 * Handles both landlines (8-9 digits) and mobile phones (9 digits)
 */
function phoneHandler() {
    return {
        init() {
            // Add event listener to phone fields
            const phoneFields = document.querySelectorAll('input[type="tel"], #telefone, .phone-field');
            phoneFields.forEach(field => {
                field.addEventListener('input', (e) => {
                    this.formatPhone(e.target);
                });
            });
        },
        
        formatPhone(field) {
            let value = field.value.replace(/\D/g, '');
            
            // Limit to 11 digits (2 area code + 9 phone digits)
            if (value.length > 11) {
                value = value.substring(0, 11);
            }
            
            // Apply formatting based on length
            if (value.length <= 2) {
                // Just area code
                value = value.replace(/^(\d{0,2})/, '($1');
            } else if (value.length <= 6) {
                // Area code + first part
                value = value.replace(/^(\d{2})(\d{0,4})/, '($1) $2');
            } else if (value.length <= 10) {
                // 8-digit landline: (11) 1234-5678
                value = value.replace(/^(\d{2})(\d{4})(\d{0,4})/, '($1) $2-$3');
            } else {
                // 9-digit mobile/landline: (11) 12345-6789
                value = value.replace(/^(\d{2})(\d{5})(\d{0,4})/, '($1) $2-$3');
            }
            
            field.value = value;
        },
        
        // Utility method to clean phone number (remove formatting)
        cleanPhone(phone) {
            return phone.replace(/\D/g, '');
        },
        
        // Utility method to validate Brazilian phone number
        validatePhone(phone) {
            const cleaned = this.cleanPhone(phone);
            // Brazilian phones: area code (2 digits) + phone number (8 or 9 digits)
            return cleaned.length >= 10 && cleaned.length <= 11;
        }
    }
}