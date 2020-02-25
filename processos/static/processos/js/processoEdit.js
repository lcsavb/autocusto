(() => {
      //// Edição completa
    const edicaoCompleta = $('#id_edicao_completa');
    const dadosRepetidos = $('#dados-repetidos');
    
    edicaoCompleta.change(function() {
        dadosRepetidos.toggleClass('d-none');
});



})();