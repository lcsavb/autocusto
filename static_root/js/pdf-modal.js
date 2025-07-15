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
    
    printPdf() {
      if (this.pdfUrl) {
        const printWindow = window.open(this.pdfUrl, '_blank');
        if (printWindow) {
          printWindow.onload = function() {
            printWindow.print();
          };
        }
      }
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