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
    showEdit: false,
    processoId: null,
    
    openPdf(url, modalTitle = 'Documento PDF', allowDownload = true, allowEdit = false, processoId = null) {
      this.pdfUrl = url;
      this.title = modalTitle;
      this.showDownload = allowDownload;
      this.showEdit = allowEdit;
      this.processoId = processoId;
      this.isOpen = true;
      document.body.style.overflow = 'hidden';
    },
    
    closePdf() {
      this.isOpen = false;
      this.pdfUrl = '';
      document.body.style.overflow = '';
      // Dispatch custom event when modal is closed
      this.$dispatch('modal-closed');
    },

    async editProcess() {
      // If we have a processo_id, set it in session before redirecting
      if (this.processoId) {
        try {
          // Send AJAX request to set processo_id in session
          const response = await fetch('/processos/set-edit-session/', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value
            },
            body: JSON.stringify({
              processo_id: this.processoId
            })
          });
          
          if (response.ok) {
            window.location.href = '/processos/edicao/';
          } else {
            Toast.error('Erro ao preparar edição. Tente novamente.');
          }
        } catch (error) {
          console.error('Error setting edit session:', error);
          Toast.error('Erro de conexão. Tente novamente.');
        }
      } else {
        // Fallback: redirect directly (session should already have processo_id set)
        window.location.href = '/processos/edicao/';
      }
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
      if (!this.pdfUrl) return;
      
      // Traditional print with dialog
      const printWindow = window.open(this.pdfUrl, '_blank', 'width=800,height=600');
      
      if (printWindow) {
        printWindow.onload = function() {
          printWindow.print();
        };
        
        Toast.info('PDF aberto em nova janela. Use Ctrl+P para imprimir.');
      } else {
        Toast.warning('Popup bloqueado. Permita popups e tente novamente.');
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
      const isEditing = formData.get('edicao'); // Check if edit checkbox is checked
      
      // Validate date
      if (!this.isValidDate(dateValue)) {
        // Date validation should be immediate - no delay needed
        Toast.error('Data inválida! Use o formato DD/MM/AAAA');
        return;
      }
      
      // If editing is enabled, submit form normally to allow redirect
      if (isEditing) {
        event.target.submit(); // Submit form normally, allowing backend redirect
        return;
      }
      
      // Otherwise, use AJAX for PDF generation
      this.isSubmitting = true;
      
      // Show progress bar elements
      const submitBtn = event.target.querySelector('button[type="submit"]');
      if (submitBtn) {
        const submitText = submitBtn.querySelector('.submit-text');
        const loadingText = submitBtn.querySelector('.loading-text');
        const progressBar = submitBtn.querySelector('.progress-bar-fill');
        
        if (submitText) submitText.style.display = 'none';
        if (loadingText) loadingText.style.display = 'inline';
        if (progressBar) progressBar.style.display = 'block';
      }
      
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
            allowDownload: true,
            allowEdit: true,
            processoId: data.processo_id || null
          });
          
          Toast.success(data.message || 'PDF gerado com sucesso!');
        } else {
          Toast.error(data.error || 'Erro ao gerar PDF');
        }
      } catch (error) {
        console.error('Error:', error);
        Toast.error('Erro de conexão. Tente novamente.');
      } finally {
        this.isSubmitting = false;
      }
    }
  }));
});