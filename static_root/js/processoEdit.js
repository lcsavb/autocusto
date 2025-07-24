$(document).ready(function() {
      //// Edição completa
    const dadosRepetidos = $('#dados-repetidos');
    
    $(document).on('change', 'input[name="edicao_completa"]', function() {
        dadosRepetidos.toggleClass('d-none');
    });
});