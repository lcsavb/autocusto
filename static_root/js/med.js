$(document).ready(function() {

    console.log('med.js loaded');
    
    // Test if jQuery is working
    console.log('jQuery version:', $.fn.jquery);
    console.log('Remove buttons found:', $('.remove-med').length);
    
    const addMed = document.querySelector('#add-med');
    if (addMed) {
        addMed.addEventListener('click', function (event) {
            console.log('AddMed clicked');
            const medSel = document.querySelector('#medicamentos-tab');
            const medicamento = document.querySelector('#medicamentos');
            
            if (!medSel || !medicamento) {
                console.log('Required elements not found');
                return;
            }
            
            const listaMedSel = Array.from(medSel.querySelectorAll('a.nav-link'));
            const listaMedicamentos = Array.from(medicamento.children);
            for (let n = 0; n < 5; n++) {
                console.log(`Checking medSel[${n}]`, listaMedSel[n]);
                if (listaMedSel[n] && listaMedSel[n].classList.contains('d-none')) {
                    event.preventDefault();
                    console.log(`Enabling medication ${n}`);
                    const medicamentoVinculado = document.querySelector(`#medicamento-${n}`);

                    listaMedSel.forEach(element => {
                        if (element !== listaMedSel[n]) {
                            element.classList.remove('active');
                            medicamentoVinculado.classList.remove('active');
                            medicamentoVinculado.classList.remove('show');
                        }
                        listaMedicamentos.forEach(element => {
                            if (element !== medicamentoVinculado) {
                                element.classList.remove('active');
                                element.classList.remove('show');
                            }
                        })
                    });
                    listaMedSel[n].classList.remove('d-none');
                    listaMedSel[n].classList.add('active');
                    listaMedicamentos[n].classList.toggle('active');
                    listaMedicamentos[n].classList.toggle('show');

                    // Show the remove button for this medication (if it exists)
                    const removeButton = listaMedSel[n].parentElement.querySelector('.remove-med');
                    if (removeButton) {
                        removeButton.classList.remove('d-none');
                        console.log(`Enabled remove button for medication ${n}`);
                    }

                    // Enable all fields for this medication and restore name attributes
                    console.log(`=== DEBUG: Finding fields for medication ${n+1} ===`);
                    
                    // Find all fields related to this medication by name pattern
                    const medNum = n + 1;
                    const allFields = $(`input[name*="med${medNum}"], select[name*="med${medNum}"], textarea[name*="med${medNum}"], input[name*="id_med${medNum}"], select[name*="id_med${medNum}"], textarea[name*="id_med${medNum}"]`);
                    console.log(`Found ${allFields.length} fields for medication ${medNum} by name pattern`);
                    
                    // Also find fields in the content area
                    const contentFields = $(listaMedicamentos[n]).find('input, select, textarea');
                    console.log(`Found ${contentFields.length} fields in medication ${medNum} content area`);
                    
                    // Combine both field sets
                    const combinedFields = allFields.add(contentFields);
                    console.log(`Total fields to enable: ${combinedFields.length}`);
                    
                    combinedFields.prop('disabled', false);
                    
                    // Restore name attributes for all fields
                    console.log(`=== DEBUG: Restoring name attributes for medication ${medNum} ===`);
                    combinedFields.each(function() {
                        const $field = $(this);
                        const fieldId = $field.attr('id');
                        const currentName = $field.attr('name');
                        
                        console.log(`Field ID: ${fieldId}, Current name: ${currentName}`);
                        
                        if (fieldId && !currentName) {
                            // Restore name attribute based on field ID
                            let nameAttr;
                            if (fieldId.startsWith('id_id_')) {
                                // Handle double id_ prefix (e.g., id_id_med2 → id_med2)
                                nameAttr = fieldId.replace('id_id_', 'id_');
                            } else if (fieldId.startsWith('id_')) {
                                // Handle single id_ prefix (e.g., id_med2_repetir_posologia → med2_repetir_posologia)
                                nameAttr = fieldId.replace('id_', '');
                            } else {
                                // No id_ prefix, use as is
                                nameAttr = fieldId;
                            }
                            $field.attr('name', nameAttr);
                            console.log(`✓ Restored name attribute: ${nameAttr} for field ${fieldId}`);
                        } else if (fieldId && currentName) {
                            console.log(`✓ Field ${fieldId} already has name: ${currentName}`);
                        } else if (!fieldId) {
                            console.log(`⚠ Field has no ID, skipping name restoration`);
                        }
                    });
                    console.log(`=== DEBUG: Name restoration complete for medication ${medNum} ===`);
                    
                    console.log(`Enabled fields for medicamento ${medNum}:`, combinedFields);

                    break;
                }
                else {
                    event.preventDefault();
                    console.log(`medSel[${n}] is not hidden, skipping`);
                }
        }
    });
    }
    
    // Function to switch to the highest-numbered visible medication tab
    function switchToPreviousVisibleMedication(removedMedNum) {
        console.log(`Switching to previous visible medication after removing ${removedMedNum}`);
        
        // Find the highest-numbered visible medication tab (excluding the one being removed)
        let targetMedNum = null;
        for (let i = 4; i >= 1; i--) {
            if (i !== removedMedNum) {
                const tab = $(`#medicamento-${i}-tab`);
                if (tab.length && !tab.hasClass('d-none')) {
                    targetMedNum = i;
                    console.log(`Found visible medication ${i} to switch to`);
                    break;
                }
            }
        }
        
        if (targetMedNum) {
            // Remove active class from all tabs and content
            $('.nav-link').removeClass('active');
            $('.tab-pane').removeClass('active show');
            
            // Activate the target medication tab and content
            $(`#medicamento-${targetMedNum}-tab`).addClass('active');
            $(`#medicamento-${targetMedNum}`).addClass('active show');
            
            console.log(`Switched to medication ${targetMedNum}`);
        } else {
            console.log('No visible medications found to switch to');
        }
    }

    // Disable fields for removed medications - using event delegation
    $(document).on('click', '.remove-med', function() {
        var medNum = $(this).data('med');
        console.log(`Remove button clicked for medication ${medNum}`);
        // Hide tab and content
        $('#medicamento-' + medNum + '-tab').addClass('d-none');
        $('#medicamento-' + medNum).removeClass('active show');
        
        // Hide the remove button for this medication
        $(this).addClass('d-none');
        console.log(`Hidden remove button for medication ${medNum}`);
        // Disable and clear all fields for this medication
        var fields = $('#medicamento-' + medNum + ' input, #medicamento-' + medNum + ' select, #medicamento-' + medNum + ' textarea');
        console.log(`Found ${fields.length} fields for medicamento ${medNum}`);
        fields.each(function() {
            var originalName = $(this).attr('name');
            $(this).prop('disabled', true).val('').removeAttr('name');
            console.log(`Field ${originalName} - disabled and name removed`);
            if (this.tagName === 'SELECT') {
                this.selectedIndex = 0;
            }
        });
        // Set medication name to DEBUG_REMOVED for debugging
        $('#medicamento-' + medNum + ' select[name*="id_med"]').val('').append('<option value="DEBUG_REMOVED" selected>DEBUG_REMOVED</option>');
        console.log(`Disabled and cleared fields for medicamento ${medNum}:`, fields);
        
        // Switch to the previous visible medication
        switchToPreviousVisibleMedication(medNum);
    });

    function repetirPosologia(numMed) {
        const botaoRepetirPosologia = $(`#id_med${numMed}_repetir_posologia`);
        const posologiaPrimeiroMes = $(`#id_med${numMed}_posologia_mes1`);
        const posologiaSegundoMes = $(`#id_med${numMed}_posologia_mes2`);
        const posologiaTerceiroMes = $(`#id_med${numMed}_posologia_mes3`);
        const posologiaQuartoMes = $(`#id_med${numMed}_posologia_mes4`);
        const posologiaQuintoMes = $(`#id_med${numMed}_posologia_mes5`);
        const posologiaSextoMes = $(`#id_med${numMed}_posologia_mes6`);
        const qtdPrimeiroMes = $(`#id_qtd_med${numMed}_mes1`)
        const qtdSegundoMes = $(`#id_qtd_med${numMed}_mes2`)
        const qtdTerceiroMes = $(`#id_qtd_med${numMed}_mes3`)
        const qtdQuartoMes = $(`#id_qtd_med${numMed}_mes4`)
        const qtdQuintoMes = $(`#id_qtd_med${numMed}_mes5`)
        const qtdSextoMes = $(`#id_qtd_med${numMed}_mes6`)
        const divPosologiasOpcionais = $(`#posologias-opcionais-med${numMed}`)

        botaoRepetirPosologia.change(function () {
            console.log(`Toggle posologias opcionais for med${numMed}`);
            divPosologiasOpcionais.toggleClass('d-none');
        });

        posologiaPrimeiroMes.keyup(function () {
            if (botaoRepetirPosologia.val() == 'True') {
                console.log(`Copy posologia for med${numMed} from mes1 to all`);
                posologiaSegundoMes.val(posologiaPrimeiroMes.val());
                posologiaTerceiroMes.val(posologiaPrimeiroMes.val());
                posologiaQuartoMes.val(posologiaPrimeiroMes.val());
                posologiaQuintoMes.val(posologiaPrimeiroMes.val());
                posologiaSextoMes.val(posologiaPrimeiroMes.val());
            }
        });

        qtdPrimeiroMes.keyup(function () {
            if (botaoRepetirPosologia.val() == 'True') {
                console.log(`Copy quantidade for med${numMed} from mes1 to all`);
                qtdSegundoMes.val(qtdPrimeiroMes.val());
                qtdTerceiroMes.val(qtdPrimeiroMes.val());
                qtdQuartoMes.val(qtdPrimeiroMes.val());
                qtdQuintoMes.val(qtdPrimeiroMes.val());
                qtdSextoMes.val(qtdPrimeiroMes.val());
            }
        });

    }

    repetirPosologia(1);
    repetirPosologia(2);
    repetirPosologia(3);
    repetirPosologia(4);
    repetirPosologia(5);

    // Handle tab switching for medications
    $(document).on('click', 'a[data-toggle="pill"]', function(e) {
        e.preventDefault();
        console.log('Tab clicked:', $(this).attr('id'));
        
        // Remove active class from all medication tabs
        $('#medicamentos-tab a.nav-link').removeClass('active');
        
        // Remove active and show from all medication content
        $('#medicamentos .tab-pane').removeClass('active show');
        
        // Add active class to clicked tab
        $(this).addClass('active');
        
        // Show corresponding content
        const targetContent = $($(this).attr('href'));
        targetContent.addClass('active show');
        
        console.log('Tab switched to:', $(this).attr('href'));
    });

    // HYBRID APPROACH: Handle "nenhum" selection
    
    // Option 1: Immediate change event listeners for medication dropdowns
    function initializeMedicationChangeListeners() {
        for (let medNumber = 1; medNumber <= 4; medNumber++) {
            const medSelect = $(`#id_id_med${medNumber}`);
            if (medSelect.length) {
                medSelect.on('change', function() {
                    const value = $(this).val();
                    console.log(`Medication ${medNumber} changed to: ${value}`);
                    
                    if (!value || value === 'nenhum' || value === '' || value === 'none') {
                        console.log(`Clearing fields for medication ${medNumber} due to nenhum/empty selection`);
                        clearMedicationFieldsFromNenhum(medNumber);
                        
                        // Hide tab for medications 2-4 (med 1 is always required)
                        if (medNumber > 1) {
                            $(`#medicamento-${medNumber}-tab`).addClass('d-none').removeClass('active');
                            $(`#medicamento-${medNumber}`).removeClass('active show');
                            $(`[data-med="${medNumber}"].remove-med`).addClass('d-none');
                            
                            // Switch to the previous visible medication
                            switchToPreviousVisibleMedication(medNumber);
                        }
                    } else {
                        // Valid medication selected - re-enable fields
                        console.log(`Valid medication selected for ${medNumber}, re-enabling fields`);
                        enableMedicationFieldsFromNenhum(medNumber);
                    }
                });
            }
        }
    }
    
    // Function to clear fields when "nenhum" is selected
    function clearMedicationFieldsFromNenhum(medNumber) {
        const fields = $(`#medicamento-${medNumber} input, #medicamento-${medNumber} select, #medicamento-${medNumber} textarea`);
        console.log(`Clearing ${fields.length} fields for medication ${medNumber}`);
        
        fields.each(function() {
            const $field = $(this);
            const originalName = $field.attr('name');
            const fieldName = $field.attr('name') || $field.attr('id') || '';
            
            // Skip the via field - it should never be disabled
            if (fieldName.includes('_via')) {
                console.log(`Skipping via field: ${originalName}`);
                return; // Skip this field
            }
            
            // Clear value
            if (this.tagName === 'SELECT') {
                this.selectedIndex = 0;
            } else if (this.type === 'checkbox' || this.type === 'radio') {
                this.checked = false;
            } else {
                $field.val('');
            }
            
            // For medication 1 (always required): only clear values and remove name attributes, but keep fields enabled
            // For medications 2-4: clear values, remove name attributes, AND disable fields
            if (medNumber === 1) {
                // Medication 1 is always required - keep fields enabled but remove from submission
                $field.removeAttr('name');
                console.log(`Cleared field but kept enabled (med 1): ${originalName}`);
            } else {
                // Medications 2-4 can be fully disabled
                $field.removeAttr('name').prop('disabled', true);
                console.log(`Cleared and disabled field: ${originalName}`);
            }
        });
    }
    
    // Function to re-enable fields when a valid medication is selected after "nenhum"
    function enableMedicationFieldsFromNenhum(medNumber) {
        const fields = $(`#medicamento-${medNumber} input, #medicamento-${medNumber} select, #medicamento-${medNumber} textarea`);
        console.log(`Re-enabling ${fields.length} fields for medication ${medNumber}`);
        
        fields.each(function() {
            const $field = $(this);
            const fieldId = $field.attr('id');
            
            // Skip the via field - it should never be disabled anyway
            const fieldName = $field.attr('name') || $field.attr('id') || '';
            if (fieldName.includes('_via')) {
                console.log(`Skipping via field (already enabled): ${fieldName}`);
                return; // Skip this field
            }
            
            // Re-enable the field
            $field.prop('disabled', false);
            
            // Restore name attribute based on field ID
            if (fieldId && !$field.attr('name')) {
                let nameAttr;
                if (fieldId.startsWith('id_id_')) {
                    // Handle double id_ prefix (e.g., id_id_med2 → id_med2)
                    nameAttr = fieldId.replace('id_id_', 'id_');
                } else if (fieldId.startsWith('id_')) {
                    // Handle single id_ prefix (e.g., id_med2_repetir_posologia → med2_repetir_posologia)
                    nameAttr = fieldId.replace('id_', '');
                } else {
                    // No id_ prefix, use as is
                    nameAttr = fieldId;
                }
                $field.attr('name', nameAttr);
                console.log(`✓ Re-enabled and restored name attribute: ${nameAttr} for field ${fieldId}`);
            } else if (fieldId && $field.attr('name')) {
                console.log(`✓ Re-enabled field ${fieldId} (name already exists: ${$field.attr('name')})`);
            } else {
                console.log(`⚠ Field has no ID, skipping name restoration`);
            }
        });
    }
    
    // Option 2: Enhanced form submission handler
    $('form').on('submit', function() {
        console.log('Form submitting - checking for blank medications');
        
        // Check all medications 1-4 (enhanced to include med 1)
        for (let i = 1; i <= 4; i++) {
            const medSelect = $(`#id_id_med${i}`);
            const medValue = medSelect.val();
            
            if (!medValue || medValue === 'nenhum' || medValue === '' || medValue === 'none') {
                console.log(`Medication ${i} is blank/nenhum (${medValue}), removing all fields from submission`);
                
                // Remove name attribute from all fields for this medication (except via field)
                $(`#medicamento-${i} input, #medicamento-${i} select, #medicamento-${i} textarea`).each(function() {
                    const originalName = $(this).attr('name');
                    const fieldName = $(this).attr('name') || $(this).attr('id') || '';
                    
                    // Skip the via field - it should never have its name removed
                    if (fieldName.includes('_via')) {
                        console.log(`Form submit: Skipping via field: ${originalName}`);
                        return; // Skip this field
                    }
                    
                    $(this).removeAttr('name');
                    console.log(`Form submit: Removed name attribute from ${originalName}`);
                });
            }
        }
    });
    
    // Initialize the change listeners
    initializeMedicationChangeListeners();
    console.log('Hybrid nenhum handling initialized');

});
