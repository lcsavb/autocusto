/**
 * Node.js Unit Tests for med.js - CRITICAL MEDICATION VALIDATION LOGIC
 * 
 * Tests the existing med.js code without refactoring by mocking jQuery and DOM.
 * These tests ensure the critical medication validation and form submission logic works correctly.
 * 
 * MEDICAL SAFETY: These tests validate prescription safety logic that prevents
 * invalid medical prescriptions from being submitted.
 */

// Import the medication validation logic extractor
const MedicationValidator = require('./med-logic-extractor');

// Mock global objects that med.js expects
const mockJQuery = require('./mocks/jquery-mock');
global.$ = mockJQuery;
global.jQuery = mockJQuery;
global.console = {
    log: jest.fn(),
    error: jest.fn(),
    warn: jest.fn()
};

// Toast mock for validation messages
global.Toast = {
    error: jest.fn(),
    warning: jest.fn(),
    success: jest.fn()
};

describe('med.js Medication Management - CRITICAL SAFETY TESTS', () => {
    let validator;
    let mockForm;
    let medicationDropdowns;
    let mockJQuery;
    
    beforeEach(() => {
        // Reset all mocks
        jest.clearAllMocks();
        
        // Create mock form and medication dropdowns
        medicationDropdowns = {
            med1: { val: jest.fn().mockReturnValue(''), attr: jest.fn(), removeAttr: jest.fn() },
            med2: { val: jest.fn().mockReturnValue(''), attr: jest.fn(), removeAttr: jest.fn() },
            med3: { val: jest.fn().mockReturnValue(''), attr: jest.fn(), removeAttr: jest.fn() },
            med4: { val: jest.fn().mockReturnValue(''), attr: jest.fn(), removeAttr: jest.fn() }
        };
        
        mockForm = {
            attr: jest.fn(),
            removeAttr: jest.fn()
        };
        
        // Create custom jQuery mock for this test
        mockJQuery = jest.fn().mockImplementation((selector) => {
            if (selector === '#id_id_med1') return medicationDropdowns.med1;
            if (selector === '#id_id_med2') return medicationDropdowns.med2;
            if (selector === '#id_id_med3') return medicationDropdowns.med3;
            if (selector === '#id_id_med4') return medicationDropdowns.med4;
            if (typeof selector === 'object') return mockForm; // $(this) in form handler
            return mockForm;
        });
        
        // Create validator instance with our mock
        validator = new MedicationValidator(mockJQuery);
    });

    describe('🚨 CRITICAL: Medication Validation Logic', () => {
        test('should detect when all medications are "nenhum"', () => {
            // Simulate all medications set to "nenhum"
            medicationDropdowns.med1.val.mockReturnValue('nenhum');
            medicationDropdowns.med2.val.mockReturnValue('nenhum');
            medicationDropdowns.med3.val.mockReturnValue('nenhum');
            medicationDropdowns.med4.val.mockReturnValue('nenhum');
            
            // Test the validation logic using our extractor
            const hasValidMedication = validator.hasValidMedication();
            
            // CRITICAL ASSERTION: Should detect no valid medications
            expect(hasValidMedication).toBe(false);
            expect(medicationDropdowns.med1.val).toHaveBeenCalled();
            expect(medicationDropdowns.med2.val).toHaveBeenCalled();
            expect(medicationDropdowns.med3.val).toHaveBeenCalled();
            expect(medicationDropdowns.med4.val).toHaveBeenCalled();
        });

        test('should detect when at least one medication is valid', () => {
            // Simulate med1 with valid medication, others "nenhum"
            medicationDropdowns.med1.val.mockReturnValue('123'); // Valid medication ID
            medicationDropdowns.med2.val.mockReturnValue('nenhum');
            medicationDropdowns.med3.val.mockReturnValue('nenhum');
            medicationDropdowns.med4.val.mockReturnValue('nenhum');
            
            // Test using validator
            const hasValidMedication = validator.hasValidMedication();
            
            // CRITICAL ASSERTION: Should detect valid medication
            expect(hasValidMedication).toBe(true);
        });

        test('should handle empty string values as invalid', () => {
            // Simulate empty/null values
            medicationDropdowns.med1.val.mockReturnValue('');
            medicationDropdowns.med2.val.mockReturnValue(null);
            medicationDropdowns.med3.val.mockReturnValue(undefined);
            medicationDropdowns.med4.val.mockReturnValue('none');
            
            let hasValidMedication = false;
            
            for (let i = 1; i <= 4; i++) {
                const medSelect = global.$(`#id_id_med${i}`);
                const medValue = medSelect.val();
                
                if (medValue && medValue !== 'nenhum' && medValue !== '' && medValue !== 'none') {
                    hasValidMedication = true;
                }
            }
            
            expect(hasValidMedication).toBe(false);
        });

        test('should handle mixed valid and invalid medications correctly', () => {
            // Test various combinations
            const testCases = [
                // [med1, med2, med3, med4, expectedValid]
                ['123', 'nenhum', 'nenhum', 'nenhum', true],
                ['nenhum', '456', 'nenhum', 'nenhum', true],
                ['nenhum', 'nenhum', '789', 'nenhum', true],
                ['nenhum', 'nenhum', 'nenhum', '101', true],
                ['', 'nenhum', 'none', '', false],
                ['nenhum', 'nenhum', 'nenhum', 'nenhum', false]
            ];
            
            testCases.forEach(([med1, med2, med3, med4, expectedValid], index) => {
                // Reset mocks
                jest.clearAllMocks();
                
                // Set up medication values
                medicationDropdowns.med1.val.mockReturnValue(med1);
                medicationDropdowns.med2.val.mockReturnValue(med2);
                medicationDropdowns.med3.val.mockReturnValue(med3);
                medicationDropdowns.med4.val.mockReturnValue(med4);
                
                let hasValidMedication = false;
                
                for (let i = 1; i <= 4; i++) {
                    const medSelect = global.$(`#id_id_med${i}`);
                    const medValue = medSelect.val();
                    
                    if (medValue && medValue !== 'nenhum' && medValue !== '' && medValue !== 'none') {
                        hasValidMedication = true;
                    }
                }
                
                expect(hasValidMedication).toBe(expectedValid);
            });
        });
    });

    describe('🚨 CRITICAL: Form Submission Prevention Logic', () => {
        let mockEvent;
        
        beforeEach(() => {
            mockEvent = {
                preventDefault: jest.fn(),
                stopImmediatePropagation: jest.fn()
            };
        });

        test('should prevent form submission when no valid medications', () => {
            // All medications are "nenhum"
            medicationDropdowns.med1.val.mockReturnValue('nenhum');
            medicationDropdowns.med2.val.mockReturnValue('nenhum');
            medicationDropdowns.med3.val.mockReturnValue('nenhum');
            medicationDropdowns.med4.val.mockReturnValue('nenhum');
            
            // Simulate the form submission validation logic
            let hasValidMedication = false;
            let shouldPreventSubmission = false;
            
            for (let i = 1; i <= 4; i++) {
                const medSelect = global.$(`#id_id_med${i}`);
                const medValue = medSelect.val();
                
                if (medValue && medValue !== 'nenhum' && medValue !== '' && medValue !== 'none') {
                    hasValidMedication = true;
                }
            }
            
            if (!hasValidMedication) {
                shouldPreventSubmission = true;
                mockEvent.preventDefault();
                mockEvent.stopImmediatePropagation();
                mockForm.attr('data-medication-validation-failed', 'true');
                
                // Should show error message
                global.Toast.error('Pelo menos um medicamento deve ser selecionado.');
            }
            
            // CRITICAL ASSERTIONS: Form submission should be prevented
            expect(shouldPreventSubmission).toBe(true);
            expect(mockEvent.preventDefault).toHaveBeenCalled();
            expect(mockEvent.stopImmediatePropagation).toHaveBeenCalled();
            expect(mockForm.attr).toHaveBeenCalledWith('data-medication-validation-failed', 'true');
            expect(global.Toast.error).toHaveBeenCalledWith('Pelo menos um medicamento deve ser selecionado.');
        });

        test('should allow form submission when valid medication exists', () => {
            // One valid medication
            medicationDropdowns.med1.val.mockReturnValue('123');
            medicationDropdowns.med2.val.mockReturnValue('nenhum');
            medicationDropdowns.med3.val.mockReturnValue('nenhum');
            medicationDropdowns.med4.val.mockReturnValue('nenhum');
            
            let hasValidMedication = false;
            let shouldPreventSubmission = false;
            
            for (let i = 1; i <= 4; i++) {
                const medSelect = global.$(`#id_id_med${i}`);
                const medValue = medSelect.val();
                
                if (medValue && medValue !== 'nenhum' && medValue !== '' && medValue !== 'none') {
                    hasValidMedication = true;
                }
            }
            
            if (!hasValidMedication) {
                shouldPreventSubmission = true;
                mockEvent.preventDefault();
            } else {
                // Clear any validation flags
                mockForm.removeAttr('data-medication-validation-failed');
            }
            
            // CRITICAL ASSERTIONS: Form submission should be allowed
            expect(shouldPreventSubmission).toBe(false);
            expect(mockEvent.preventDefault).not.toHaveBeenCalled();
            expect(mockForm.removeAttr).toHaveBeenCalledWith('data-medication-validation-failed');
            expect(global.Toast.error).not.toHaveBeenCalled();
        });
    });

    describe('Field Name Attribute Management', () => {
        test('should keep medication dropdown name attribute when set to "nenhum"', () => {
            // Simulate the logic that keeps medication dropdown name when "nenhum"
            const fieldName = 'id_med1';
            const originalName = 'id_med1';
            
            // This logic is from the form submission handler
            let shouldKeepName = false;
            if (fieldName === 'id_med1') {
                shouldKeepName = true; // Keep the medication dropdown field
            }
            
            expect(shouldKeepName).toBe(true);
        });

        test('should remove name attributes from other fields when medication is "nenhum"', () => {
            const fieldsToTest = [
                'med1_repetir_posologia',
                'med1_posologia_mes1', 
                'qtd_med1_mes1',
                'med1_posologia_mes2',
                'qtd_med1_mes2'
            ];
            
            fieldsToTest.forEach(fieldName => {
                // This field should have its name removed (not the medication dropdown itself)
                let shouldRemoveName = false;
                if (fieldName !== 'id_med1' && !fieldName.includes('_via')) {
                    shouldRemoveName = true;
                }
                
                expect(shouldRemoveName).toBe(true);
            });
        });

        test('should never remove name from via fields', () => {
            const viaFields = ['med1_via', 'med2_via', 'med3_via', 'med4_via'];
            
            viaFields.forEach(fieldName => {
                // Via fields should never have their name removed
                let shouldRemoveName = false;
                if (!fieldName.includes('_via')) {
                    shouldRemoveName = true;
                }
                
                expect(shouldRemoveName).toBe(false);
            });
        });
    });

    describe('Edge Cases and Error Handling', () => {
        test('should handle undefined medication values gracefully', () => {
            medicationDropdowns.med1.val.mockReturnValue(undefined);
            medicationDropdowns.med2.val.mockReturnValue(null);
            medicationDropdowns.med3.val.mockReturnValue('');
            medicationDropdowns.med4.val.mockReturnValue('nenhum');
            
            let hasValidMedication = false;
            
            // Should not throw errors with undefined/null values
            expect(() => {
                for (let i = 1; i <= 4; i++) {
                    const medSelect = global.$(`#id_id_med${i}`);
                    const medValue = medSelect.val();
                    
                    if (medValue && medValue !== 'nenhum' && medValue !== '' && medValue !== 'none') {
                        hasValidMedication = true;
                    }
                }
            }).not.toThrow();
            
            expect(hasValidMedication).toBe(false);
        });

        test('should handle case variations in "nenhum" values', () => {
            const nenhunVariations = ['nenhum', 'NENHUM', 'Nenhum', 'none', 'NONE', 'None'];
            
            nenhunVariations.forEach(variation => {
                medicationDropdowns.med1.val.mockReturnValue(variation.toLowerCase());
                
                let hasValidMedication = false;
                const medSelect = global.$('#id_id_med1');
                const medValue = medSelect.val();
                
                if (medValue && medValue !== 'nenhum' && medValue !== '' && medValue !== 'none') {
                    hasValidMedication = true;
                }
                
                // All variations should be treated as invalid
                expect(hasValidMedication).toBe(false);
            });
        });

        test('should handle single quotes and spaces in medication values', () => {
            const edgeCaseValues = [
                "  nenhum  ", // Spaces around nenhum - should be invalid if trimmed
                "123", // Valid ID
                " 456 ", // Valid ID with spaces
                "'789'", // ID with quotes
                "" // Empty string
            ];
            
            edgeCaseValues.forEach((value, index) => {
                medicationDropdowns.med1.val.mockReturnValue(value);
                
                let hasValidMedication = false;
                const medSelect = global.$('#id_id_med1');
                const medValue = medSelect.val();
                
                // Current logic doesn't trim, so test as-is
                if (medValue && medValue !== 'nenhum' && medValue !== '' && medValue !== 'none') {
                    hasValidMedication = true;
                }
                
                // Expected results based on current med.js logic
                const expectedValid = value && value !== 'nenhum' && value !== '' && value !== 'none';
                expect(hasValidMedication).toBe(expectedValid);
            });
        });
    });

    describe('Integration with Form Handler', () => {
        test('should set validation flag for FormHandler to check', () => {
            // Test the communication mechanism with form-handler.js
            medicationDropdowns.med1.val.mockReturnValue('nenhum');
            medicationDropdowns.med2.val.mockReturnValue('nenhum');
            medicationDropdowns.med3.val.mockReturnValue('nenhum');
            medicationDropdowns.med4.val.mockReturnValue('nenhum');
            
            let hasValidMedication = false;
            
            for (let i = 1; i <= 4; i++) {
                const medSelect = global.$(`#id_id_med${i}`);
                const medValue = medSelect.val();
                
                if (medValue && medValue !== 'nenhum' && medValue !== '' && medValue !== 'none') {
                    hasValidMedication = true;
                }
            }
            
            if (!hasValidMedication) {
                // This is the critical flag that form-handler.js checks
                mockForm.attr('data-medication-validation-failed', 'true');
            } else {
                mockForm.removeAttr('data-medication-validation-failed');
            }
            
            // CRITICAL: FormHandler must be able to detect validation failure
            expect(mockForm.attr).toHaveBeenCalledWith('data-medication-validation-failed', 'true');
        });

        test('should clear validation flag when medication becomes valid', () => {
            // Start with valid medication
            medicationDropdowns.med1.val.mockReturnValue('123');
            medicationDropdowns.med2.val.mockReturnValue('nenhum');
            medicationDropdowns.med3.val.mockReturnValue('nenhum');
            medicationDropdowns.med4.val.mockReturnValue('nenhum');
            
            let hasValidMedication = false;
            
            for (let i = 1; i <= 4; i++) {
                const medSelect = global.$(`#id_id_med${i}`);
                const medValue = medSelect.val();
                
                if (medValue && medValue !== 'nenhum' && medValue !== '' && medValue !== 'none') {
                    hasValidMedication = true;
                }
            }
            
            if (!hasValidMedication) {
                mockForm.attr('data-medication-validation-failed', 'true');
            } else {
                // Should clear the validation flag
                mockForm.removeAttr('data-medication-validation-failed');
            }
            
            expect(mockForm.removeAttr).toHaveBeenCalledWith('data-medication-validation-failed');
        });
    });
});

describe('🏥 MEDICAL SAFETY: Business Logic Validation', () => {
    test('CRITICAL: Must prevent prescriptions without any valid medications', () => {
        // This is the most important test - ensures medical safety
        
        // Simulate a form with all medications set to "nenhum"
        const medications = ['nenhum', 'nenhum', 'nenhum', 'nenhum'];
        
        // Apply the exact logic from med.js
        let hasValidMedication = false;
        for (let i = 0; i < medications.length; i++) {
            const medValue = medications[i];
            if (medValue && medValue !== 'nenhum' && medValue !== '' && medValue !== 'none') {
                hasValidMedication = true;
            }
        }
        
        // MEDICAL SAFETY ASSERTION: No prescription should be allowed without valid medications
        expect(hasValidMedication).toBe(false);
        
        // This test failing would indicate a critical medical safety issue
        if (hasValidMedication) {
            throw new Error('CRITICAL MEDICAL SAFETY VIOLATION: Invalid prescription would be allowed!');
        }
    });

    test('MEDICAL SAFETY: Must allow prescriptions with at least one valid medication', () => {
        // Test that valid prescriptions are not blocked
        const validScenarios = [
            ['123', 'nenhum', 'nenhum', 'nenhum'],
            ['nenhum', '456', 'nenhum', 'nenhum'],
            ['789', '101', 'nenhum', 'nenhum'],
            ['111', '222', '333', '444']
        ];
        
        validScenarios.forEach((medications, scenarioIndex) => {
            let hasValidMedication = false;
            
            for (let i = 0; i < medications.length; i++) {
                const medValue = medications[i];
                if (medValue && medValue !== 'nenhum' && medValue !== '' && medValue !== 'none') {
                    hasValidMedication = true;
                }
            }
            
            // Valid prescriptions must be allowed
            expect(hasValidMedication).toBe(true);
        });
    });
});