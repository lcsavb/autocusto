/**
 * CEP Handler using BrasilAPI and Alpine.js
 * Automatically fills address fields when CEP is entered
 */
function cepHandler() {
    return {
        init() {
            // Add event listener to CEP field
            const cepField = document.getElementById('cep');
            if (cepField) {
                cepField.addEventListener('blur', (e) => {
                    this.fetchAddress(e.target.value);
                });
            }
        },
        
        async fetchAddress(cep) {
            // Remove non-numeric characters
            const cleanCep = cep.replace(/\D/g, '');
            
            // Check if CEP has 8 digits
            if (cleanCep.length !== 8) {
                return;
            }
            
            try {
                const response = await fetch(`https://brasilapi.com.br/api/cep/v1/${cleanCep}`);
                
                if (!response.ok) {
                    throw new Error('CEP não encontrado');
                }
                
                const data = await response.json();
                
                // Fill all available fields
                this.fillField('id_logradouro', data.street);
                this.fillField('id_cidade', data.city);
                this.fillField('id_bairro', data.neighborhood);
                
            } catch (error) {
                console.error('Erro ao buscar CEP:', error);
            }
        },
        
        fillField(fieldId, value) {
            const field = document.getElementById(fieldId);
            if (field && value) {
                field.value = value;
            }
        }
    }
}