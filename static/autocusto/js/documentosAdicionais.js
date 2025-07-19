(() => {
    const url = $('#div_url_1_vez').attr('data-1-vez-url');
    const relatorio = $('.relatorio');
    const divRelatorio = $('#div-relatorio');
    const cid = $('#id_cid').val();

    $(document).on('change', 'input[name="emitir_relatorio"]', function() {
        let escolha = $('input[name="emitir_relatorio"]:checked').val();
        console.log('Emitir relatório changed:', escolha);
        escolha = escolha == 'True'
        if (escolha) {
            divRelatorio.removeClass('d-none');
        }
        else {
            divRelatorio.addClass('d-none');
            relatorio.val('');
        }
    });

    $(document).on('change', 'input[name="consentimento"]', function() {
        let escolha = $('input[name="consentimento"]:checked').val();
        console.log('Consentimento changed:', escolha);
        escolha = escolha == 'True';
        if (escolha) {
            $.ajax ( {
                url: url,
                data: {'cid': cid},
                datatype: 'json',
                success: function(res) {
                    if (res.relatorio) {
                        divRelatorio.removeClass('d-none');
                        $('input[name="emitir_relatorio"][value="True"]').prop('checked', true);
                        relatorio.val(res.relatorio);
                    }
                }

            }
            );
        }
        else {
            $('input[name="emitir_relatorio"][value="False"]').prop('checked', true);
            divRelatorio.addClass('d-none');
            relatorio.val('');
        }
    });


    


})();
