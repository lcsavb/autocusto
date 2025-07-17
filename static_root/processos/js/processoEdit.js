console.log('ProcessoEdit.js file loaded');

$(document).ready(function() {
      //// Edição completa
    const dadosRepetidos = $('#dados-repetidos');
    
    console.log('ProcessoEdit ready, radio buttons found:', $('input[name="edicao_completa"]').length);
    console.log('dados-repetidos div found:', dadosRepetidos.length);
    
    $(document).on('change', 'input[name="edicao_completa"]', function() {
        console.log('Edição completa changed:', this.value);
        dadosRepetidos.toggleClass('d-none');
    });
});