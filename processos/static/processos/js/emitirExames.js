(() => {
    const campoEmitirExames = $('#id_emitir_exames');
    const listaExames = $('.exames');
    const divExames = $('#div-exames');


    campoEmitirExames.change(() => {
        let escolha = campoEmitirExames.val();
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
