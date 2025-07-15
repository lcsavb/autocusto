/**
 * PDF Modal Component for Alpine.js
 * Reusable modal for displaying PDFs across the application
 */

document.addEventListener('alpine:init', () => {
  // PDF Modal Component
  Alpine.data('pdfModal', () => ({
    isOpen: false,
    pdfUrl: '',
    title: 'Documento PDF',
    showDownload: true,
    
    openPdf(url, modalTitle = 'Documento PDF', allowDownload = true) {
      this.pdfUrl = url;
      this.title = modalTitle;
      this.showDownload = allowDownload;
      this.isOpen = true;
      document.body.style.overflow = 'hidden';
    },
    
    closePdf() {
      this.isOpen = false;
      this.pdfUrl = '';
      document.body.style.overflow = '';
    },
    
    downloadPdf() {
      if (this.pdfUrl) {
        const link = document.createElement('a');
        link.href = this.pdfUrl;
        link.download = this.title.replace(/\s+/g, '_') + '.pdf';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      }
    },
    
    async printPdf() {
      if (!this.pdfUrl) return;
      
      try {
        // Check if we can use silent printing
        const canSilentPrint = await this.checkSilentPrintPermission();
        
        if (canSilentPrint) {
          console.log('Attempting silent print...');
          await this.attemptSilentPrint();
        } else {
          console.log('Falling back to dialog print...');
          this.dialogPrint();
        }
      } catch (error) {
        console.log('Print error, falling back to dialog:', error);
        this.dialogPrint();
      }
    },

    async checkSilentPrintPermission() {
      // Check user preference from localStorage
      const userPreference = localStorage.getItem('preferDirectPrint');
      if (userPreference === 'true') {
        return true;
      }
      
      if (userPreference === 'false') {
        return false;
      }

      // Ask user for the first time
      return await this.requestPrintPermission();
    },

    async requestPrintPermission() {
      // Show a custom dialog to ask user
      const userWantsDirectPrint = confirm(
        'Deseja ativar impressão direta sem diálogo?\n\n' +
        'Isso permitirá imprimir PDFs automaticamente sem mostrar a janela de impressão.\n\n' +
        'Você pode alterar essa configuração a qualquer momento.'
      );
      
      // Store user preference
      localStorage.setItem('preferDirectPrint', userWantsDirectPrint ? 'true' : 'false');
      
      return userWantsDirectPrint;
    },

    async attemptSilentPrint() {
      try {
        // Create hidden iframe for silent printing
        const iframe = document.createElement('iframe');
        iframe.style.position = 'fixed';
        iframe.style.top = '-1000px';
        iframe.style.left = '-1000px';
        iframe.style.width = '1px';
        iframe.style.height = '1px';
        iframe.style.opacity = '0';
        iframe.style.border = 'none';
        iframe.src = this.pdfUrl;
        
        document.body.appendChild(iframe);
        
        return new Promise((resolve, reject) => {
          const timeout = setTimeout(() => {
            document.body.removeChild(iframe);
            reject(new Error('Print timeout'));
          }, 5000);
          
          iframe.onload = () => {
            clearTimeout(timeout);
            try {
              // Try silent print
              iframe.contentWindow.print();
              
              // Show success message via Alpine.js
              this.$dispatch('add-toast', {
                message: 'PDF enviado para impressão!',
                type: 'success'
              });
              
              // Clean up
              setTimeout(() => {
                if (document.body.contains(iframe)) {
                  document.body.removeChild(iframe);
                }
                resolve();
              }, 1000);
            } catch (error) {
              if (document.body.contains(iframe)) {
                document.body.removeChild(iframe);
              }
              reject(error);
            }
          };
          
          iframe.onerror = () => {
            clearTimeout(timeout);
            if (document.body.contains(iframe)) {
              document.body.removeChild(iframe);
            }
            reject(new Error('Failed to load PDF'));
          };
        });
      } catch (error) {
        throw error;
      }
    },

    dialogPrint() {
      // Traditional print with dialog
      const printWindow = window.open(this.pdfUrl, '_blank', 'width=800,height=600');
      
      if (printWindow) {
        printWindow.onload = function() {
          printWindow.print();
        };
        
        this.$dispatch('add-toast', {
          message: 'PDF aberto em nova janela. Use Ctrl+P para imprimir.',
          type: 'info'
        });
      } else {
        this.$dispatch('add-toast', {
          message: 'Popup bloqueado. Permita popups e tente novamente.',
          type: 'warning'
        });
      }
    },

    // Method to reset print preferences (for settings)
    resetPrintPreferences() {
      localStorage.removeItem('preferDirectPrint');
      this.$dispatch('add-toast', {
        message: 'Preferências de impressão redefinidas.',
        type: 'info'
      });
    }
  }));

  // Renovacao Form Component
  Alpine.data('renovacaoForm', () => ({
    isSubmitting: false,
    
    // Date formatting and validation
    formatDate(event) {
      let value = event.target.value.replace(/\D/g, '');
      if (value.length >= 2) value = value.substring(0,2) + '/' + value.substring(2);
      if (value.length >= 5) value = value.substring(0,5) + '/' + value.substring(5);
      if (value.length > 10) value = value.substring(0,10);
      event.target.value = value;
    },
    
    // Date validation
    isValidDate(dateString) {
      if (!dateString || dateString.length !== 10) return false;
      const [day, month, year] = dateString.split('/');
      const date = new Date(year, month - 1, day);
      return Boolean(+date) && 
             date.getDate() == day && 
             date.getMonth() == month - 1 && 
             date.getFullYear() == year;
    },
    
    // Form submission
    async submitForm(event) {
      event.preventDefault();
      
      const formData = new FormData(event.target);
      const dateValue = formData.get('data_1');
      
      // Validate date
      if (!this.isValidDate(dateValue)) {
        console.log('Dispatching date validation error toast');
        this.$dispatch('add-toast', {
          message: 'Data inválida! Use o formato DD/MM/AAAA',
          type: 'error'
        });
        return;
      }
      
      this.isSubmitting = true;
      
      try {
        const response = await fetch(event.target.action, {
          method: 'POST',
          body: formData,
          headers: {
            'Accept': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
          }
        });
        
        const data = await response.json();
        
        if (data.success) {
          // Open PDF in modal
          this.$dispatch('open-pdf', {
            url: data.pdf_url,
            title: 'Renovação de Processo',
            allowDownload: true
          });
          
          // Show success toast using Alpine.js event system
          console.log('Dispatching success toast');
          this.$dispatch('add-toast', {
            message: data.message || 'PDF gerado com sucesso!',
            type: 'success'
          });
        } else {
          // Show error toast using Alpine.js event system
          console.log('Dispatching error toast');
          this.$dispatch('add-toast', {
            message: data.error || 'Erro ao gerar PDF',
            type: 'error'
          });
        }
      } catch (error) {
        console.error('Error:', error);
        console.log('Dispatching connection error toast');
        this.$dispatch('add-toast', {
          message: 'Erro de conexão. Tente novamente.',
          type: 'error'
        });
      } finally {
        this.isSubmitting = false;
      }
    }
  }));
});