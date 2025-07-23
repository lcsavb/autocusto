/**
 * Med.js Logic Extractor for Testing
 * 
 * This file extracts the core logic from med.js for unit testing
 * without requiring DOM or jQuery in the browser environment.
 */

// Mock the global environment that med.js expects
const mockGlobal = {
    $: require('./mocks/jquery-mock'),
    jQuery: null,
    console: {
        log: jest.fn(),
        error: jest.fn(),
        warn: jest.fn()
    },
    Toast: {
        error: jest.fn(),
        warning: jest.fn(),
        success: jest.fn()
    }
};

mockGlobal.jQuery = mockGlobal.$;

/**
 * Extract the core medication validation logic from med.js
 * This is the critical business logic that prevents invalid prescriptions
 */
class MedicationValidator {
    constructor($) {
        this.$ = $ || mockGlobal.$;
    }

    /**
     * Check if there are any valid medications selected
     * This is extracted from the form submission handler in med.js
     */
    hasValidMedication() {
        let hasValidMedication = false;
        
        // Check all medications 1-4 (this logic is from med.js)
        for (let i = 1; i <= 4; i++) {
            const medSelect = this.$(`#id_id_med${i}`);
            const medValue = medSelect.val();
            
            if (medValue && medValue !== 'nenhum' && medValue !== '' && medValue !== 'none') {
                hasValidMedication = true;
                console.log(`Medication ${i} has valid value: ${medValue}`);
            }
        }
        
        return hasValidMedication;
    }

    /**
     * Validate form submission - returns true if should prevent submission
     * This logic is extracted from the med.js form submission handler
     */
    shouldPreventSubmission(formElement) {
        const hasValid = this.hasValidMedication();
        
        if (!hasValid) {
            console.log('VALIDATION FAILED: No valid medications selected - preventing form submission');
            
            // Set validation flag (from med.js)
            this.$(formElement).attr('data-medication-validation-failed', 'true');
            
            // Show error message (from med.js)
            if (mockGlobal.Toast) {
                mockGlobal.Toast.error('Pelo menos um medicamento deve ser selecionado.');
            }
            
            return true; // Prevent submission
        } else {
            // Clear validation flag (from med.js)
            this.$(formElement).removeAttr('data-medication-validation-failed');
            return false; // Allow submission
        }
    }

    /**
     * Check if a field should keep its name attribute
     * This logic is from the med.js form submission handler
     */
    shouldKeepFieldName(fieldName, medNumber) {
        // Skip the via field - it should never have its name removed
        if (fieldName.includes('_via')) {
            console.log(`Form submit: Skipping via field: ${fieldName}`);
            return true;
        }
        
        // Keep the medication dropdown field itself so backend knows it was set to "nenhum"
        if (fieldName === `id_med${medNumber}`) {
            console.log(`Form submit: Keeping medication dropdown field: ${fieldName}`);
            return true;
        }
        
        return false; // Remove name from this field
    }

    /**
     * Process field name removal for a medication set to "nenhum"
     * This logic is from the med.js form submission handler
     */
    processFieldsForNenhum(medNumber, formElement) {
        const fieldsProcessed = [];
        
        // Simulate finding fields for this medication
        const potentialFields = [
            `med${medNumber}_repetir_posologia`,
            `med${medNumber}_posologia_mes1`,
            `qtd_med${medNumber}_mes1`,
            `med${medNumber}_posologia_mes2`,
            `qtd_med${medNumber}_mes2`,
            `med${medNumber}_posologia_mes3`,
            `qtd_med${medNumber}_mes3`,
            `med${medNumber}_posologia_mes4`,
            `qtd_med${medNumber}_mes4`,
            `med${medNumber}_posologia_mes5`,
            `qtd_med${medNumber}_mes5`,
            `med${medNumber}_posologia_mes6`,
            `qtd_med${medNumber}_mes6`,
            `med${medNumber}_via`,
            `id_med${medNumber}`
        ];
        
        potentialFields.forEach(fieldName => {
            if (this.shouldKeepFieldName(fieldName, medNumber)) {
                fieldsProcessed.push({ field: fieldName, action: 'kept' });
            } else {
                fieldsProcessed.push({ field: fieldName, action: 'removed' });
                console.log(`Form submit: Removed name attribute from ${fieldName}`);
            }
        });
        
        return fieldsProcessed;
    }

    /**
     * Check if a medication value should be considered "empty" or invalid
     * This logic handles the various forms of "nenhum" in med.js
     */
    isMedicationEmpty(medValue) {
        if (!medValue || medValue === '' || medValue === 'none') {
            return true;
        }
        
        if (medValue === 'nenhum') {
            return true;
        }
        
        return false;
    }

    /**
     * Get all medication values (for testing)
     */
    getAllMedicationValues() {
        const values = {};
        for (let i = 1; i <= 4; i++) {
            const medSelect = this.$(`#id_id_med${i}`);
            values[`med${i}`] = medSelect.val();
        }
        return values;
    }
}

module.exports = MedicationValidator;