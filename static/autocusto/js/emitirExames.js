(() => {
    const listaExames = $('.exames');
    const divExames = $('#div-exames');


    $(document).on('change', 'input[name="emitir_exames"]', function() {
        let escolha = $('input[name="emitir_exames"]:checked').val();
        console.log('Emitir exames changed:', escolha);
        escolha = escolha == 'True';
        if (escolha) {
            divExames.removeClass('d-none');
        }
        else {
            divExames.addClass('d-none');
            listaExames.val('');
        }
    });

})();
