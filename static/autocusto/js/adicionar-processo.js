/**
 * Adicionar Processo Component for Alpine.js
 * Replaces jQuery-based buscaDoencas.js and buscaPacientes.js
 */

console.log('adicionar-processo.js file loaded');

// Check if Alpine is already available
if (window.Alpine) {
  console.log('Alpine already available, registering component immediately');
  window.Alpine.data('adicionarProcesso', () => ({
    // Disease search
    diseases: [],
    showDiseases: false,
    
    // Patient search
    patients: [],
    showPatients: false,
    
    // Loading states
    searchingDiseases: false,
    searchingPatients: false,
    
    // URLs from form data attributes
    get diseaseSearchUrl() {
      return document.querySelector('#js-form')?.dataset.buscaDoencas || '';
    },
    
    get patientSearchUrl() {
      return document.querySelector('#js-form')?.dataset.buscaPacientes || '';
    },
    
    // Search for diseases based on CID input
    async searchDiseases(keyword) {
      if (keyword.length <= 2) {
        this.diseases = [];
        this.showDiseases = false;
        return;
      }
      
      this.searchingDiseases = true;
      this.showDiseases = true;
      
      // Clear patient results when searching diseases
      this.patients = [];
      this.showPatients = false;
      
      try {
        const response = await fetch(`${this.diseaseSearchUrl}?palavraChave=${encodeURIComponent(keyword)}`, {
          headers: {
            'Accept': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
          }
        });
        
        if (response.ok) {
          const data = await response.json();
          this.diseases = data;
        } else {
          this.diseases = [];
        }
      } catch (error) {
        console.error('Error searching diseases:', error);
        this.diseases = [];
      } finally {
        this.searchingDiseases = false;
      }
    },
    
    // Search for patients based on CPF input
    async searchPatients(keyword) {
      if (keyword.length <= 2) {
        this.patients = [];
        this.showPatients = false;
        return;
      }
      
      this.searchingPatients = true;
      this.showPatients = true;
      
      try {
        const response = await fetch(`${this.patientSearchUrl}?palavraChave=${encodeURIComponent(keyword)}`, {
          headers: {
            'Accept': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
          }
        });
        
        if (response.ok) {
          const data = await response.json();
          this.patients = data;
        } else {
          this.patients = [];
        }
      } catch (error) {
        console.error('Error searching patients:', error);
        this.patients = [];
      } finally {
        this.searchingPatients = false;
      }
    },
    
    // Select a disease from the dropdown
    selectDisease(cid) {
      document.getElementById('id_cid').value = cid;
      this.diseases = [];
      this.showDiseases = false;
    },
    
    // Select a patient from the dropdown
    selectPatient(cpf) {
      document.getElementById('id_cpf_paciente').value = cpf;
      this.patients = [];
      this.showPatients = false;
    },
    
    // Format CPF input
    formatCpf(event) {
      let value = event.target.value.replace(/\D/g, '');
      if (value.length <= 11) {
        value = value.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4');
        value = value.replace(/(\d{3})(\d{3})(\d{3})/, '$1.$2.$3');
        value = value.replace(/(\d{3})(\d{3})/, '$1.$2');
        value = value.replace(/(\d{3})/, '$1');
      }
      event.target.value = value;
    },
    
    // Hide dropdowns when clicking outside
    hideDropdowns() {
      this.showDiseases = false;
      this.showPatients = false;
    }
  }));
} else {
  console.log('Alpine not available, waiting for alpine:init event');
  document.addEventListener('alpine:init', () => {
    console.log('Registering adicionarProcesso component via event');
    Alpine.data('adicionarProcesso', () => ({
      // Disease search
      diseases: [],
      showDiseases: false,
      
      // Patient search
      patients: [],
      showPatients: false,
      
      // Loading states
      searchingDiseases: false,
      searchingPatients: false,
      
      // URLs from form data attributes
      get diseaseSearchUrl() {
        return document.querySelector('#js-form')?.dataset.buscaDoencas || '';
      },
      
      get patientSearchUrl() {
        return document.querySelector('#js-form')?.dataset.buscaPacientes || '';
      },
      
      // Search for diseases based on CID input
      async searchDiseases(keyword) {
        if (keyword.length <= 2) {
          this.diseases = [];
          this.showDiseases = false;
          return;
        }
        
        this.searchingDiseases = true;
        this.showDiseases = true;
        
        // Clear patient results when searching diseases
        this.patients = [];
        this.showPatients = false;
        
        try {
          const response = await fetch(`${this.diseaseSearchUrl}?palavraChave=${encodeURIComponent(keyword)}`, {
            headers: {
              'Accept': 'application/json',
              'X-Requested-With': 'XMLHttpRequest'
            }
          });
          
          if (response.ok) {
            const data = await response.json();
            this.diseases = data;
          } else {
            this.diseases = [];
          }
        } catch (error) {
          console.error('Error searching diseases:', error);
          this.diseases = [];
        } finally {
          this.searchingDiseases = false;
        }
      },
      
      // Search for patients based on CPF input
      async searchPatients(keyword) {
        if (keyword.length <= 2) {
          this.patients = [];
          this.showPatients = false;
          return;
        }
        
        this.searchingPatients = true;
        this.showPatients = true;
        
        try {
          const response = await fetch(`${this.patientSearchUrl}?palavraChave=${encodeURIComponent(keyword)}`, {
            headers: {
              'Accept': 'application/json',
              'X-Requested-With': 'XMLHttpRequest'
            }
          });
          
          if (response.ok) {
            const data = await response.json();
            this.patients = data;
          } else {
            this.patients = [];
          }
        } catch (error) {
          console.error('Error searching patients:', error);
          this.patients = [];
        } finally {
          this.searchingPatients = false;
        }
      },
      
      // Select a disease from the dropdown
      selectDisease(cid) {
        document.getElementById('id_cid').value = cid;
        this.diseases = [];
        this.showDiseases = false;
      },
      
      // Select a patient from the dropdown
      selectPatient(cpf) {
        document.getElementById('id_cpf_paciente').value = cpf;
        this.patients = [];
        this.showPatients = false;
      },
      
      // Format CPF input
      formatCpf(event) {
        let value = event.target.value.replace(/\D/g, '');
        if (value.length <= 11) {
          value = value.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4');
          value = value.replace(/(\d{3})(\d{3})(\d{3})/, '$1.$2.$3');
          value = value.replace(/(\d{3})(\d{3})/, '$1.$2');
          value = value.replace(/(\d{3})/, '$1');
        }
        event.target.value = value;
      },
      
      // Hide dropdowns when clicking outside
      hideDropdowns() {
        this.showDiseases = false;
        this.showPatients = false;
      }
    }));
  });
}