(() => {
    const campoPrimeiraVez = $('#id_consentimento');
    const url = $('#div_url_1_vez').attr('data-1-vez-url');
    const relatorio = $('.relatorio');
    const emitirRelatorio = $('#id_emitir_relatorio');
    const divRelatorio = $('#div-relatorio');
    const cid = $('#id_cid').val();

    emitirRelatorio.change(() => {
        let escolha = emitirRelatorio.val();
        escolha = escolha == 'True'
        if (escolha) {
            divRelatorio.removeClass('d-none');
        }
        else {
            divRelatorio.addClass('d-none');
            relatorio.val('');
        }
    });

    campoPrimeiraVez.change(() => {
        let escolha = campoPrimeiraVez.val();
        escolha = escolha == 'True';
        if (escolha) {
            $.ajax ( {
                url: url,
                data: {'cid': cid},
                datatype: 'json',
                success: function(res) {
                    if (res.relatorio) {
                        divRelatorio.removeClass('d-none');
                        emitirRelatorio.val('True');
                        relatorio.val(res.relatorio);
                    }
                }

            }
            );
        }
        else {
            emitirRelatorio.val('False');
            divRelatorio.addClass('d-none');
            relatorio.val('');
        }
    });


    


})();
