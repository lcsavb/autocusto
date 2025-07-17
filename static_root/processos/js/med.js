(() => {
    const addMed = document.querySelector('#add-med');

    addMed.addEventListener('click', function (event) {
        event.preventDefault();
        
        // Get all medication tabs (a elements)
        const medTabs = document.querySelectorAll('#medicamentos-tab a[id$="-tab"]');
        const medicamento = document.querySelector('#medicamentos').children;
        const listaMedicamentos = Array.from(medicamento);
        
        for (let n = 0; n < medTabs.length; n++) {
            const currentTab = medTabs[n];
            if (currentTab.classList.contains('d-none')) {
                const medicamentoVinculado = document.querySelector(`#medicamento-${n + 1}`);

                // Remove active class from all tabs and contents
                medTabs.forEach(tab => {
                    tab.classList.remove('active');
                });
                
                listaMedicamentos.forEach(element => {
                    element.classList.remove('active');
                    element.classList.remove('show');
                });

                // Show and activate the new medication
                currentTab.classList.remove('d-none');
                currentTab.classList.add('active');
                medicamentoVinculado.classList.add('active');
                medicamentoVinculado.classList.add('show');
                
                // Show remove button for this medication (except for med 1 which is always required)
                if (n > 0) {
                    const removeButton = document.querySelector(`[data-med="${n + 1}"].remove-med`);
                    if (removeButton) removeButton.classList.remove('d-none');
                }
                
                // Re-enable fields for this medication
                enableMedicationFields(n + 1);

                break;
            }
        }
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
            divPosologiasOpcionais.toggleClass('d-none');
        });

        posologiaPrimeiroMes.keyup(function () {
            if (botaoRepetirPosologia.val() == 'True') {
                posologiaSegundoMes.val(posologiaPrimeiroMes.val());
                posologiaTerceiroMes.val(posologiaPrimeiroMes.val());
                posologiaQuartoMes.val(posologiaPrimeiroMes.val());
                posologiaQuintoMes.val(posologiaPrimeiroMes.val());
                posologiaSextoMes.val(posologiaPrimeiroMes.val());
            }
        });

        qtdPrimeiroMes.keyup(function () {
            if (botaoRepetirPosologia.val() == 'True') {
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

    // Handle manual tab switching
    const medicationTabs = document.querySelectorAll('#medicamentos-tab a[id$="-tab"]');
    
    medicationTabs.forEach(tab => {
        tab.addEventListener('click', function(event) {
            event.preventDefault();
            
            // Remove active class from all tabs and contents
            medicationTabs.forEach(t => t.classList.remove('active'));
            const allContents = document.querySelectorAll('#medicamentos .tab-pane');
            allContents.forEach(content => {
                content.classList.remove('active', 'show');
            });
            
            // Add active class to clicked tab
            this.classList.add('active');
            
            // Show corresponding content
            const targetId = this.getAttribute('href').substring(1);
            const targetContent = document.querySelector(`#${targetId}`);
            if (targetContent) {
                targetContent.classList.add('active', 'show');
            }
        });
    });

    // Remove medication functionality
    const removeMedButtons = document.querySelectorAll('.remove-med');
    
    removeMedButtons.forEach(button => {
        button.addEventListener('click', function(event) {
            event.preventDefault();
            const medNumber = this.getAttribute('data-med');
            removeMedication(medNumber);
        });
    });

    function removeMedication(medNumber) {
        // Get the tab and content elements
        const tabElement = document.querySelector(`#medicamento-${medNumber}-tab`);
        const contentElement = document.querySelector(`#medicamento-${medNumber}`);
        
        // Check if this was the active tab before removing classes
        const wasActive = tabElement.classList.contains('active');
        
        // Hide the tab and content
        tabElement.classList.add('d-none');
        tabElement.classList.remove('active');
        contentElement.classList.remove('active', 'show');
        
        // Hide remove button
        const removeButton = document.querySelector(`[data-med="${medNumber}"].remove-med`);
        if (removeButton) removeButton.classList.add('d-none');
        
        // Clear all form fields for this medication
        clearMedicationFields(medNumber);
        
        // If this was the active tab, switch to the first visible tab
        if (wasActive) {
            switchToFirstVisibleTab();
        }
    }

    function clearMedicationFields(medNumber) {
        // Clear medication selection, remove name attribute, and disable
        const medSelect = document.querySelector(`#id_med${medNumber}`);
        if (medSelect) {
            medSelect.value = '';
            medSelect.removeAttribute('name');
            medSelect.disabled = true;
        }
        
        // Clear via field, remove name attribute, and disable
        const viaField = document.querySelector(`#id_med${medNumber}_via`);
        if (viaField) {
            viaField.value = '';
            viaField.removeAttribute('name');
            viaField.disabled = true;
        }
        
        // Clear repeat posology checkbox, remove name attribute, and disable
        const repeatCheckbox = document.querySelector(`#id_med${medNumber}_repetir_posologia`);
        if (repeatCheckbox) {
            repeatCheckbox.checked = false;
            repeatCheckbox.removeAttribute('name');
            repeatCheckbox.disabled = true;
        }
        
        // Clear all month fields, remove name attributes, and disable
        for (let month = 1; month <= 6; month++) {
            const posologyField = document.querySelector(`#id_med${medNumber}_posologia_mes${month}`);
            const quantityField = document.querySelector(`#id_qtd_med${medNumber}_mes${month}`);
            
            if (posologyField) {
                posologyField.value = '';
                posologyField.removeAttribute('name');
                posologyField.disabled = true;
            }
            if (quantityField) {
                quantityField.value = '';
                quantityField.removeAttribute('name');
                quantityField.disabled = true;
            }
        }
        
        // Hide optional posology fields
        const optionalDiv = document.querySelector(`#posologias-opcionais-med${medNumber}`);
        if (optionalDiv) optionalDiv.classList.add('d-none');
    }
    
    function enableMedicationFields(medNumber) {
        // Re-enable medication selection and restore name attribute
        const medSelect = document.querySelector(`#id_med${medNumber}`);
        if (medSelect) {
            medSelect.setAttribute('name', `id_med${medNumber}`);
            medSelect.disabled = false;
        }
        
        // Re-enable via field and restore name attribute
        const viaField = document.querySelector(`#id_med${medNumber}_via`);
        if (viaField) {
            viaField.setAttribute('name', `med${medNumber}_via`);
            viaField.disabled = false;
        }
        
        // Re-enable repeat posology checkbox and restore name attribute
        const repeatCheckbox = document.querySelector(`#id_med${medNumber}_repetir_posologia`);
        if (repeatCheckbox) {
            repeatCheckbox.setAttribute('name', `med${medNumber}_repetir_posologia`);
            repeatCheckbox.disabled = false;
        }
        
        // Re-enable all month fields and restore name attributes
        for (let month = 1; month <= 6; month++) {
            const posologyField = document.querySelector(`#id_med${medNumber}_posologia_mes${month}`);
            const quantityField = document.querySelector(`#id_qtd_med${medNumber}_mes${month}`);
            
            if (posologyField) {
                posologyField.setAttribute('name', `med${medNumber}_posologia_mes${month}`);
                posologyField.disabled = false;
            }
            if (quantityField) {
                quantityField.setAttribute('name', `qtd_med${medNumber}_mes${month}`);
                quantityField.disabled = false;
            }
        }
    }

    function switchToFirstVisibleTab() {
        const tabs = document.querySelectorAll('#medicamentos-tab .nav-link');
        const contents = document.querySelectorAll('#medicamentos .tab-pane');
        
        // First remove active class from all tabs and contents
        tabs.forEach(tab => tab.classList.remove('active'));
        contents.forEach(content => content.classList.remove('active', 'show'));
        
        // Find first visible tab and activate it
        for (let tab of tabs) {
            if (!tab.classList.contains('d-none') && tab.id !== 'add-med') {
                tab.classList.add('active');
                const tabTarget = tab.getAttribute('href').substring(1);
                const targetContent = document.querySelector(`#${tabTarget}`);
                if (targetContent) {
                    targetContent.classList.add('active', 'show');
                }
                break;
            }
        }
    }
    
    // HYBRID APPROACH: Handle "nenhum" selection
    
    // Option 1: Immediate change event listeners for each medication dropdown
    function initializeMedicationChangeListeners() {
        for (let medNumber = 1; medNumber <= 4; medNumber++) {
            const medSelect = document.querySelector(`#id_med${medNumber}`);
            if (medSelect) {
                medSelect.addEventListener('change', function() {
                    console.log(`Medication ${medNumber} changed to: ${this.value}`);
                    
                    if (this.value === 'nenhum' || this.value === '' || this.value === 'none') {
                        console.log(`Clearing fields for medication ${medNumber} due to nenhum/empty selection`);
                        clearMedicationFields(medNumber);
                        
                        // Optionally hide the tab for better UX (except med1 which is always required)
                        if (medNumber > 1) {
                            const tabElement = document.querySelector(`#medicamento-${medNumber}-tab`);
                            const contentElement = document.querySelector(`#medicamento-${medNumber}`);
                            if (tabElement && contentElement) {
                                tabElement.classList.add('d-none');
                                tabElement.classList.remove('active');
                                contentElement.classList.remove('active', 'show');
                                
                                // Switch to first visible tab if this was active
                                if (contentElement.classList.contains('active')) {
                                    switchToFirstVisibleTab();
                                }
                            }
                        }
                    } else {
                        console.log(`Enabling fields for medication ${medNumber}`);
                        enableMedicationFields(medNumber);
                    }
                });
            }
        }
    }
    
    // Option 2: Form submission handler as backup
    function initializeFormSubmissionHandler() {
        const form = document.querySelector('form');
        if (form) {
            form.addEventListener('submit', function(e) {
                console.log('Form submission - checking for nenhum medications');
                
                for (let medNumber = 1; medNumber <= 4; medNumber++) {
                    const medSelect = document.querySelector(`#id_med${medNumber}`);
                    if (medSelect) {
                        const value = medSelect.value;
                        if (value === 'nenhum' || value === '' || value === 'none') {
                            console.log(`Form submit: Clearing fields for medication ${medNumber} (value: ${value})`);
                            clearMedicationFields(medNumber);
                        }
                    }
                }
            });
        }
    }
    
    // Initialize both approaches on DOM ready
    document.addEventListener('DOMContentLoaded', function() {
        initializeMedicationChangeListeners();
        initializeFormSubmissionHandler();
        console.log('Hybrid nenhum handling initialized');
    });


})();
